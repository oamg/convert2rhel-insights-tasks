from mock import mock_open, patch

from main import (
    gather_textual_report,
)


@patch('os.path.exists', return_value=True)
def test_gather_textual_report_file_exists(mock_exists):
    test_content = 'Test data'
    with patch("__builtin__.open", mock_open(read_data=test_content)):
        report_data = gather_textual_report()

    assert mock_exists.called_once()
    assert report_data == test_content

def test_gather_textual_report_file_does_not_exists():
    report_data = gather_textual_report()
    assert report_data == ""
