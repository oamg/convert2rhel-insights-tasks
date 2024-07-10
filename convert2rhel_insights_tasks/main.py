import json
import logging
import os
import re
import shutil
import subprocess
import copy
import sys
from time import gmtime, strftime

from urllib2 import urlopen, URLError

# SCRIPT_TYPE is either 'CONVERSION' or 'ANALYSIS'
# Value is set in signed yaml envelope in content_vars (SCRIPT_MODE)
SCRIPT_TYPE = os.getenv("RHC_WORKER_SCRIPT_MODE", "").upper()
IS_CONVERSION = SCRIPT_TYPE == "CONVERSION"
IS_ANALYSIS = SCRIPT_TYPE == "ANALYSIS"

STATUS_CODE = {
    "SUCCESS": 0,
    "INFO": 25,
    "WARNING": 51,
    "SKIP": 101,
    "OVERRIDABLE": 152,
    "ERROR": 202,
}

# Revert the `STATUS_CODE` dictionary to map number: name instead of name:
# number as used originally.
STATUS_CODE_NAME = {number: name for name, number in STATUS_CODE.items()}
# Log folder path for convert2rhel
C2R_LOG_FOLDER = "/var/log/convert2rhel"
# Log file for convert2rhel
C2R_LOG_FILE = "%s/convert2rhel.log" % C2R_LOG_FOLDER
# Path to the convert2rhel pre conversion report json file.
C2R_PRE_REPORT_FILE = "%s/convert2rhel-pre-conversion.json" % C2R_LOG_FOLDER
# Path to the convert2rhel post conversion report json file.
C2R_POST_REPORT_FILE = "%s/convert2rhel-post-conversion.json" % C2R_LOG_FOLDER
# Path to the convert2rhel pre report textual file.
C2R_PRE_REPORT_TXT_FILE = "%s/convert2rhel-pre-conversion.txt" % C2R_LOG_FOLDER
# Path to the convert2rhel post report textual file.
C2R_POST_REPORT_TXT_FILE = "%s/convert2rhel-post-conversion.txt" % C2R_LOG_FOLDER
# Path to the archive folder for convert2rhel.
C2R_ARCHIVE_DIR = "%s/archive" % C2R_LOG_FOLDER
# Set of yum transactions that will be rolled back after the operation is done.
YUM_TRANSACTIONS_TO_UNDO = set()

# Detect the last transaction id in yum.
LATEST_YUM_TRANSACTION_PATTERN = re.compile(r"^(\s+)?(\d+)", re.MULTILINE)

# Path to store the script logs
LOG_DIR = "/var/log/convert2rhel-insights-tasks"
# Log filename for the script. It will be created based on the script type of
# execution.
LOG_FILENAME = "convert2rhel-insights-tasks-%s.log" % (
    "conversion" if IS_CONVERSION else "analysis"
)

# Path to the sos extras folder
SOS_REPORT_FOLDER = "/etc/sos.extras.d"
# Name of the file based on the conversion type for sos report
SOS_REPORT_FILE = "convert2rhel-insights-tasks-%s-logs" % (
    "conversion" if IS_CONVERSION else "analysis"
)

logger = logging.getLogger(__name__)


class RequiredFile(object):
    """Holds data about files needed to download convert2rhel"""

    def __init__(self, path="", host="", keep=False):
        self.path = path
        self.host = host
        self.keep = keep  # conversion specific
        self.backup_suffix = ".backup"

        self.backup_created = False
        self.created = False

    def create_from_host_url_data(self):
        return self._create(urlopen(self.host).read())

    def create_from_data(self, data):
        return self._create(data)

    def _create(self, data):
        try:
            directory = os.path.dirname(self.path)
            if not os.path.exists(directory):
                logger.info("Creating directory at '%s'", directory)
                os.makedirs(directory, mode=0o755)

            logger.info("Writing file to destination: '%s'", self.path)
            with open(self.path, mode="w") as handler:
                handler.write(data)
                os.chmod(self.path, 0o644)

            self.created = True
        except OSError as err:
            logger.warning("Failed to write file to '%s':\n %s", self.path, err)
            return False
        return True

    def delete(self):
        """Deletes the file. Returns True if deleted, otherwise False."""
        if not self.created:
            return False

        try:
            logger.info("Removing the previously downloaded file '%s'", self.path)
            os.remove(self.path)
        except OSError as err:
            logger.warning("Failed to remove '%s':\n %s", self.path, err)
            return False
        return True

    def restore(self):
        """Restores file backup (rename). Returns True if restored, otherwise False."""
        if not self.backup_created:
            return False

        file_path = self.path + self.backup_suffix
        try:
            logger.info("Restoring backed up file %s.", file_path)
            os.rename(file_path, self.path)
            logger.info("File restored (%s).", self.path)
        except OSError as err:
            logger.warning("Failed to restore %s:\n %s", file_path, err)
            return False
        return True

    def backup(self):
        """Creates backup file (rename). Returns True if backed up, otherwise False."""
        if not os.path.exists(self.path):
            logger.info("File %s does not exist, no need to back up.", self.path)
            return False

        try:
            logger.info(
                "Trying to create backup of %s (%s) ...",
                self.path,
                self.backup_suffix,
            )
            full_path = self.path + self.backup_suffix
            os.rename(self.path, full_path)
            logger.info("Back up created (%s).", full_path)
            self.backup_created = True
        except OSError as err:
            logger.warning("Failed to create back up of %s (%s)", self.path, err)
            return False
        return True


class ProcessError(Exception):
    """Custom exception to report errors during setup and run of conver2rhel"""

    def __init__(self, message, report):
        super(ProcessError, self).__init__(report)
        self.message = message
        self.report = report


class OutputCollector(object):
    """Wrapper class for script expected stdout"""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments
    # Eight and five is reasonable in this case.

    def __init__(
        self, status="", message="", report="", entries=None, alert=False, error=False
    ):
        self.status = status
        self.alert = alert  # true if error true or if conversion inhibited
        self.error = error  # true if the script wasn't able to finish, otherwise false
        self.message = message
        self.report = report
        self.tasks_format_version = "1.0"
        self.tasks_format_id = "oamg-format"
        self.entries = entries
        self.report_json = None

    def to_dict(self):
        # If we have entries, then we change report_json to be a dictionary
        # with the needed values, otherwise, we leave it as `None` to be
        # transformed to `null` in json.
        if self.entries:
            self.report_json = {
                "tasks_format_version": self.tasks_format_version,
                "tasks_format_id": self.tasks_format_id,
                "entries": self.entries,
            }

        return {
            "status": self.status,
            "alert": self.alert,
            "error": self.error,
            "message": self.message,
            "report": self.report,
            "report_json": self.report_json,
        }


def setup_sos_report():
    """Setup sos report log collection."""
    if not os.path.exists(SOS_REPORT_FOLDER):
        os.makedirs(SOS_REPORT_FOLDER)

    script_log_file = os.path.join(LOG_DIR, LOG_FILENAME)
    sosreport_link_file = os.path.join(SOS_REPORT_FOLDER, SOS_REPORT_FILE)
    # In case the file for sos report does not exist, lets create one and add
    # the log file path to it.
    if not os.path.exists(sosreport_link_file):
        with open(sosreport_link_file, mode="w") as handler:
            handler.write(":%s\n" % script_log_file)


def setup_logger_handler():
    """
    Setup custom logging levels, handlers, and so on. Call this method from
    your application's main start point.
    """
    # Receive the log level from the worker and try to parse it. If the log
    # level is not compatible with what the logging library expects, set the
    # log level to INFO automatically.
    log_level = os.getenv("RHC_WORKER_LOG_LEVEL", "INFO").upper()
    log_level = logging.getLevelName(log_level)
    if isinstance(log_level, str):
        log_level = logging.INFO

    # enable raising exceptions
    logger.propagate = True
    logger.setLevel(log_level)

    # create sys.stdout handler for info/debug
    stdout_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    stdout_handler.setFormatter(formatter)

    # Create the directory if it don't exist
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    log_filepath = os.path.join(LOG_DIR, LOG_FILENAME)
    file_handler = logging.FileHandler(log_filepath)
    file_handler.setFormatter(formatter)

    # can flush logs to the file that were logged before initializing the file handler
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)


def archive_old_logger_files():
    """
    Archive the old log files to not mess with multiple runs outputs. Every
    time a new run begins, this method will be called to archive the previous
    logs if there is a `convert2rhel.log` file there, it will be archived using
    the same name for the log file, but having an appended timestamp to it.

    For example:
        /var/log/convert2rhel-insights-tasks/archive/convert2rhel-insights-tasks-1635162445070567607.log
        /var/log/convert2rhel-insights-tasks/archive/convert2rhel-insights-tasks-1635162478219820043.log

    This way, the user can track the logs for each run individually based on
    the timestamp.
    """

    current_log_file = os.path.join(LOG_DIR, LOG_FILENAME)
    archive_log_dir = os.path.join(LOG_DIR, "archive")

    # No log file found, that means it's a first run or it was manually deleted
    if not os.path.exists(current_log_file):
        return

    stat = os.stat(current_log_file)

    # Get the last modified time in UTC
    last_modified_at = gmtime(stat.st_mtime)

    # Format time to a human-readable format
    formatted_time = strftime("%Y%m%dT%H%M%SZ", last_modified_at)

    # Create the directory if it don't exist
    if not os.path.exists(archive_log_dir):
        os.makedirs(archive_log_dir)

    file_name, suffix = tuple(LOG_FILENAME.rsplit(".", 1))
    archive_log_file = "%s/%s-%s.%s" % (
        archive_log_dir,
        file_name,
        formatted_time,
        suffix,
    )
    shutil.move(current_log_file, archive_log_file)


def get_rollback_failures(returncode):
    """Returns lines with errors in rollback section of c2r log file, or empty string."""
    rollback_failures = ""

    if returncode != 1 or returncode is None:
        return rollback_failures

    logger.info(
        "Checking content of '%s' for possible rollback problems ...", C2R_LOG_FILE
    )

    start_of_rollback_failures_section = (
        "Following errors were captured during rollback:"
    )
    end_of_rollback_failures_section = "DEBUG - /var/run/lock/convert2rhel.pid"
    try:
        with open(C2R_LOG_FILE, mode="r") as handler:
            # Skip the empty lines and strip white chars from start and end of the string.
            lines = [line.strip() for line in handler.readlines() if line.strip()]

            # Find index of first string in the logs that we care about.
            start_index = lines.index(start_of_rollback_failures_section)

            # Get the end index of the rollback failures section.
            # Find indexes of the "DEBUG - /var/run/lock/convert2rhel.pid" occurrences.
            end_message_occurrences = [
                i for i, s in enumerate(lines) if end_of_rollback_failures_section in s
            ]
            end_index = None
            # Find the first occurence of the end message after the beggining of rollback failures section.
            for occurence_index in end_message_occurrences:
                if occurence_index > start_index:
                    end_index = occurence_index
                    break
            # If the end message wasn't found, use the rest of the log.
            if not end_index:
                end_index = None

            rollback_failures = lines[start_index + 1 : end_index]
    except ValueError:
        logger.info(
            "Failed to find rollback section ('%s') in '%s' file.",
            start_of_rollback_failures_section,
            C2R_LOG_FILE,
        )
    except IOError:
        logger.warning("Failed to read '%s' file.", C2R_LOG_FILE)

    return "\n".join(rollback_failures)


def _check_ini_file_modified():
    rpm_va_output, ini_file_not_modified = run_subprocess(
        ["/usr/bin/rpm", "-Va", "convert2rhel"]
    )

    # No modifications at all
    if not ini_file_not_modified:
        return False

    lines = rpm_va_output.strip().split("\n")
    for line in lines:
        line = line.strip().split()
        status = line[0].replace(".", "").replace("?", "")
        path = line[-1]

        default_ini_modified = path == "/etc/convert2rhel.ini"
        md5_hash_mismatch = "5" in status

        if default_ini_modified and md5_hash_mismatch:
            return True
    return False


def check_convert2rhel_inhibitors_before_run():
    """
    Conditions that must be True in order to run convert2rhel command.
    """
    default_ini_path = "/etc/convert2rhel.ini"
    custom_ini_path = os.path.expanduser("~/.convert2rhel.ini")
    logger.info(
        "Checking that '%s' wasn't modified and '%s' doesn't exist ...",
        default_ini_path,
        custom_ini_path,
    )

    if os.path.exists(custom_ini_path):
        raise ProcessError(
            message="Custom %s was found." % custom_ini_path,
            report=(
                "Remove the %s file by running "
                "'rm -f %s' before running the Task again."
            )
            % (custom_ini_path, custom_ini_path),
        )

    if _check_ini_file_modified():
        raise ProcessError(
            message="According to 'rpm -Va' command %s was modified."
            % default_ini_path,
            report=(
                "Either remove the %s file by running "
                "'rm -f %s' or uninstall convert2rhel by running "
                "'yum remove convert2rhel' before running the Task again."
            )
            % (default_ini_path, default_ini_path),
        )


def get_system_distro_version():
    """Currently we execute the task only for RHEL 7 or 8"""
    logger.info("Checking OS distribution and version ID ...")
    try:
        distribution_id = None
        version_id = None
        with open("/etc/system-release", "r") as system_release_file:
            data = system_release_file.readline()
        match = re.search(r"(.+?)\s?(?:release\s?)", data)
        if match:
            # Split and get the first position, which will contain the system
            # name.
            distribution_id = match.group(1).lower()

        match = re.search(r".+?(\d+)\.(\d+)\D?", data)
        if match:
            version_id = "%s.%s" % (match.group(1), match.group(2))
    except IOError:
        logger.warning("Couldn't read /etc/system-release")

    logger.info(
        "Detected distribution='%s' in version='%s'",
        distribution_id,
        version_id,
    )
    return distribution_id, version_id


def is_eligible_releases(release):
    eligible_releases = "7.9"
    return release == eligible_releases if release else False


def archive_report_file(file):
    """Archive json and textual report from convert2rhel on given filepath"""

    if not os.path.exists(file):
        logger.info("%s does not exist. Skipping archive.", file)
        return

    stat = os.stat(file)
    # Get the last modified time in UTC
    last_modified_at = gmtime(stat.st_mtime)

    # Format time to a human-readable format
    formatted_time = strftime("%Y%m%dT%H%M%SZ", last_modified_at)

    # Create the directory if it don't exist
    if not os.path.exists(C2R_ARCHIVE_DIR):
        os.makedirs(C2R_ARCHIVE_DIR)

    file_name, suffix = tuple(os.path.basename(file).rsplit(".", 1))
    archive_log_file = "%s/%s-%s.%s" % (
        C2R_ARCHIVE_DIR,
        file_name,
        formatted_time,
        suffix,
    )
    shutil.move(file, archive_log_file)


def gather_json_report(report_file):
    """Collect the json report generated by convert2rhel."""
    logger.info("Collecting JSON report.")

    if not os.path.exists(report_file):
        return {}

    try:
        with open(report_file, "r") as handler:
            data = json.load(handler)

            if not data:
                return {}
    except ValueError:
        # In case it is not a valid JSON content.
        return {}

    return data


def gather_textual_report(report_file):
    """
    Collect the textual report generated by convert2rhel.

        .. note::
            We are checking if file exists here as the textual report is not
            that important as the JSON report for the script and for Insights.
            It's fine if the textual report does not exist, but the JSON one is
            required.
    """
    logger.info("Collecting TXT report.")
    data = ""
    if os.path.exists(report_file):
        with open(report_file, mode="r") as handler:
            data = handler.read()
    return data


def generate_report_message(highest_status):
    """Generate a report message based on the status severity."""
    message = ""
    alert = False

    conversion_succes_msg = (
        "No problems found. The system was converted successfully. Please,"
        " reboot your system at your earliest convenience to make sure that"
        " the system is using the RHEL Kernel."
    )

    if STATUS_CODE[highest_status] < STATUS_CODE["WARNING"]:
        message = (
            conversion_succes_msg
            if IS_CONVERSION
            else "No problems found. The system is ready for conversion."
        )

    if STATUS_CODE[highest_status] == STATUS_CODE["WARNING"]:
        message = (
            conversion_succes_msg
            if IS_CONVERSION
            else (
                "The conversion can proceed. "
                "However, there is one or more warnings about issues that might occur after the conversion."
            )
        )

    if STATUS_CODE[highest_status] > STATUS_CODE["WARNING"]:
        message = "The conversion cannot proceed. You must resolve existing issues to perform the conversion."
        alert = True

    return message, alert


def setup_convert2rhel(required_files):
    """Setup convert2rhel tool by downloading the required files."""
    logger.info("Downloading required files.")
    try:
        for required_file in required_files:
            required_file.backup()
            required_file.create_from_host_url_data()
    except URLError as err:
        url = required_file.host
        # pylint: disable=raise-missing-from
        raise ProcessError(
            message="Failed to download required files needed for convert2rhel to run.",
            report="Download of required file from %s failed with error: %s"
            % (url, err),
        )


# Code taken from
# https://github.com/oamg/convert2rhel/blob/v1.4.1/convert2rhel/utils.py#L345
# and modified to adapt the needs of the tools that are being executed in this
# script.
def run_subprocess(cmd, print_cmd=True, env=None):
    """
    Call the passed command and optionally log the called command
    (print_cmd=True) and environment variables in form of dictionary(env=None).
    Switching off printing the command can be useful in case it contains a
    password in plain text.

    The cmd is specified as a list starting with the command and followed by a
    list of arguments. Example: ["/usr/bin/yum", "install", "<package>"]
    """
    # This check is here because we passed in strings in the past and changed
    # to a list for security hardening.  Remove this once everyone is
    # comfortable with using a list instead.
    if isinstance(cmd, str):
        raise TypeError("cmd should be a list, not a str")

    if print_cmd:
        logger.info("Calling command '%s'", " ".join(cmd))

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, env=env
    )
    output = ""
    for line in iter(process.stdout.readline, b""):
        line = line.decode("utf8")
        output += line

    # Call wait() to wait for the process to terminate so that we can
    # get the return code.
    process.wait()

    return output, process.returncode


def _get_last_yum_transaction_id(pkg_name):
    output, return_code = run_subprocess(["/usr/bin/yum", "history", "list", pkg_name])
    if return_code:
        # NOTE: There is only print because list will exit with 1 when no such transaction exist
        logger.warning(
            "Listing yum transaction history for '%s' failed with exit status '%s' and output '%s'"
            "\nThis may cause clean up function to not remove '%s' after Task run.",
            pkg_name,
            return_code,
            output,
            pkg_name,
        )
        return None

    matches = LATEST_YUM_TRANSACTION_PATTERN.findall(output)
    return matches[-1][1] if matches else None


def _check_if_package_installed(pkg_name):
    _, return_code = run_subprocess(["/usr/bin/rpm", "-q", pkg_name])
    return return_code == 0


def install_or_update_convert2rhel(required_files):
    """
    Install the convert2rhel tool to the system.
    Returns True and transaction ID if the c2r pkg was installed, otherwise False, None.
    """
    logger.info("Installing & updating Convert2RHEL package.")

    c2r_pkg_name = "convert2rhel"
    c2r_installed = _check_if_package_installed(c2r_pkg_name)

    if not c2r_installed:
        setup_convert2rhel(required_files)
        output, returncode = run_subprocess(
            ["/usr/bin/yum", "install", c2r_pkg_name, "-y"],
        )
        if returncode:
            raise ProcessError(
                message="Failed to install convert2rhel RPM.",
                report="Installing convert2rhel with yum exited with code '%s' and output:\n%s"
                % (returncode, output.rstrip("\n")),
            )
        transaction_id = _get_last_yum_transaction_id(c2r_pkg_name)
        return True, transaction_id

    output, returncode = run_subprocess(["/usr/bin/yum", "update", c2r_pkg_name, "-y"])
    if returncode:
        raise ProcessError(
            message="Failed to update convert2rhel RPM.",
            report="Updating convert2rhel with yum exited with code '%s' and output:\n%s"
            % (returncode, output.rstrip("\n")),
        )
    # NOTE: If we would like to undo update we could use _get_last_yum_transaction_id(c2r_pkg_name)
    return False, None


def prepare_environment_variables(env):
    """Prepare environment variables to be used in subprocess

    This metod will prepare any environment variables before they are sent down
    to the subprocess that will convert2rhel. Currently, this is meant to be a
    workaround since convert2rhel does not parse the value of the environment
    variables, but only check the presence of them in os.environ.

    With this function, we are make sure that any variables that have the value
    0 are ignored before setting them in the subprocess env context, this will
    prevent convert2rhel to wrongly skipping checks because it was pre-defined
    in the insights playbook.

    :param env: The environment variables before setting them in subprocess.
    :type env: dict[str, Any]
    """
    for variable, value in env.items():
        # We can pop out of context both the OPTIONAL_REPOSITORIES and
        # ELS_DISABLED envs as they are not necessary for convert2rhel
        # execution.
        if variable in ("OPTIONAL_REPOSITORIES", "ELS_DISABLED"):
            env.pop(variable)

        if variable.startswith("CONVERT2RHEL_") and value == "0":
            env.pop(variable)
    return env


def run_convert2rhel(env):
    """
    Run the convert2rhel tool assigning the correct environment variables.

    :param env: Dictionary of possible environment variables to passed down to
        the process.
    :type env: dict[str]
    """
    logger.info("Running Convert2RHEL %s", (SCRIPT_TYPE.title()))

    command = ["/usr/bin/convert2rhel"]
    if IS_ANALYSIS:
        command.append("analyze")

    command.append("-y")

    # This will always be represented as either false/true, since this option
    # comes from the input parameters through Insights UI.
    els_disabled = json.loads(env.pop("ELS_DISABLED", "false").lower())
    if not bool(els_disabled):
        command.append("--els")

    optional_repositories = env.pop("OPTIONAL_REPOSITORIES", None)
    # The `None` value that comes from the playbook gets converted to "None"
    # when we parse it from the environment variable, to not mess with casting
    # and converting, the easiest option is to check against that value for
    # now.
    # TODO(r0x0d): The ideal solution here would be coming with a pre-defined
    # dictionary of values that have the correct values and types. Maybe for
    # the future.
    if optional_repositories and optional_repositories != "None":
        repositories = optional_repositories.split(",")
        repositories = [
            "--enablerepo=%s" % repository.strip() for repository in repositories
        ]
        command.extend(repositories)

    env = prepare_environment_variables(env)
    output, returncode = run_subprocess(command, env=env)
    return output, returncode


def parse_environment_variables():
    """Read the environment variable from os.environ and return them."""
    new_env = {}
    for key, value in os.environ.items():
        valid_prefix = "RHC_WORKER_"
        if key.startswith(valid_prefix):
            # This also removes multiple valid prefixes
            new_env[key.replace(valid_prefix, "")] = value
        else:
            new_env[key] = value
    return new_env


def cleanup(required_files):
    """
    Cleanup the downloaded files downloaded in previous steps in this script.

    If any of the required files was already present on the system, the script
    will not remove that file, as it understand that it is a system file and
    not something that was downloaded by the script.
    """
    logger.info("Cleaning up modifications to the system ...")

    for required_file in required_files:
        if required_file.keep:
            continue
        required_file.delete()
        required_file.restore()

    for transaction_id in YUM_TRANSACTIONS_TO_UNDO:
        output, returncode = run_subprocess(
            ["/usr/bin/yum", "history", "undo", "-y", transaction_id],
        )
        if returncode:
            logger.warning(
                "Undo of yum transaction with ID %s failed with exit status '%s' and output:\n%s",
                transaction_id,
                returncode,
                output,
            )


def _generate_message_key(message, action_id):
    """
    Helper method to generate a key field in the message composed by action_id
    and message_id.
    Returns modified copy of original message.
    """
    new_message = copy.deepcopy(message)

    new_message["key"] = "%s::%s" % (action_id, message["id"])
    del new_message["id"]

    return new_message


def _generate_detail_block(message):
    """
    Helper method to generate the detail key that is composed by the
    remediations and diagnosis fields.
    Returns modified copy of original message.
    """
    new_message = copy.deepcopy(message)
    detail_block = {
        "remediations": [],
        "diagnosis": [],
    }

    remediation_key = "remediations" if "remediations" in new_message else "remediation"
    detail_block["remediations"].append(
        {"context": new_message.pop(remediation_key, "")}
    )
    detail_block["diagnosis"].append({"context": new_message.pop("diagnosis", "")})
    new_message["detail"] = detail_block
    return new_message


def _rename_dictionary_key(message, new_key, old_key):
    """Helper method to rename keys in a flatten dictionary."""
    new_message = copy.deepcopy(message)
    new_message[new_key] = new_message.pop(old_key)
    return new_message


def _filter_message_level(message, level):
    """
    Filter for messages with specific level. If any of the message matches the
    level, return None, otherwise, if it is different from what is expected,
    return the message received to continue with the other transformations.
    """
    if message["level"] != level:
        return message

    return {}


def apply_message_transform(message, action_id):
    """Apply the necessary data transformation to the given messages."""
    if not _filter_message_level(message, level="SUCCESS"):
        return {}

    new_message = _generate_message_key(message, action_id)
    new_message = _rename_dictionary_key(new_message, "severity", "level")
    new_message = _rename_dictionary_key(new_message, "summary", "description")
    new_message = _generate_detail_block(new_message)

    # Appending the `modifiers` key to the message here for now. Once we have
    # this feature in the frontend, we can populate the data with it.
    new_message["modifiers"] = []

    return new_message


def transform_raw_data(raw_data):
    """
    Method that will transform the raw data given and output in the expected
    format.

    The expected format will be a flattened version of both results and
    messages into a single
    """
    new_data = []
    for action_id, result in raw_data["actions"].items():
        # Format the results as a single list
        for message in result["messages"]:
            new_data.append(apply_message_transform(message, action_id))

        new_data.append(apply_message_transform(result["result"], action_id))

    # Filter out None values before returning
    return [data for data in new_data if data]


def update_insights_inventory():
    """
    Call insights-client to update insights inventory.
    """
    logger.info("Updating system status in Red Hat Insights.")
    output, returncode = run_subprocess(cmd=["/usr/bin/insights-client"])

    if returncode:
        raise ProcessError(
            message="Conversion succeeded but update of Insights Inventory by registering the system again failed.",
            report="insights-client execution exited with code '%s' and output:\n%s"
            % (returncode, output.rstrip("\n")),
        )

    logger.info("System registered with insights-client successfully.")


def check_repos_are_valid():
    """Check if the repositories under /etc/yum.repos.d are available.

    :raises ProcessExit: In case any of the repositories defined in that folder
        is not available.
    """
    logger.info("Checking for system repositories accessbility")
    output, return_code = run_subprocess(
        cmd=["/usr/bin/yum", "makecache", "--setopt=*.skip_if_unavailable=False"]
    )

    if return_code != 0:
        # This will always print, and we know it is the last command before it
        # tells us what is wrong.
        match = "yum-config-manager --save"
        output_lines = [line.strip() for line in output.split("\n") if line]

        # Retrieve the index of the match by searching for that substring
        # inside of the output_lines.
        failure_index = [
            index for index, failure in enumerate(output_lines) if match in failure
        ][0]

        # For showing the errors, we actually want the index + 1, as the index
        # itself will be the match, and we don't care about that part.
        failures = output_lines[failure_index + 1 :]
        raise ProcessError(
            message="Failed to verify accessibility of system repositories.",
            report="The following repositories are not accessible: %s.\n\nFor more information, please visit https://access.redhat.com/solutions/7077708."
            % "\n".join(failures),
        )

    logger.info("System repositories are acessible.")


# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
def main():
    """Main entrypoint for the script."""
    output = OutputCollector()
    gpg_key_file = RequiredFile(
        path="/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release",
        host="https://www.redhat.com/security/data/fd431d51.txt",
    )
    c2r_repo = RequiredFile(
        path="/etc/yum.repos.d/convert2rhel.repo",
        host="https://cdn-public.redhat.com/content/public/addon/dist/convert2rhel/server/7/7Server/x86_64/files/repofile.repo",
    )
    required_files = [
        gpg_key_file,
        c2r_repo,
    ]

    convert2rhel_installed = False
    # Flag that indicate if the (pre)conversion was successful or not.
    execution_successful = False
    # String to hold any errors that happened during rollback.
    rollback_errors = ""

    # Switched to True only after setup is called
    do_cleanup = False

    returncode = None

    setup_sos_report()
    archive_old_logger_files()
    setup_logger_handler()

    try:
        # Exit if invalid value for SCRIPT_TYPE
        if SCRIPT_TYPE not in ["CONVERSION", "ANALYSIS"]:
            raise ProcessError(
                message="Allowed values for RHC_WORKER_SCRIPT_MODE are 'CONVERSION' and 'ANALYSIS'.",
                report='Exiting because RHC_WORKER_SCRIPT_MODE="%s"' % SCRIPT_TYPE,
            )

        # Exit if not CentOS 7.9
        dist, version = get_system_distro_version()

        # Just try (pre)conversion if we can't read the dist or version
        # (e.g. /etc/system-release is missing), such state is logged in get_system_distro_version
        check_dist_version(dist, version)

        check_repos_are_valid()

        archive_report_file(C2R_PRE_REPORT_FILE)
        archive_report_file(C2R_POST_REPORT_FILE)
        archive_report_file(C2R_PRE_REPORT_TXT_FILE)
        archive_report_file(C2R_POST_REPORT_TXT_FILE)

        # Setup Convert2RHEL to be executed.
        do_cleanup = True
        convert2rhel_installed, transaction_id = install_or_update_convert2rhel(
            required_files
        )
        if convert2rhel_installed:
            YUM_TRANSACTIONS_TO_UNDO.add(transaction_id)

        check_convert2rhel_inhibitors_before_run()
        new_env = parse_environment_variables()
        stdout, returncode = run_convert2rhel(new_env)
        execution_successful = returncode == 0

        # Returncode other than 0 can happen in three states in analysis mode:
        #  1. In case there is another instance of convert2rhel running
        #  2. In case of KeyboardInterrupt, SystemExit (misplaced by mistaked),
        #     Exception not catched before.
        #  3. There was an error during rollback. This result in return code 1.
        # In any case, we should treat this as separate and give it higher
        # priority. In case the returncode was non zero, we don't care about
        # the rest and we should jump to the exception handling immediatly
        if not execution_successful:
            rollback_errors = get_rollback_failures(returncode)
            # Check if there are any inhibitors in the rollback logging. This is
            # necessary in the case where the analysis was done successfully, but
            # there was an error in the rollback log.
            if rollback_errors:
                raise ProcessError(
                    message=(
                        "A rollback of changes performed by convert2rhel failed. The system is in an undefined state. "
                        "Recover the system from a backup or contact Red Hat support."
                    ),
                    report=(
                        "\nFor details, refer to the convert2rhel log file on the host at "
                        "/var/log/convert2rhel/convert2rhel.log. Relevant lines from log file: \n%s\n"
                    )
                    % rollback_errors,
                )

            step = "pre-conversion analysis" if IS_ANALYSIS else "conversion"
            raise ProcessError(
                message=(
                    "An error occurred during the %s. For details, refer to "
                    "the convert2rhel log file on the host at /var/log/convert2rhel/convert2rhel.log"
                )
                % step,
                report=(
                    "convert2rhel exited with code %s.\n"
                    "Output of the failed command: %s"
                    % (returncode, stdout.rstrip("\n"))
                ),
            )

        # Only call insights to update inventory on successful conversion.
        if IS_CONVERSION:
            update_insights_inventory()

        logger.info(
            "Convert2RHEL %s script finished successfully!", SCRIPT_TYPE.title()
        )
    except ProcessError as exception:
        logger.error(exception.report)
        output = OutputCollector(
            status="ERROR",
            alert=True,
            error=False,
            message=exception.message,
            report=exception.report,
        )
    except Exception as exception:
        logger.critical(str(exception))
        output = OutputCollector(
            status="ERROR",
            alert=True,
            error=False,
            message="An unexpected error occurred. Expand the row for more details.",
            report=str(exception),
        )
    finally:
        # Report file could be either the pre-conversion or post-conversion
        # depending on the SCRIPT_TYPE and conversion status. For example:
        #   - If the SCRIPT_TYPE is analysis, then we will always use pre-conversion report
        #   - If the SCRIPT_TYPE is conversion, we gonna check the following:
        #       - If the conversion was successful, use the post-conversion report
        #       - Otherwise, we probably have the pre-conversion report, so let's use that.
        json_report_file = C2R_PRE_REPORT_FILE
        txt_report_file = C2R_PRE_REPORT_TXT_FILE
        if IS_CONVERSION and not os.path.exists(C2R_PRE_REPORT_FILE):
            json_report_file = C2R_POST_REPORT_FILE
            txt_report_file = C2R_POST_REPORT_TXT_FILE

        # Gather JSON report
        data = gather_json_report(json_report_file)

        if data:
            output.status = data.get("status", None)

            if not rollback_errors:
                # At this point we know JSON report exists and no rollback errors occured
                # we can rewrite previous conversion message with more specific one (or add missing message)
                # and set alert
                output.message, output.alert = generate_report_message(output.status)

            is_successful_conversion = IS_CONVERSION and execution_successful

            if is_successful_conversion:
                gpg_key_file.keep = True

                # NOTE: When c2r statistics on insights are not reliant on rpm being installed
                # remove below line (=decide only based on install_or_update_convert2rhel() result)
                if convert2rhel_installed:
                    YUM_TRANSACTIONS_TO_UNDO.remove(transaction_id)

                # NOTE: Keep always because added/updated pkg is also kept
                # (if repo existed, the .backup file will remain on system)
                c2r_repo.keep = True

            should_attach_entries_and_report = (
                IS_CONVERSION or IS_ANALYSIS
            ) or not is_successful_conversion
            if not output.report and should_attach_entries_and_report:
                # Try to attach the textual report in the report if we have json
                # report, otherwise, we would overwrite the report raised by the
                # exception.
                output.report = gather_textual_report(txt_report_file)

            if not rollback_errors and should_attach_entries_and_report:
                output.entries = transform_raw_data(data)

        if do_cleanup:
            cleanup(required_files)

        print("### JSON START ###")
        print(json.dumps(output.to_dict(), indent=4))
        print("### JSON END ###")


def check_dist_version(dist, version):
    """Check for dist and version. If they don't match, raise an ProcessError and stop the script."""
    if dist and version:
        is_valid_dist = dist.startswith("centos")
        is_valid_version = is_eligible_releases(version)
        if not is_valid_dist or not is_valid_version:
            raise ProcessError(
                message="Conversion is only supported on CentOS 7.9 distributions.",
                report='Exiting because distribution="%s" and version="%s"'
                % (dist.title(), version),
            )


if __name__ == "__main__":
    main()
