# pylint: disable=too-many-arguments

from mock import patch, mock_open, Mock

from scripts.preconversion_assessment_script import main, ProcessError


# fmt: off
@patch("scripts.preconversion_assessment_script.gather_json_report", side_effect=[{"actions": []}])
@patch("scripts.preconversion_assessment_script.verify_required_files_are_present", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.install_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.run_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.find_highest_report_level", side_effect=Mock(return_value=["SUCCESS"]))
@patch("scripts.preconversion_assessment_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.generate_report_message", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.transform_raw_data", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.cleanup", side_effect=Mock())
# fmt: on
def test_main_success(
    mock_cleanup,
    mock_transform_raw_data,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_find_highest_report_level,
    mock_run_convert2rhel,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_verify_required_files_are_present,
    mock_gather_json_report,
):
    main()

    assert mock_verify_required_files_are_present.call_count == 1
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_find_highest_report_level.call_count == 1
    assert mock_gather_textual_report.call_count == 1
    assert mock_generate_report_message.call_count == 1
    assert mock_cleanup.call_count == 1
    assert mock_transform_raw_data.call_count == 1


# fmt: off
@patch("__builtin__.open", new_callable=mock_open())
@patch("scripts.preconversion_assessment_script.gather_json_report", side_effect=[{"actions": []}])
@patch("scripts.preconversion_assessment_script.verify_required_files_are_present", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.install_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.run_convert2rhel", side_effect=ProcessError("Process error"))
@patch("scripts.preconversion_assessment_script.find_highest_report_level", side_effect=Mock(return_value=["SUCCESS"]))
@patch("scripts.preconversion_assessment_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.generate_report_message", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.cleanup", side_effect=Mock())
# fmt: on
def test_main_process_error(
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_find_highest_report_level,
    mock_run_convert2rhel,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_verify_required_files_are_present,
    mock_gather_json_report,
    mock_open_func,
):
    main()

    assert mock_verify_required_files_are_present.call_count == 1
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 0
    assert mock_find_highest_report_level.call_count == 0
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
    assert mock_open_func.call_count == 0


# fmt: off
@patch("__builtin__.open", mock_open(read_data="not json serializable"))
@patch("scripts.preconversion_assessment_script.verify_required_files_are_present", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.install_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.run_convert2rhel", side_effect=Mock())
@patch("scripts.preconversion_assessment_script.find_highest_report_level", side_effect=Mock(return_value=["SUCCESS"]))
@patch("scripts.preconversion_assessment_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.generate_report_message", side_effect=Mock(return_value=""))
@patch("scripts.preconversion_assessment_script.cleanup", side_effect=Mock())
# fmt: on
def test_main_general_exception(
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_find_highest_report_level,
    mock_run_convert2rhel,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_verify_required_files_are_present,
):
    main()

    assert mock_verify_required_files_are_present.call_count == 1
    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_find_highest_report_level.call_count == 0
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    assert mock_cleanup.call_count == 1
