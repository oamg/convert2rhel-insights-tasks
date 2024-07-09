# pylint: disable=too-many-arguments

from mock import patch, mock_open, Mock

from utils import extract_json
from convert2rhel_insights_tasks.main import main


# fmt: off
@patch("convert2rhel_insights_tasks.main.IS_ANALYSIS", True)
@patch("convert2rhel_insights_tasks.main.SCRIPT_TYPE", "ANALYSIS")
@patch("convert2rhel_insights_tasks.main.gather_json_report", side_effect=[{"actions": []}])
@patch("convert2rhel_insights_tasks.main.install_or_update_convert2rhel", return_value=(False, 1))
@patch("convert2rhel_insights_tasks.main.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("convert2rhel_insights_tasks.main.run_convert2rhel", return_value=("", 0))
@patch("convert2rhel_insights_tasks.main.gather_textual_report", side_effect=Mock(return_value=""))
@patch("convert2rhel_insights_tasks.main.generate_report_message", side_effect=Mock(return_value=("successfully", False)))
@patch("convert2rhel_insights_tasks.main.transform_raw_data", side_effect=Mock(return_value=""))
@patch("convert2rhel_insights_tasks.main.cleanup", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.get_system_distro_version", return_value=("centos", "7.9"))
@patch("convert2rhel_insights_tasks.main.is_eligible_releases", return_value=True)
@patch("convert2rhel_insights_tasks.main.archive_report_file", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.get_rollback_failures", return_value="")
@patch("convert2rhel_insights_tasks.main.update_insights_inventory", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.setup_sos_report", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.archive_old_logger_files", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.setup_logger_handler", side_effect=Mock())
# fmt: on
# pylint: disable=too-many-locals
def test_main_success_c2r_installed(
    mock_setup_logger_handler,
    mock_setup_sos_report,
    mock_archive_old_logger_files,
    mock_update_insights_inventory,
    mock_get_rollback_failures,
    mock_archive_report_file,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_transform_raw_data,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_or_update_convert2rhel,
    mock_gather_json_report,
    capsys,  # to check for rollback info in stdout
    caplog,
):
    main()

    output = capsys.readouterr().out
    assert "rollback" not in caplog.text
    assert "Convert2RHEL Analysis script finished successfully!" in caplog.text
    assert '"alert": false' in output
    assert extract_json(output) is not None

    assert mock_setup_logger_handler.call_count == 1
    assert mock_setup_sos_report.call_count == 1
    assert mock_archive_old_logger_files.call_count == 1
    assert mock_get_rollback_failures.call_count == 0
    assert mock_update_insights_inventory.call_count == 0
    assert mock_install_or_update_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_gather_textual_report.call_count == 1
    assert mock_generate_report_message.call_count == 1
    assert mock_cleanup.call_count == 1
    assert mock_transform_raw_data.call_count == 1
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_report_file.call_count == 4
    assert mock_transform_raw_data.call_count == 1


# fmt: off
@patch("convert2rhel_insights_tasks.main.IS_ANALYSIS", True)
@patch("convert2rhel_insights_tasks.main.SCRIPT_TYPE", "ANALYSIS")
@patch("convert2rhel_insights_tasks.main.gather_json_report", side_effect=[{"actions": []}])
@patch("convert2rhel_insights_tasks.main.install_or_update_convert2rhel", return_value=(False, None))
@patch("convert2rhel_insights_tasks.main.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("convert2rhel_insights_tasks.main.run_convert2rhel", return_value=("", 0))
@patch("convert2rhel_insights_tasks.main.gather_textual_report", side_effect=Mock(return_value=""))
@patch("convert2rhel_insights_tasks.main.generate_report_message", side_effect=Mock(return_value=("successfully", False)))
@patch("convert2rhel_insights_tasks.main.transform_raw_data", side_effect=Mock(return_value=""))
@patch("convert2rhel_insights_tasks.main.cleanup", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.get_system_distro_version", return_value=("centos", "7.9"))
@patch("convert2rhel_insights_tasks.main.is_eligible_releases", return_value=True)
@patch("convert2rhel_insights_tasks.main.archive_report_file", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.get_rollback_failures", return_value="")
@patch("convert2rhel_insights_tasks.main.update_insights_inventory", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.setup_sos_report", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.archive_old_logger_files", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.setup_logger_handler", side_effect=Mock())
# fmt: on
# pylint: disable=too-many-locals
def test_main_success_c2r_updated(
    mock_setup_logger_handler,
    mock_setup_sos_report,
    mock_archive_old_logger_files,
    mock_update_insights_inventory,
    mock_get_rollback_failures,
    mock_archive_report_file,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_transform_raw_data,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_or_update_convert2rhel,
    mock_gather_json_report,
    capsys,  # to check for rollback info in stdout
    caplog,
):
    main()

    output = capsys.readouterr().out
    assert "rollback" not in caplog.text
    assert "Convert2RHEL Analysis script finished successfully!" in caplog.text
    assert '"alert": false' in output
    assert extract_json(output) is not None

    assert mock_get_rollback_failures.call_count == 0
    assert mock_setup_logger_handler.call_count == 1
    assert mock_setup_sos_report.call_count == 1
    assert mock_archive_old_logger_files.call_count == 1
    assert mock_update_insights_inventory.call_count == 0
    assert mock_install_or_update_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_gather_textual_report.call_count == 1
    assert mock_generate_report_message.call_count == 1
    assert mock_cleanup.call_count == 1
    assert mock_transform_raw_data.call_count == 1
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_report_file.call_count == 4
    assert mock_transform_raw_data.call_count == 1


# fmt: off
@patch("convert2rhel_insights_tasks.main.IS_ANALYSIS", True)
@patch("convert2rhel_insights_tasks.main.SCRIPT_TYPE", "ANALYSIS")
@patch("__builtin__.open", mock_open(read_data="not json serializable"))
@patch("convert2rhel_insights_tasks.main.install_or_update_convert2rhel", return_value=(True, 1))
@patch("convert2rhel_insights_tasks.main.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("convert2rhel_insights_tasks.main.run_convert2rhel", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.gather_textual_report", side_effect=Mock(return_value=""))
@patch("convert2rhel_insights_tasks.main.generate_report_message", side_effect=Mock(return_value=("failed", False)))
@patch("convert2rhel_insights_tasks.main.cleanup", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.get_system_distro_version", return_value=("centos", "7.9"))
@patch("convert2rhel_insights_tasks.main.is_eligible_releases", return_value=True)
@patch("convert2rhel_insights_tasks.main.archive_report_file", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.update_insights_inventory", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.setup_sos_report", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.archive_old_logger_files", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.setup_logger_handler", side_effect=Mock())
# fmt: on
def test_main_general_exception(
    mock_setup_logger_handler,
    mock_setup_sos_report,
    mock_archive_old_logger_files,
    mock_update_insights_inventory,
    mock_archive_report_file,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_or_update_convert2rhel,
    capsys,
):
    main()

    output = capsys.readouterr().out
    assert "rollback errors" not in output
    assert "'Mock' object is not iterable" in output
    assert '"alert": true' in output
    assert extract_json(output) is not None

    assert mock_setup_logger_handler.call_count == 1
    assert mock_setup_sos_report.call_count == 1
    assert mock_archive_old_logger_files.call_count == 1
    assert mock_update_insights_inventory.call_count == 0
    assert mock_install_or_update_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_report_file.call_count == 4


# fmt: off
@patch("convert2rhel_insights_tasks.main.IS_ANALYSIS", True)
@patch("convert2rhel_insights_tasks.main.SCRIPT_TYPE", "ANALYSIS")
@patch("__builtin__.open", mock_open(read_data="not json serializable"))
@patch("convert2rhel_insights_tasks.main.install_or_update_convert2rhel", return_value=(True, 1))
@patch("os.path.exists", return_value=False)
@patch("convert2rhel_insights_tasks.main._check_ini_file_modified", return_value=True)
@patch("convert2rhel_insights_tasks.main.run_convert2rhel", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.gather_textual_report", side_effect=Mock(return_value=""))
@patch("convert2rhel_insights_tasks.main.generate_report_message", side_effect=Mock(return_value=("", False)))
@patch("convert2rhel_insights_tasks.main.cleanup", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.get_system_distro_version", return_value=("centos", "7.9"))
@patch("convert2rhel_insights_tasks.main.is_eligible_releases", return_value=True)
@patch("convert2rhel_insights_tasks.main.archive_report_file", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.update_insights_inventory", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.setup_sos_report", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.archive_old_logger_files", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.setup_logger_handler", side_effect=Mock())
# fmt: on
# pylint: disable=too-many-locals
def test_main_inhibited_ini_modified(
    mock_setup_logger_handler,
    mock_setup_sos_report,
    mock_archive_old_logger_files,
    mock_update_insights_inventory,
    mock_archive_report_file,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_custom_ini,
    mock_path_exists,
    mock_install_or_update_convert2rhel,
    capsys,
):
    main()

    output = capsys.readouterr().out
    assert "/etc/convert2rhel.ini was modified" in output
    assert '"alert": true' in output
    assert extract_json(output) is not None

    assert mock_setup_logger_handler.call_count == 1
    assert mock_setup_sos_report.call_count == 1
    assert mock_archive_old_logger_files.call_count == 1
    assert mock_update_insights_inventory.call_count == 0
    assert mock_archive_report_file.call_count == 4
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_custom_ini.call_count == 1
    assert mock_path_exists.call_count == 2
    assert mock_install_or_update_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 0
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_archive_report_file.call_count == 4


# fmt: off
@patch("convert2rhel_insights_tasks.main.IS_ANALYSIS", True)
@patch("convert2rhel_insights_tasks.main.SCRIPT_TYPE", "ANALYSIS")
@patch("__builtin__.open", mock_open(read_data="not json serializable"))
@patch("convert2rhel_insights_tasks.main.install_or_update_convert2rhel", return_value=(True, 1))
@patch("os.path.exists", return_value=True)
@patch("convert2rhel_insights_tasks.main.run_convert2rhel", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.gather_textual_report", side_effect=Mock(return_value=""))
@patch("convert2rhel_insights_tasks.main.generate_report_message", side_effect=Mock(return_value=("", False)))
@patch("convert2rhel_insights_tasks.main.cleanup", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.get_system_distro_version", return_value=("centos", "7.9"))
@patch("convert2rhel_insights_tasks.main.is_eligible_releases", return_value=True)
@patch("convert2rhel_insights_tasks.main.archive_report_file", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.update_insights_inventory", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.setup_sos_report", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.archive_old_logger_files", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.setup_logger_handler", side_effect=Mock())
# fmt: on
def test_main_inhibited_custom_ini(
    mock_setup_logger_handler,
    mock_archive_old_logger_files,
    mock_setup_sos_report,
    mock_update_insights_inventory,
    mock_archive_report_file,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_path_exists,
    mock_install_or_update_convert2rhel,
    capsys,
):
    main()

    output = capsys.readouterr().out
    assert ".convert2rhel.ini was found" in output
    assert '"alert": true' in output
    assert extract_json(output) is not None

    assert mock_setup_logger_handler.call_count == 1
    assert mock_setup_sos_report.call_count == 1
    assert mock_archive_old_logger_files.call_count == 1
    assert mock_update_insights_inventory.call_count == 0
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_path_exists.call_count == 2
    assert mock_install_or_update_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 0
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_archive_report_file.call_count == 4


# fmt: off
@patch("convert2rhel_insights_tasks.main.IS_ANALYSIS", True)
@patch("convert2rhel_insights_tasks.main.SCRIPT_TYPE", "ANALYSIS")
@patch("convert2rhel_insights_tasks.main.gather_json_report", side_effect=[{"actions": [], "status": "ERROR"}])
@patch("convert2rhel_insights_tasks.main.install_or_update_convert2rhel", return_value=(False, 1))
@patch("convert2rhel_insights_tasks.main.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("convert2rhel_insights_tasks.main.run_convert2rhel", return_value=("", 1))
@patch("convert2rhel_insights_tasks.main.gather_textual_report", side_effect=Mock(return_value=""))
@patch("convert2rhel_insights_tasks.main.transform_raw_data", side_effect=Mock(return_value=""))
@patch("convert2rhel_insights_tasks.main.cleanup", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.get_system_distro_version", return_value=("centos", "7.9"))
@patch("convert2rhel_insights_tasks.main.is_eligible_releases", return_value=True)
@patch("convert2rhel_insights_tasks.main.archive_report_file", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.get_rollback_failures", return_value="")
@patch("convert2rhel_insights_tasks.main.update_insights_inventory", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.setup_sos_report", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.archive_old_logger_files", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.setup_logger_handler", side_effect=Mock())
# fmt: on
# pylint: disable=too-many-locals
def test_main_inhibited_c2r_installed_no_rollback_err(
    mock_setup_logger_handler,
    mock_setup_sos_report,
    mock_archive_old_logger_files,
    mock_update_insights_inventory,
    mock_get_rollback_failures,
    mock_archive_report_file,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_transform_raw_data,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_or_update_convert2rhel,
    mock_gather_json_report,
    capsys,
):
    main()

    mock_get_rollback_failures.assert_called_once()
    output = capsys.readouterr().out
    assert "The conversion cannot proceed" in output
    assert '"alert": true' in output
    assert extract_json(output) is not None

    assert mock_update_insights_inventory.call_count == 0
    assert mock_install_or_update_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_transform_raw_data.call_count == 1
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_report_file.call_count == 4
    assert mock_setup_logger_handler.call_count == 1
    assert mock_setup_sos_report.call_count == 1
    assert mock_archive_old_logger_files.call_count == 1


# fmt: off
@patch("convert2rhel_insights_tasks.main.IS_ANALYSIS", True)
@patch("convert2rhel_insights_tasks.main.SCRIPT_TYPE", "ANALYSIS")
@patch("convert2rhel_insights_tasks.main.gather_json_report", side_effect=[{"actions": []}])
@patch("convert2rhel_insights_tasks.main.install_or_update_convert2rhel", return_value=(False, 1))
@patch("convert2rhel_insights_tasks.main.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("convert2rhel_insights_tasks.main.run_convert2rhel", return_value=("", 1))
@patch("convert2rhel_insights_tasks.main.gather_textual_report", side_effect=Mock(return_value=""))
@patch("convert2rhel_insights_tasks.main.generate_report_message", side_effect=Mock(return_value=("ERROR", False)))
@patch("convert2rhel_insights_tasks.main.transform_raw_data", side_effect=Mock(return_value=""))
@patch("convert2rhel_insights_tasks.main.cleanup", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.get_system_distro_version", return_value=("centos", "7.9"))
@patch("convert2rhel_insights_tasks.main.is_eligible_releases", return_value=True)
@patch("convert2rhel_insights_tasks.main.archive_report_file", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.get_rollback_failures", return_value="rollback error")
@patch("convert2rhel_insights_tasks.main.update_insights_inventory", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.setup_sos_report", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.archive_old_logger_files", side_effect=Mock())
@patch("convert2rhel_insights_tasks.main.setup_logger_handler", side_effect=Mock())
# fmt: on
# pylint: disable=too-many-locals
def test_main_inhibited_c2r_installed_rollback_errors(
    mock_setup_logger_handler,
    mock_setup_sos_report,
    mock_archive_old_logger_files,
    mock_update_insights_inventory,
    mock_get_rollback_failures,
    mock_archive_report_file,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_transform_raw_data,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_or_update_convert2rhel,
    mock_gather_json_report,
    capsys,
):
    main()

    assert mock_get_rollback_failures.call_count == 1
    output = capsys.readouterr().out
    assert "### JSON START ###" in output
    assert "A rollback of changes performed by convert2rhel failed" in output
    assert '"alert": true' in output
    assert extract_json(output) is not None

    assert mock_setup_logger_handler.call_count == 1
    assert mock_setup_sos_report.call_count == 1
    assert mock_archive_old_logger_files.call_count == 1
    assert mock_update_insights_inventory.call_count == 0
    assert mock_install_or_update_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_transform_raw_data.call_count == 0
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_report_file.call_count == 4
