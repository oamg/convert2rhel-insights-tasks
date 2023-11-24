# pylint: disable=too-many-arguments

from mock import patch, mock_open, Mock, ANY

from scripts.conversion_script import main, ProcessError


# fmt: off
@patch("scripts.conversion_script.gather_json_report", side_effect=[{"actions": []}])
@patch("scripts.conversion_script.update_insights_inventory", side_effect=Mock())
@patch("scripts.conversion_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.conversion_script.install_convert2rhel", return_value=True)
@patch("scripts.conversion_script.run_convert2rhel", side_effect=Mock())
@patch("scripts.conversion_script.find_highest_report_level", side_effect=Mock(return_value=["SUCCESS"]))
@patch("scripts.conversion_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.conversion_script.generate_report_message", side_effect=Mock(return_value=("successfully", False)))
@patch("scripts.conversion_script.transform_raw_data", side_effect=Mock(return_value=""))
@patch("scripts.conversion_script.cleanup", side_effect=Mock())
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
    mock_update_insights_inventory,
    mock_gather_json_report,
):
    main()

    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_update_insights_inventory.call_count == 1
    assert mock_gather_json_report.call_count == 1
    assert mock_find_highest_report_level.call_count == 1
    assert mock_gather_textual_report.call_count == 1
    assert mock_generate_report_message.call_count == 1
    assert mock_cleanup.call_count == 1
    # NOTE: When c2r statistics on insights are not reliant on rpm being installed
    # we should expect True here
    mock_cleanup.assert_called_once_with(ANY, undo_last_yum_transaction=False)
    assert mock_transform_raw_data.call_count == 1


# fmt: off
@patch("__builtin__.open", new_callable=mock_open())
@patch("scripts.conversion_script.gather_json_report", side_effect=[{"actions": []}])
@patch("scripts.conversion_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.conversion_script.install_convert2rhel", return_value=True)
@patch("scripts.conversion_script.run_convert2rhel", side_effect=ProcessError("test", "Process error"))
@patch("scripts.conversion_script.find_highest_report_level", side_effect=Mock(return_value=["SUCCESS"]))
@patch("scripts.conversion_script.gather_textual_report", side_effect=Mock(return_value=""))
@patch("scripts.conversion_script.generate_report_message", side_effect=Mock(return_value=("failed", False)))
@patch("scripts.conversion_script.cleanup", side_effect=Mock())
# fmt: on
def test_main_process_error(
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_find_highest_report_level,
    mock_run_convert2rhel,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
    mock_gather_json_report,
    mock_open_func,
):
    main()

    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_gather_json_report.call_count == 0
    assert mock_find_highest_report_level.call_count == 0
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    mock_cleanup.assert_called_once_with(ANY, undo_last_yum_transaction=True)
    assert mock_open_func.call_count == 0


# fmt: off
@patch("__builtin__.open", mock_open(read_data="not json serializable"))
@patch("scripts.conversion_script.setup_convert2rhel", side_effect=Mock())
@patch("scripts.conversion_script.install_convert2rhel", return_value=True)
@patch("scripts.conversion_script.run_convert2rhel", side_effect=Mock())
@patch("scripts.conversion_script.find_highest_report_level", side_effect=Mock(return_value=["SUCCESS"]))
@patch("scripts.conversion_script.gather_textual_report", side_effect=Mock(return_value="failed"))
@patch("scripts.conversion_script.generate_report_message", side_effect=Mock(return_value=("", False)))
@patch("scripts.conversion_script.cleanup", side_effect=Mock())
# fmt: on
def test_main_general_exception(
    mock_cleanup,
    mock_generate_report_message,
    mock_gather_textual_report,
    mock_find_highest_report_level,
    mock_run_convert2rhel,
    mock_install_convert2rhel,
    mock_setup_convert2rhel,
):
    main()

    assert mock_setup_convert2rhel.call_count == 1
    assert mock_install_convert2rhel.call_count == 1
    assert mock_run_convert2rhel.call_count == 1
    assert mock_find_highest_report_level.call_count == 0
    assert mock_gather_textual_report.call_count == 0
    assert mock_generate_report_message.call_count == 0
    mock_cleanup.assert_called_once_with(ANY, undo_last_yum_transaction=True)

