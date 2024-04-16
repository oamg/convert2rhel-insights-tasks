import json
import os
import pytest
from mock import patch

from scripts.c2r_script import archive_analysis_report


@pytest.fixture
def create_json_report_mock(tmpdir):
    content = {"test": 1}
    file = tmpdir.join("report.json")
    file.write(json.dumps(content))

    return str(file)


# pylint: disable=redefined-outer-name
def test_archive_old_report(create_json_report_mock, tmpdir):
    tmp_archive_dir = str(tmpdir.join("archive"))
    with patch("scripts.c2r_script.C2R_ARCHIVE_DIR", tmp_archive_dir):
        archive_analysis_report(create_json_report_mock)

    assert len(os.listdir(tmp_archive_dir)) == 1


@patch("scripts.c2r_script.os.path.exists", return_value=True)
@patch("scripts.c2r_script.shutil.move")
def test_archive_old_report_no_dir(mock_dir_exists, mock_move, create_json_report_mock):
    archive_analysis_report(create_json_report_mock)

    mock_dir_exists.assert_called_once()
    mock_move.assert_called_once()
