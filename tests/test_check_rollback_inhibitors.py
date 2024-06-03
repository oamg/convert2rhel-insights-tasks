import pytest
from mock import patch, mock_open


from convert2rhel_insights_tasks.main import get_rollback_failures


@patch(
    "__builtin__.open",
    new_callable=mock_open,
    read_data="\n".join(
        [
            "Some lines before the warning",
            "CRITICAL - Rollback of system wasn't completed successfully.",
            "The system is left in an undetermined state that Convert2RHEL cannot fix.",
            "It is strongly recommended to store the Convert2RHEL logs for later investigation, and restore the system from a backup.",
            "Following errors were captured during rollback:",
            "Error message 1",
            "Error message 2",
            "[202X-YY-ZZT13:00:00+0000] DEBUG - /var/run/lock/convert2rhel.pid PID 42 unlocked.",
            "Some lines after the report",
        ]
    ),
)
def test_rollback_with_errors(mock_open_fn):
    """Test when there are errors."""
    result = get_rollback_failures(returncode=1)
    mock_open_fn.assert_called_once()
    assert result == "Error message 1\nError message 2"


@patch(
    "__builtin__.open",
    new_callable=mock_open,
    read_data="\n".join(
        [
            "Some lines before the warning",
            "CRITICAL - Rollback of system wasn't completed successfully.",
            "The system is left in an undetermined state that Convert2RHEL cannot fix.",
            "It is strongly recommended to store the Convert2RHEL logs for later investigation, and restore the system from a backup.",
            "Following errors were captured during rollback:",
            "Error message 1",
            "Error message 2",
        ]
    ),
)
def test_rollback_with_errors_no_end(mock_open_fn):
    """Test when there are errors without lines after failures."""
    result = get_rollback_failures(returncode=1)
    mock_open_fn.assert_called_once()
    assert result == "Error message 1\nError message 2"


@patch(
    "__builtin__.open",
    new_callable=mock_open,
    read_data="\n".join(
        [
            "Some lines before the warning",
            "Following errors were captured during rollback:",
            "[202X-YY-ZZT13:00:00+0000] DEBUG - /var/run/lock/convert2rhel.pid PID 42 unlocked.",
            "Pre-conversion analysis report",
            "Some lines after the report",
        ]
    ),
)
def test_rollback_empty_output(mock_open_fn):
    """Test cases when there are any errors provided in the failures part."""
    result = get_rollback_failures(returncode=1)
    mock_open_fn.assert_called_once()
    assert result == ""


@pytest.mark.parametrize(("return_code"), (0, 1, None))
@patch(
    "__builtin__.open",
    new_callable=mock_open,
    read_data="".join(
        [
            "No warning or report",
            "No errors here",
        ]
    ),
)
def test_rollback_c2r_return_code(mock_open_fn, return_code):
    """Test of c2r return codes. When 0, there are any errors."""
    result = get_rollback_failures(returncode=return_code)

    call_count = 0 if return_code is None else return_code

    assert mock_open_fn.call_count == call_count
    assert result == ""


@patch("__builtin__.open", side_effect=IOError("File not found"))
def test_io_error(mock_open_fn):
    result = get_rollback_failures(returncode=1)
    mock_open_fn.assert_called_once()
    assert result == ""
