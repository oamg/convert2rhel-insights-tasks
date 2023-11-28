import os
from mock import patch

from scripts.conversion_script import archive_analysis_report


def test_archive_old_report(create_json_report_mock, tmpdir):
    tmp_archive_dir = str(tmpdir.join("archive"))
    with patch("scripts.conversion_script.C2R_ARCHIVE_DIR", tmp_archive_dir):
        archive_analysis_report(create_json_report_mock)

    assert len(os.listdir(tmp_archive_dir)) == 1
