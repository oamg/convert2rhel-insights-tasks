import hashlib
import json
import os
import subprocess

try:
    # Python3
    from urllib.request import urlopen
except ImportError:
    # Python 2
    from urllib2 import urlopen


class RequiredFile(object):
    """Holds data about files needed to download convert2rhel"""

    def __init__(self, path="", host=""):
        self.path = path
        self.host = host
        self.sha512_on_system = None
        self.is_file_present = False


class ProcessError(Exception):
    """Custom exception to report errors during setup and run of conver2rhel"""

    def __init__(self, message):
        super(ProcessError, self).__init__(message)
        self.message = message


class OutputCollector(object):
    """Wrapper class for script expected stdout"""

    def __init__(self, status="", message="", report="", report_json=None):
        if report_json is None:
            report_json = {}

        self.status = status
        self.message = message
        self.report = report
        self.report_json = report_json

    def to_dict(self):
        return {
            "status": self.status,
            "message": self.message,
            "report": self.report,
            "report_json": {"entries": self.report_json},
        }


STATUS_CODE = {
    "SUCCESS": 0,
    "INFO": 25,
    "WARNING": 51,
    "SKIP": 101,
    "OVERRIDABLE": 152,
    "ERROR": 202,
}
STATUS_CODE_NAME = {number: name for name, number in STATUS_CODE.items()}
C2R_REPORT_FILE = "/var/log/convert2rhel/convert2rhel-pre-conversion.json"
C2R_REPORT_TXT_FILE = "/var/log/convert2rhel/convert2rhel-pre-conversion.txt"

REQUIRED_FILES = [
    RequiredFile(
        path="/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release",
        host="https://www.redhat.com/security/data/fd431d51.txt",
    ),
    RequiredFile(
        path="/etc/rhsm/ca/redhat-uep.pem",
        host="https://ftp.redhat.com/redhat/convert2rhel/redhat-uep.pem",
    ),
    RequiredFile(
        path="/etc/yum.repos.d/convert2rhel.repo",
        host="https://ftp.redhat.com/redhat/convert2rhel/7/convert2rhel.repo",
    ),
]


def collect_report_level(action_results):
    action_level_combined = []
    # Gather status codes from messages and result. We are not seeking for
    # differences between them as we want all the results, no matter from where
    # they come.
    for value in action_results.values():
        action_level_combined.append(value["result"]["level"])
        for message in value["messages"]:
            action_level_combined.append(message["level"])

    valid_action_levels = [
        level for level in action_level_combined if level in STATUS_CODE
    ]
    valid_action_levels.sort(key=lambda status: STATUS_CODE[status], reverse=True)
    return valid_action_levels


def gather_textual_report():
    data = ""
    if os.path.exists(C2R_REPORT_TXT_FILE):
        with open(C2R_REPORT_TXT_FILE, mode="r") as handler:
            data = handler.read()
    return data


def generate_report_message(highest_status):
    message = ""
    if STATUS_CODE[highest_status] < STATUS_CODE["WARNING"]:
        message = "No problems found. The system is ready for conversion."

    if STATUS_CODE[highest_status] == STATUS_CODE["WARNING"]:
        message = (
            "The conversion can proceed. "
            "However, there is one or more warnings about issues that might occur after the conversion."
        )

    if STATUS_CODE[highest_status] > STATUS_CODE["WARNING"]:
        message = "The conversion cannot proceed. You must resolve existing issues to perform the conversion."

    return message


def setup_convert2rhel(required_files=None):
    if required_files is None:
        required_files = REQUIRED_FILES

    for required_file in required_files:
        response = urlopen(required_file.host)
        data = response.read()
        downloaded_file_sha512 = hashlib.sha512(data)

        if os.path.exists(required_file.path):
            print(
                "File '%s' is already present on the system. Downloading a copy in order to check if they are the same."
                % required_file.path
            )
            if (
                downloaded_file_sha512.hexdigest()
                != required_file.sha512_on_system.hexdigest()
            ):
                raise ProcessError(
                    message="File '%s' present on the system does not match the one downloaded. Stopping the execution."
                    % required_file.path
                )
        else:
            directory = os.path.dirname(required_file.path)
            if not os.path.exists(directory):
                print("Creating directory at '%s'" % directory)
                os.makedirs(directory, mode=0o755)

            print("Writing file to destination: '%s'" % required_file.path)
            with open(required_file.path, mode="w") as handler:
                handler.write(data)
                os.chmod(required_file.path, 0o644)


def install_convert2rhel():
    subprocess.check_output(["yum", "install", "convert2rhel", "-y"])
    subprocess.check_output(["yum", "update", "convert2rhel", "-y"])


def run_convert2rhel():
    env = {"PATH": os.environ["PATH"]}

    if "RHC_WORKER_CONVERT2RHEL_DISABLE_TELEMETRY" in os.environ:
        env["CONVERT2RHEL_DISABLE_TELEMETRY"] = os.environ[
            "RHC_WORKER_CONVERT2RHEL_DISABLE_TELEMETRY"
        ]

    process = subprocess.Popen(
        ["/usr/bin/convert2rhel", "analyze", "--debug"],
        env=env,
        bufsize=1,
    )
    if process.returncode:
        raise ProcessError(
            message="Convert2RHEL exited with code '%s'." % process.returncode
        )


def cleanup(required_files=None):
    if required_files is None:
        required_files = REQUIRED_FILES

    for required_file in required_files:
        if not required_file.is_file_present and os.path.exists(required_file.path):
            print(
                "Removing the file '%s' as it was previously downloaded."
                % required_file.path
            )
            os.remove(required_file.path)
            continue

        print(
            "File '%s' was present on the system before the execution. Skipping the removal."
            % required_file.path
        )


def verify_required_files_are_present(required_files=None):
    if required_files is None:
        required_files = REQUIRED_FILES

    for required_file in required_files:
        # Avoid race conditions
        try:
            with open(required_file.path, mode="r") as handler:
                required_file.sha512_on_system = hashlib.sha512(handler.read())
                required_file.is_file_present = True
        except (IOError, OSError):
            required_file.is_file_present = False


def main():
    output = OutputCollector()
    try:
        print("Verifying if required files are present on the system.")
        verify_required_files_are_present()
        print("Downloading required files.")
        setup_convert2rhel()
        print("Installing & updating Convert2RHEL package.")
        install_convert2rhel()
        print("Running Convert2RHEL Analysis")
        run_convert2rhel()

        with open(C2R_REPORT_FILE, "r") as handler:
            data = json.load(handler)

        output.report_json = data

        print("Collecting status.")
        combined_levels = collect_report_level(action_results=data["action_results"])
        output.status = combined_levels[0]
        # Set the first position of the list as being the final status, that's
        # needed because `collect_report_level` will sort out the list with the
        # highest priority first.

        output.report = gather_textual_report()
        output.message = generate_report_message(combined_levels[0])

        print("Done with the execution!")
    except ProcessError as exception:
        output = OutputCollector(status="ERROR", message=exception.message)
    except Exception as exception:
        output = OutputCollector(status="ERROR", message=str(exception))
    finally:
        print("Cleaning up modifications to the system.")
        cleanup()

        print("### JSON START ###")
        print(json.dumps(output.to_dict()))
        print("### JSON END ###")


if __name__ == "__main__":
    main()
