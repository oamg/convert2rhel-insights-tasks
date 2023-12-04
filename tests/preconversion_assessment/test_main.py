# pylint: disable=too-many-arguments

from mock import patch, mock_open, Mock

from scripts.preconversion_assessment_script import OutputCollector, main, ProcessError


@patch(
    "scripts.preconversion_assessment_script.get_system_distro_version",
    return_value=("centos", "7"),
)
@patch("scripts.preconversion_assessment_script.cleanup")
@patch("scripts.preconversion_assessment_script.OutputCollector")
def test_main_non_eligible_release(
    mock_output_collector,
    mock_cleanup,
    mock_get_system_distro_version,
):
    mock_output_collector.return_value = OutputCollector(entries=["non-empty"])

    main()

    mock_get_system_distro_version.assert_called_once()
    mock_output_collector.assert_called()
    mock_cleanup.assert_called_once()


# fmt: off
@patch("scripts.preconversion_assessment_script.gather_json_report", side_effect=[{"actions": []}])
@patch("scripts.preconversion_assessment_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.install_convert2rhel", return_value=(False, 1))
@patch("scripts.preconversion_assessment_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.preconversion_assessment_script.run_convert2rhel", return_value=("", 0))
@patch("scripts.preconversion_assessment_script.find_highest_report_level", side_effect=Mock(return_value=["SUCCESS"]))
@patch("scripts.preconversion_assessment_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.generate_report_message", side_effect=Mock(return_value=("successfully", False)))
@patch("scripts.preconversion_assessment_script.transform_raw_data", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.cleanup", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.preconversion_assessment_script.is_eligible_releases", return_value=True)
@patch("scripts.preconversion_assessment_script.archive_analysis_report", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.check_for_inhibitors_in_rollback", return_value="")
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
    mock_find_highest_report_level,
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
    assert mock_find_highest_report_level.call_count == 1
    assert mock_gather_textual_report.call_count == 1
    assert mock_generate_report_message.call_count == 1
    assert mock_cleanup.call_count == 1
    assert mock_transform_raw_data.call_count == 1
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_analysis_report.call_count == 0
    assert mock_transform_raw_data.call_count == 1


# fmt: off
@patch("__builtin__.open", new_callable=mock_open())
@patch("scripts.preconversion_assessment_script.gather_json_report", side_effect=None)
@patch("scripts.preconversion_assessment_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.install_convert2rhel", return_value=(True, 1))
@patch("scripts.preconversion_assessment_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.preconversion_assessment_script.run_convert2rhel", side_effect=ProcessError("test", "Process error"))
@patch("scripts.preconversion_assessment_script.find_highest_report_level", side_effect=Mock(return_value=["SUCCESS"]))
@patch("scripts.preconversion_assessment_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.generate_report_message", side_effect=Mock(return_value=("failed", False)))
@patch("scripts.preconversion_assessment_script.cleanup", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.preconversion_assessment_script.is_eligible_releases", return_value=True)
@patch("scripts.preconversion_assessment_script.archive_analysis_report", side_effect=Mock())
# fmt: on
def test_main_process_error(
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_find_highest_report_level,
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
    assert mock_find_highest_report_level.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_open_func.call_count == 0
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_analysis_report.call_count == 0


# fmt: off
@patch("__builtin__.open", mock_open(read_data="not json serializable"))
@patch("scripts.preconversion_assessment_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.install_convert2rhel", return_value=(True, 1))
@patch("scripts.preconversion_assessment_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.preconversion_assessment_script.run_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.find_highest_report_level", side_effect=Mock(return_value=["SUCCESS"]))
@patch("scripts.preconversion_assessment_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.generate_report_message", side_effect=Mock(return_value=("failed", False)))
@patch("scripts.preconversion_assessment_script.cleanup", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.preconversion_assessment_script.is_eligible_releases", return_value=True)
@patch("scripts.preconversion_assessment_script.archive_analysis_report", side_effect=Mock())
# fmt: on
def test_main_general_exception(
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_find_highest_report_level,
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
    assert mock_find_highest_report_level.call_count == 0
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_analysis_report.call_count == 0


# fmt: off
@patch("__builtin__.open", mock_open(read_data="not json serializable"))
@patch("scripts.preconversion_assessment_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.install_convert2rhel", side_effect=Mock())
@patch("os.path.exists", return_value=False)
@patch("scripts.preconversion_assessment_script._check_ini_file_modified", return_value=True)
@patch("scripts.preconversion_assessment_script.run_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.find_highest_report_level", side_effect=Mock(return_value=["SUCCESS"]))
@patch("scripts.preconversion_assessment_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.generate_report_message", side_effect=Mock(return_value=("", False)))
@patch("scripts.preconversion_assessment_script.cleanup", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.preconversion_assessment_script.is_eligible_releases", return_value=True)
@patch("scripts.preconversion_assessment_script.archive_analysis_report", side_effect=Mock())
# fmt: on
def test_main_inhibited_ini_modified(
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_find_highest_report_level,
    mock_run_convert2rhel,
    mock_custom_ini,
    mock_ini_modified,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
):
    main()

    assert mock_setup_convert2rhel.call_count == 1
    assert mock_custom_ini.call_count == 1
    assert mock_ini_modified.call_count == 4
    assert mock_install_convert2rhel.call_count == 0
    assert mock_run_convert2rhel.call_count == 0
    assert mock_find_highest_report_level.call_count == 0
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_analysis_report.call_count == 0


# fmt: off
@patch("__builtin__.open", mock_open(read_data="not json serializable"))
@patch("scripts.preconversion_assessment_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.install_convert2rhel", side_effect=Mock())
@patch("os.path.exists", return_value=True)
@patch("scripts.preconversion_assessment_script.run_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.find_highest_report_level", side_effect=Mock(return_value=["SUCCESS"]))
@patch("scripts.preconversion_assessment_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.generate_report_message", side_effect=Mock(return_value=("", False)))
@patch("scripts.preconversion_assessment_script.cleanup", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.preconversion_assessment_script.is_eligible_releases", return_value=True)
@patch("scripts.preconversion_assessment_script.archive_analysis_report", side_effect=Mock())
# fmt: on
def test_main_inhibited_custom_ini(
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_find_highest_report_level,
    mock_run_convert2rhel,
    mock_inhibitor_check,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
):
    main()

    assert mock_setup_convert2rhel.call_count == 1
    assert mock_inhibitor_check.call_count == 4
    assert mock_install_convert2rhel.call_count == 0
    assert mock_run_convert2rhel.call_count == 0
    assert mock_find_highest_report_level.call_count == 0
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_analysis_report.call_count == 2


# fmt: off
@patch("scripts.preconversion_assessment_script.gather_json_report", side_effect=[{"actions": []}])
@patch("scripts.preconversion_assessment_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.install_convert2rhel", return_value=(False, 1))
@patch("scripts.preconversion_assessment_script.check_convert2rhel_inhibitors_before_run", return_value=("", 0))
@patch("scripts.preconversion_assessment_script.run_convert2rhel", return_value=("", 1))
@patch("scripts.preconversion_assessment_script.find_highest_report_level", side_effect=Mock(return_value=["SUCCESS"]))
@patch("scripts.preconversion_assessment_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.generate_report_message", side_effect=Mock(return_value=("successfully", False)))
@patch("scripts.preconversion_assessment_script.transform_raw_data", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.cleanup", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.get_system_distro_version", return_value=("centos", "7.9"))
@patch("scripts.preconversion_assessment_script.is_eligible_releases", return_value=True)
@patch("scripts.preconversion_assessment_script.archive_analysis_report", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.check_for_inhibitors_in_rollback", return_value="rollback error")
# fmt: on
# pylint: disable=too-many-locals
def test_main_inhibited_c2r_installed(
    mock_rollback_inhibitor_check,
    mock_archive_analysis_report,
    mock_is_eligible_releases,
    mock_get_system_distro_version,
    mock_cleanup,
    mock_transform_raw_data,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_find_highest_report_level,
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
    assert mock_find_highest_report_level.call_count == 1
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_transform_raw_data.call_count == 0
    assert mock_get_system_distro_version.call_count == 1
    assert mock_is_eligible_releases.call_count == 1
    assert mock_archive_analysis_report.call_count == 0
