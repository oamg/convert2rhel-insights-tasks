import json
import pytest
from mock import mock_open, patch

from convert2rhel_insights_tasks.main import gather_textual_report, gather_json_report


@patch("os.path.exists", return_value=True)
def test_gather_textual_report_file_exists(mock_exists):
    test_content = "Test data"
    with patch("__builtin__.open", mock_open(read_data=test_content)):
        report_data = gather_textual_report("some-file.txt")

    assert mock_exists.called_once()
    assert report_data == test_content


def test_gather_textual_report_file_does_not_exists():
    report_data = gather_textual_report("some-file.txt")
    assert report_data == ""


def test_gather_json_report(tmpdir):
    file = tmpdir.join("report.jsn")
    file.write(json.dumps({"test": "hi"}))
    file = str(file)
    with patch("convert2rhel_insights_tasks.main.C2R_PRE_REPORT_FILE", file):
        report_data = gather_json_report(file, returncode=0)

    assert report_data == {"test": "hi"}


@pytest.mark.parametrize(
    ("content", "expected"),
    (
        (
            r"{}",
            {},
        ),
        ("not serializable", {}),
    ),
)
def test_gather_json_report_bad_content(content, expected, tmpdir):
    file = tmpdir.join("report.json")
    file.write(content)
    file = str(file)
    with patch("convert2rhel_insights_tasks.main.C2R_PRE_REPORT_FILE", file):
        assert gather_json_report(file, returncode=1) == expected


def test_gather_json_report_missing_file():
    with patch("convert2rhel_insights_tasks.main.C2R_PRE_REPORT_FILE", "/missing/file"):
        assert gather_json_report("/missing/file", returncode=0) == {}


def test_gather_json_report_return_code():
    with patch("convert2rhel_insights_tasks.main.C2R_PRE_REPORT_FILE", "/missing/file"):
        assert gather_json_report("/missing/file", returncode=1) == {}
