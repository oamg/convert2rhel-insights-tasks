from mock import patch, mock_open


from scripts.conversion_script import (
    check_for_inhibitors_in_rollback
)

@patch("__builtin__.open", new_callable=mock_open, read_data="\n".join([
    "Some lines before the warning",
    "WARNING - Abnormal exit! Performing rollback ...",
    "Error message 1",
    "Error message 2",
    "Pre-conversion analysis report",
    "Some lines after the report",
]))
def test_rollback_with_errors(mock_open_fn):
    result = check_for_inhibitors_in_rollback()
    mock_open_fn.assert_called_once()
    assert result == "Error message 1\nError message 2"

@patch("__builtin__.open", new_callable=mock_open, read_data="".join([
    "No warning or report",
    "No errors here",
]))
def test_no_rollback_section_value_error(mock_open_fn):
    result = check_for_inhibitors_in_rollback()
    mock_open_fn.assert_called_once()
    assert result == ""

@patch("__builtin__.open", side_effect=IOError("File not found"))
def test_io_error(mock_open_fn):
    result = check_for_inhibitors_in_rollback()
    mock_open_fn.assert_called_once()
    assert result == ""
