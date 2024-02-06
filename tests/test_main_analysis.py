# pylint: disable=too-many-arguments

import pytest
from mock import patch, mock_open, Mock

from scripts.c2r_script import main, ProcessError


# fmt: off
@patch("scripts.c2r_script.IS_ANALYSIS", True)
@patch("scripts.c2r_script.SCRIPT_TYPE", "ANALYSIS")
@patch("scripts.c2r_script.gather_json_report", side_effect=[{"actions": []}])
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.install_convert2rhel", return_value=(False, 1))
@patch("scripts.c2r_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.c2r_script.run_convert2rhel", return_value=("", 0))
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.generate_report_message", side_effect=Mock(return_value=("successfully", False)))
@patch("scripts.c2r_script.transform_raw_data", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.cleanup", side_effect=Mock())
@patch("scripts.c2r_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.c2r_script.is_eligible_releases", return_value=True)
@patch("scripts.c2r_script.archive_analysis_report", side_effect=Mock())
@patch("scripts.c2r_script.check_for_inhibitors_in_rollback", return_value="")
@patch("scripts.c2r_script.update_insights_inventory", side_effect=Mock())
# fmt: on
# pylint: disable=too-many-locals
def test_main_success_c2r_installed(
    mock_update_insights_inventory,
    mock_rollback_inhibitor_check,
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_transform_raw_data,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_gather_json_report,
    capsys,  # to check for rollback info in stdout
):
    main()

    output = capsys.readouterr().out
    assert "rollback" not in output
    assert "Convert2RHEL Analysis script finished successfully!" in output
    assert '"alert": false' in output
    assert mock_rollback_inhibitor_check.call_count == 1

    assert mock_update_insights_inventory.call_count == 0
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_gather_textual_report.call_count == 1
    assert mock_generate_report_message.call_count == 1
    assert mock_cleanup.call_count == 1
    assert mock_transform_raw_data.call_count == 1
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_analysis_report.call_count == 0
    assert mock_transform_raw_data.call_count == 1


# fmt: off
@patch("scripts.c2r_script.IS_ANALYSIS", True)
@patch("scripts.c2r_script.SCRIPT_TYPE", "ANALYSIS")
@patch("scripts.c2r_script.gather_json_report", side_effect=[{"actions": []}])
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.install_convert2rhel", return_value=(False, None))
@patch("scripts.c2r_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.c2r_script.run_convert2rhel", return_value=("", 0))
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.generate_report_message", side_effect=Mock(return_value=("successfully", False)))
@patch("scripts.c2r_script.transform_raw_data", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.cleanup", side_effect=Mock())
@patch("scripts.c2r_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.c2r_script.is_eligible_releases", return_value=True)
@patch("scripts.c2r_script.archive_analysis_report", side_effect=Mock())
@patch("scripts.c2r_script.check_for_inhibitors_in_rollback", return_value="")
@patch("scripts.c2r_script.update_insights_inventory", side_effect=Mock())
# fmt: on
# pylint: disable=too-many-locals
def test_main_success_c2r_updated(
    mock_update_insights_inventory,
    mock_rollback_inhibitor_check,
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_transform_raw_data,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_gather_json_report,
    capsys,  # to check for rollback info in stdout
):
    main()

    output = capsys.readouterr().out
    assert "rollback" not in output
    assert "Convert2RHEL Analysis script finished successfully!" in output
    assert '"alert": false' in output
    assert mock_rollback_inhibitor_check.call_count == 1

    assert mock_update_insights_inventory.call_count == 0
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_gather_textual_report.call_count == 1
    assert mock_generate_report_message.call_count == 1
    assert mock_cleanup.call_count == 1
    assert mock_transform_raw_data.call_count == 1
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_analysis_report.call_count == 0
    assert mock_transform_raw_data.call_count == 1


# fmt: off
@patch("scripts.c2r_script.IS_ANALYSIS", True)
@patch("scripts.c2r_script.SCRIPT_TYPE", "ANALYSIS")
@patch("__builtin__.open", new_callable=mock_open())
@patch("scripts.c2r_script.gather_json_report", return_value={})
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.install_convert2rhel", return_value=(True, 1))
@patch("scripts.c2r_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.c2r_script.run_convert2rhel", side_effect=ProcessError("test", "Process error"))
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.generate_report_message", side_effect=Mock(return_value=("failed", False)))
@patch("scripts.c2r_script.cleanup", side_effect=Mock())
@patch("scripts.c2r_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.c2r_script.is_eligible_releases", return_value=True)
@patch("scripts.c2r_script.archive_analysis_report", side_effect=Mock())
@patch("scripts.c2r_script.update_insights_inventory", side_effect=Mock())
# fmt: on
def test_main_process_error(
    mock_update_insights_inventory,
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_gather_json_report,
    mock_open_func,
    capsys,
):
    main()

    output = capsys.readouterr().out
    assert "rollback" not in output
    assert "Process error" in output
    assert '"alert": true' in output

    assert mock_update_insights_inventory.call_count == 0
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_open_func.call_count == 0
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_analysis_report.call_count == 0


# fmt: off
@patch("scripts.c2r_script.IS_ANALYSIS", True)
@patch("scripts.c2r_script.SCRIPT_TYPE", "ANALYSIS")
@patch("__builtin__.open", mock_open(read_data="not json serializable"))
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.install_convert2rhel", return_value=(True, 1))
@patch("scripts.c2r_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.c2r_script.run_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.generate_report_message", side_effect=Mock(return_value=("failed", False)))
@patch("scripts.c2r_script.cleanup", side_effect=Mock())
@patch("scripts.c2r_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.c2r_script.is_eligible_releases", return_value=True)
@patch("scripts.c2r_script.archive_analysis_report", side_effect=Mock())
@patch("scripts.c2r_script.update_insights_inventory", side_effect=Mock())
# fmt: on
def test_main_general_exception(
    mock_update_insights_inventory,
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    capsys,
):
    main()

    output = capsys.readouterr().out
    assert "rollback errors" not in output
    assert "'Mock' object is not iterable" in output
    assert '"alert": true' in output

    assert mock_update_insights_inventory.call_count == 0
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_analysis_report.call_count == 0


# fmt: off
@patch("scripts.c2r_script.IS_ANALYSIS", True)
@patch("scripts.c2r_script.SCRIPT_TYPE", "ANALYSIS")
@patch("__builtin__.open", mock_open(read_data="not json serializable"))
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.install_convert2rhel", return_value=(True, 1))
@patch("os.path.exists", return_value=False)
@patch("scripts.c2r_script._check_ini_file_modified", return_value=True)
@patch("scripts.c2r_script.run_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.generate_report_message", side_effect=Mock(return_value=("", False)))
@patch("scripts.c2r_script.cleanup", side_effect=Mock())
@patch("scripts.c2r_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.c2r_script.is_eligible_releases", return_value=True)
@patch("scripts.c2r_script.archive_analysis_report", side_effect=Mock())
@patch("scripts.c2r_script.update_insights_inventory", side_effect=Mock())
# fmt: on
def test_main_inhibited_ini_modified(
    mock_update_insights_inventory,
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_custom_ini,
    mock_ini_modified,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    capsys,
):
    main()

    output = capsys.readouterr().out
    assert "/etc/convert2rhel.ini was modified" in output
    assert '"alert": true' in output

    assert mock_update_insights_inventory.call_count == 0
    assert mock_archive_analysis_report.call_count == 0
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_custom_ini.call_count == 1
    assert mock_ini_modified.call_count == 4
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 0
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_archive_analysis_report.call_count == 0


# fmt: off
@patch("scripts.c2r_script.IS_ANALYSIS", True)
@patch("scripts.c2r_script.SCRIPT_TYPE", "ANALYSIS")
@patch("__builtin__.open", mock_open(read_data="not json serializable"))
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.install_convert2rhel", return_value=(True, 1))
@patch("os.path.exists", return_value=True)
@patch("scripts.c2r_script.run_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.generate_report_message", side_effect=Mock(return_value=("", False)))
@patch("scripts.c2r_script.cleanup", side_effect=Mock())
@patch("scripts.c2r_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.c2r_script.is_eligible_releases", return_value=True)
@patch("scripts.c2r_script.archive_analysis_report", side_effect=Mock())
@patch("scripts.c2r_script.update_insights_inventory", side_effect=Mock())
# fmt: on
def test_main_inhibited_custom_ini(
    mock_update_insights_inventory,
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    capsys,
):
    main()

    output = capsys.readouterr().out
    assert ".convert2rhel.ini was found" in output
    assert '"alert": true' in output

    assert mock_update_insights_inventory.call_count == 0
    assert mock_archive_analysis_report.call_count == 2
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_inhibitor_check.call_count == 4
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 0
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_archive_analysis_report.call_count == 2


# fmt: off
@patch("scripts.c2r_script.IS_ANALYSIS", True)
@patch("scripts.c2r_script.SCRIPT_TYPE", "ANALYSIS")
@patch("scripts.c2r_script.gather_json_report", side_effect=[{"actions": [], "status": "ERROR"}])
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.install_convert2rhel", return_value=(False, 1))
@patch("scripts.c2r_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.c2r_script.run_convert2rhel", return_value=("", 1))
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.transform_raw_data", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.cleanup", side_effect=Mock())
@patch("scripts.c2r_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.c2r_script.is_eligible_releases", return_value=True)
@patch("scripts.c2r_script.archive_analysis_report", side_effect=Mock())
@patch("scripts.c2r_script.check_for_inhibitors_in_rollback", return_value="")
@patch("scripts.c2r_script.update_insights_inventory", side_effect=Mock())
# fmt: on
# pylint: disable=too-many-locals
def test_main_inhibited_c2r_installed_no_rollback_err(
    mock_update_insights_inventory,
    mock_rollback_inhibitor_check,
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_transform_raw_data,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_gather_json_report,
    capsys,
):
    main()

    mock_rollback_inhibitor_check.assert_called_once()
    output = capsys.readouterr().out
    assert "The conversion cannot proceed" in output
    assert '"alert": true' in output

    assert mock_update_insights_inventory.call_count == 0
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_transform_raw_data.call_count == 1
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_analysis_report.call_count == 0


# fmt: off
@pytest.mark.parametrize(
    ("run_return_code"),
    (
        (0),
        (1),
    ),
)
@patch("scripts.c2r_script.IS_ANALYSIS", True)
@patch("scripts.c2r_script.SCRIPT_TYPE", "ANALYSIS")
@patch("scripts.c2r_script.gather_json_report", side_effect=[{"actions": []}])
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.install_convert2rhel", return_value=(False, 1))
@patch("scripts.c2r_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.generate_report_message", side_effect=Mock(return_value=("ERROR", False)))
@patch("scripts.c2r_script.transform_raw_data", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.cleanup", side_effect=Mock())
@patch("scripts.c2r_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.c2r_script.is_eligible_releases", return_value=True)
@patch("scripts.c2r_script.archive_analysis_report", side_effect=Mock())
@patch("scripts.c2r_script.check_for_inhibitors_in_rollback", return_value="rollback error")
@patch("scripts.c2r_script.update_insights_inventory", side_effect=Mock())
# fmt: on
# pylint: disable=too-many-locals
def test_main_inhibited_c2r_installed_rollback_errors(
    mock_update_insights_inventory,
    mock_rollback_inhibitor_check,
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_transform_raw_data,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_inhibitor_check,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_gather_json_report,
    run_return_code,
    capsys,
):

    with patch(
        "scripts.c2r_script.run_convert2rhel", return_value=("", run_return_code)
    ) as mock_run_convert2rhel:
        main()

    mock_rollback_inhibitor_check.assert_called_once()
    output = capsys.readouterr().out
    assert "### JSON START ###" in output
    assert "A rollback of changes performed by convert2rhel failed" in output
    assert '"alert": true' in output

    assert mock_update_insights_inventory.call_count == 0
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_transform_raw_data.call_count == 0
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_analysis_report.call_count == 0
