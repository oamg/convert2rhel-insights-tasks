# pylint: disable=too-many-arguments

from mock import patch, Mock

from scripts.c2r_script import main

@patch("scripts.c2r_script.SCRIPT_TYPE", "CONVERSION")
@patch(
    "scripts.c2r_script.get_system_distro_version", return_value=("centos", "7")
)
@patch("scripts.c2r_script.cleanup")
@patch("scripts.c2r_script.archive_analysis_report", side_effect=Mock())
@patch("scripts.c2r_script.update_insights_inventory", side_effect=Mock())
def test_main_non_eligible_release(
    mock_update_insights_inventory,
    mock_archive_analysis_report,
    mock_cleanup,
    mock_get_system_distro_version,
    capsys,
):
    main()

    output = capsys.readouterr().out
    assert "Conversion is only supported on" in output
    assert '"alert": true' in output

    mock_get_system_distro_version.assert_called_once()
    mock_cleanup.assert_called_once()
    assert mock_archive_analysis_report.call_count == 0
    assert mock_update_insights_inventory.call_count == 0


# fmt: off
@patch("scripts.c2r_script.SCRIPT_TYPE", "CONVERSION")
@patch("scripts.c2r_script.gather_json_report", side_effect=[{"actions": [], "status": "SUCCESS"}])
@patch("scripts.c2r_script.update_insights_inventory", side_effect=Mock())
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.install_convert2rhel", return_value=(True, 1))
@patch("scripts.c2r_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.c2r_script.run_convert2rhel", return_value=("", 0))
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.transform_raw_data", side_effect=Mock(return_value=""))
# These patches are calls made in cleanup
@patch("os.path.exists", return_value=False)
@patch("scripts.c2r_script.run_subprocess", return_value=("", 1))
@patch("scripts.c2r_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.c2r_script.is_eligible_releases", return_value=True)
@patch("scripts.c2r_script.archive_analysis_report", side_effect=Mock())
# fmt: on
# pylint: disable=too-many-locals
def test_main_success_c2r_installed(
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup_pkg_call,
    mock_os_exists,
    mock_transform_raw_data,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_update_insights_inventory,
    mock_gather_json_report,
    capsys,  # to check for rollback info in stdout
):
    main()

    output = capsys.readouterr().out
    assert "No problems found. The system was converted successfully." in output
    assert '"alert": false' in output

    assert mock_archive_analysis_report.call_count == 0
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_update_insights_inventory.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_transform_raw_data.call_count == 0
    # NOTE: we should expect below one call once we don't require rpm because of insights conversion statistics
    assert mock_cleanup_pkg_call.call_count == 0
    # 2x for archive
    assert mock_os_exists.call_count == 2


# fmt: off
@patch("scripts.c2r_script.SCRIPT_TYPE", "CONVERSION")
@patch("scripts.c2r_script.archive_analysis_report", side_effect=Mock())
@patch("scripts.c2r_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.c2r_script.is_eligible_releases", return_value=True)
@patch("scripts.c2r_script.gather_json_report", side_effect=[{"actions": [], "status": "SUCCESS"}])
@patch("scripts.c2r_script.update_insights_inventory", side_effect=Mock())
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.install_convert2rhel", return_value=(False, None))
@patch("scripts.c2r_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.c2r_script.run_convert2rhel", return_value=("", 0))
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.transform_raw_data", side_effect=Mock(return_value=""))
# These patches are calls made in cleanup
@patch("os.path.exists", return_value=False)
@patch("scripts.c2r_script.run_subprocess", return_value=("", 1))
# fmt: on
# pylint: disable=too-many-locals
def test_main_success_c2r_updated(
    mock_cleanup_pkg_call,
    mock_os_exists,
    mock_transform_raw_data,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_update_insights_inventory,
    mock_gather_json_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_archive_analysis_report,
    capsys,  # to check for rollback info in stdout
):
    main()

    output = capsys.readouterr().out
    assert "No problems found. The system was converted successfully." in output
    assert '"alert": false' in output

    assert mock_archive_analysis_report.call_count == 0
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_update_insights_inventory.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_transform_raw_data.call_count == 0
    # NOTE: we should expect below one call once we don't require rpm because of insights conversion statistics
    assert mock_cleanup_pkg_call.call_count == 0
    # 2x for archive
    assert mock_os_exists.call_count == 2


# fmt: off
@patch("scripts.c2r_script.SCRIPT_TYPE", "CONVERSION")
@patch("scripts.c2r_script.gather_json_report", side_effect=[{"actions": [], "status": "ERROR"}])
@patch("scripts.c2r_script.update_insights_inventory", side_effect=Mock())
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.c2r_script.install_convert2rhel", return_value=(True, 1))
@patch("scripts.c2r_script.run_convert2rhel", return_value=("", 1))
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.transform_raw_data", side_effect=Mock(return_value=""))
# These patches are calls made in cleanup
@patch("os.path.exists", return_value=False)
@patch("scripts.c2r_script.run_subprocess", return_value=("", 1))
@patch("scripts.c2r_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.c2r_script.is_eligible_releases", return_value=True)
@patch("scripts.c2r_script.check_for_inhibitors_in_rollback", return_value="")
# fmt: on
# pylint: disable=too-many-locals
def test_main_inhibited_c2r_installed_no_rollback_err(
    mock_rollback_inhibitor_check,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup_pkg_call,
    mock_os_exists,
    mock_transform_raw_data,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_update_insights_inventory,
    mock_gather_json_report,
    capsys,
):
    main()

    output = capsys.readouterr().out
    assert "The conversion cannot proceed" in output
    assert '"alert": true' in output

    mock_rollback_inhibitor_check.assert_called_once()

    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_transform_raw_data.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_cleanup_pkg_call.call_count == 1
    # 2x for archive
    assert mock_os_exists.call_count == 2
    assert mock_update_insights_inventory.call_count == 0


# fmt: off
@patch("scripts.c2r_script.SCRIPT_TYPE", "CONVERSION")
@patch("scripts.c2r_script.gather_json_report", return_value={})
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.install_convert2rhel", return_value=(False, 1))
@patch("scripts.c2r_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.c2r_script.run_convert2rhel", return_value=("", 1))
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.cleanup", side_effect=Mock())
@patch("scripts.c2r_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.c2r_script.is_eligible_releases", return_value=True)
@patch("scripts.c2r_script.archive_analysis_report", side_effect=Mock())
@patch("scripts.c2r_script.update_insights_inventory", side_effect=Mock())
# fmt: on
def test_main_process_error_no_report(
    mock_update_insights_inventory,
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_gather_json_report,
    capsys,
):
    main()

    output = capsys.readouterr().out
    assert "An error occurred during the pre-conversion analysis" in output
    assert '"alert": true' in output

    # Zero because os.path.exists is not mocked and reports do not exist
    assert mock_archive_analysis_report.call_count == 0
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_update_insights_inventory.call_count == 0


# fmt: off
@patch("scripts.c2r_script.SCRIPT_TYPE", "CONVERSION")
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.install_convert2rhel", return_value=(False, 1))
@patch("scripts.c2r_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.c2r_script.run_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value="failed"))
@patch("scripts.c2r_script.generate_report_message", side_effect=Mock(return_value=("", False)))
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
    assert "An unexpected error occurred" in output
    assert '"alert": true' in output

    # Zero because os.path.exists is not mocked and reports do not exist
    assert mock_archive_analysis_report.call_count == 0
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_update_insights_inventory.call_count == 0


# fmt: off
@patch("scripts.c2r_script.SCRIPT_TYPE", "CONVERSION")
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
    mock_os_exists,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    capsys,
):
    main()

    output = capsys.readouterr().out
    assert "/etc/convert2rhel.ini was modified" in output
    assert '"alert": true' in output

    assert mock_archive_analysis_report.call_count == 0
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_custom_ini.call_count == 1
    # 2x for archive check + 1 inside in inhibitor check + 1 gather json
    assert mock_os_exists.call_count == 4
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 0
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_update_insights_inventory.call_count == 0


# fmt: off
@patch("scripts.c2r_script.SCRIPT_TYPE", "CONVERSION")
@patch("scripts.c2r_script.gather_json_report", side_effect=Mock(return_value={}))
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
    mock_os_exists,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_gather_json_report,
    capsys,
):
    main()

    output = capsys.readouterr().out
    assert ".convert2rhel.ini was found" in output
    assert '"alert": true' in output

    assert mock_archive_analysis_report.call_count == 2
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_setup_convert2rhel.call_count == 1
    # Twice for archiving reports + 1 inside inhibitor check
    assert mock_os_exists.call_count == 3
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 0
    assert mock_gather_json_report.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_update_insights_inventory.call_count == 0


# fmt: off
@patch("scripts.c2r_script.SCRIPT_TYPE", "CONVERSION")
@patch("scripts.c2r_script.gather_json_report", side_effect=[{"actions": []}])
@patch("scripts.c2r_script.update_insights_inventory", side_effect=Mock())
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.c2r_script.install_convert2rhel", return_value=(True, 1))
@patch("scripts.c2r_script.run_convert2rhel", return_value=("", 1))
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.generate_report_message", side_effect=Mock(return_value=("inhibited", False)))
@patch("scripts.c2r_script.transform_raw_data", side_effect=Mock(return_value=""))
# These patches are calls made in cleanup
@patch("os.path.exists", return_value=False)
@patch("scripts.c2r_script.run_subprocess", return_value=("", 1))
@patch("scripts.c2r_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.c2r_script.is_eligible_releases", return_value=True)
@patch("scripts.c2r_script.check_for_inhibitors_in_rollback", return_value="rollback error")
# fmt: on
# pylint: disable=too-many-locals
def test_main_inhibited_c2r_installed_rollback_errors(
    mock_rollback_inhibitor_check,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup_pkg_call,
    mock_os_exists,
    mock_transform_raw_data,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_update_insights_inventory,
    mock_gather_json_report,
    capsys,
):
    main()

    output = capsys.readouterr().out
    assert "A rollback of changes performed by convert2rhel failed" in output
    assert '"alert": true' in output

    mock_rollback_inhibitor_check.assert_called_once()
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_inhibitor_check.call_count == 1
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_transform_raw_data.call_count == 0
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup_pkg_call.call_count == 1
    # 2x for archive
    assert mock_os_exists.call_count == 2
    assert mock_update_insights_inventory.call_count == 0
