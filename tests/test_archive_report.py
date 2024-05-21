import json
import os
import pytest
from mock import patch

from convert2rhel_insights_tasks.main import archive_analysis_report


@pytest.fixture
def create_json_report_mock(tmpdir):
    content = {"test": 1}
    file = tmpdir.join("report.json")
    file.write(json.dumps(content))

    return str(file)


# pylint: disable=redefined-outer-name
def test_archive_old_report(create_json_report_mock, tmpdir):
    tmp_archive_dir = str(tmpdir.join("archive"))
    with patch("convert2rhel_insights_tasks.main.C2R_ARCHIVE_DIR", tmp_archive_dir):
        archive_analysis_report(create_json_report_mock)

    assert len(os.listdir(tmp_archive_dir)) == 1


@patch("convert2rhel_insights_tasks.main.os.path.exists", return_value=True)
@patch("convert2rhel_insights_tasks.main.shutil.move")
def test_archive_old_report_no_dir(mock_dir_exists, mock_move, create_json_report_mock):
    archive_analysis_report(create_json_report_mock)

    mock_dir_exists.assert_called_once()
    mock_move.assert_called_once()
