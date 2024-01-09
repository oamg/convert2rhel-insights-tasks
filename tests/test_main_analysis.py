# pylint: disable=too-many-arguments

from mock import patch, mock_open, Mock

from scripts.c2r_script import OutputCollector, main, ProcessError


@patch("scripts.c2r_script.IS_ANALYSIS", True)
@patch("scripts.c2r_script.SCRIPT_TYPE", "ANALYSIS")
@patch(
    "scripts.c2r_script.get_system_distro_version",
    return_value=("centos", "7"),
)
@patch("scripts.c2r_script.cleanup")
@patch("scripts.c2r_script.OutputCollector")
def test_main_non_eligible_release(
    mock_output_collector,
    mock_cleanup,
    mock_get_system_distro_version,
):
    mock_output_collector.return_value = OutputCollector(entries=["non-empty"])

    main()

    mock_get_system_distro_version.assert_called_once()
    mock_output_collector.assert_called()
    mock_cleanup.assert_not_called()


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
# fmt: on
# pylint: disable=too-many-locals
def test_main_success_c2r_installed(
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

    captured = capsys.readouterr()
    assert "rollback" not in captured.out
    assert mock_rollback_inhibitor_check.call_count == 1

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
# fmt: on
def test_main_process_error(
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
):
    main()

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
# fmt: on
def test_main_general_exception(
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
):
    main()

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
# fmt: on
def test_main_inhibited_ini_modified(
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
):
    main()

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
# fmt: on
def test_main_inhibited_custom_ini(
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
):
    main()

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
@patch("scripts.c2r_script.gather_json_report", side_effect=[{"actions": []}])
@patch("scripts.c2r_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.c2r_script.install_convert2rhel", return_value=(False, 1))
@patch("scripts.c2r_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.c2r_script.run_convert2rhel", return_value=("", 1))
@patch("scripts.c2r_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.generate_report_message", side_effect=Mock(return_value=("successfully", False)))
@patch("scripts.c2r_script.transform_raw_data", side_effect=Mock(return_value=""))
@patch("scripts.c2r_script.cleanup", side_effect=Mock())
@patch("scripts.c2r_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.c2r_script.is_eligible_releases", return_value=True)
@patch("scripts.c2r_script.archive_analysis_report", side_effect=Mock())
@patch("scripts.c2r_script.check_for_inhibitors_in_rollback", return_value="rollback error")
# fmt: on
# pylint: disable=too-many-locals
def test_main_inhibited_c2r_installed_rollback_errors(
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
):
    main()
    mock_rollback_inhibitor_check.assert_called_once()

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
