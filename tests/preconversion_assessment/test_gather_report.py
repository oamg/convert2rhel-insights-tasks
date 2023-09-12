import pytest

from mock import mock_open, patch

from scripts.preconversion_assessment_script import (
    gather_textual_report,
    gather_json_report,
    ProcessError,
)


@patch("os.path.exists", return_value=True)
def test_gather_textual_report_file_exists(mock_exists):
    test_content = "Test data"
    with patch("__builtin__.open", mock_open(read_data=test_content)):
        report_data = gather_textual_report()

    assert mock_exists.called_once()
    assert report_data == test_content


def test_gather_textual_report_file_does_not_exists():
    report_data = gather_textual_report()
    assert report_data == ""


def test_gather_json_report():
    test_content = '{"test": "hi"}'
    with patch("__builtin__.open", mock_open(read_data=test_content)):
        report_data = gather_json_report()

    assert report_data == {"test": "hi"}


def test_gather_json_report_no_content(tmpdir):
    file = tmpdir.join("report.json")
    file.write(r"{}")
    file = str(file)
    with patch("scripts.preconversion_assessment_script.C2R_REPORT_FILE", file):
        with pytest.raises(
            ProcessError,
            match="The file '%s' doesn't contain any JSON data in it." % file,
        ):
            gather_json_report()
