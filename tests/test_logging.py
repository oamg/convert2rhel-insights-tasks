import os
import logging
import pytest
import scripts

from scripts.c2r_script import (
    setup_sos_report,
    setup_logger_handler,
    archive_old_logger_files,
)


def test_setup_sos_report(monkeypatch, tmpdir):
    sos_report_folder = str(tmpdir)
    monkeypatch.setattr(scripts.c2r_script, "SOS_REPORT_FOLDER", sos_report_folder)

    setup_sos_report()

    sos_report_file = os.path.join(
        sos_report_folder, "convert2rhel-worker-scripts-analysis-logs"
    )
    assert os.path.exists(sos_report_folder)
    assert os.path.exists(sos_report_file)

    with open(sos_report_file) as handler:
        assert (
            ":/var/log/convert2rhel-worker-scripts/convert2rhel-worker-script-analysis.log"
            == handler.read().strip()
        )


@pytest.mark.noautofixtures
def test_setup_logger_handler(monkeypatch, tmpdir):
    log_dir = str(tmpdir)
    monkeypatch.setattr(scripts.c2r_script, "LOG_DIR", log_dir)
    monkeypatch.setattr(scripts.c2r_script, "LOG_FILENAME", "filelog.log")

    logger = logging.getLogger(__name__)
    setup_logger_handler()

    # emitting some log entries
    logger.info("Test info: %s", "data")
    logger.debug("Test debug: %s", "other data")

    assert os.path.exists(log_dir)


def test_archive_old_logger_files(monkeypatch, tmpdir):
    log_dir = str(tmpdir)
    archive_dir = os.path.join(log_dir, "archive")
    monkeypatch.setattr(scripts.c2r_script, "LOG_DIR", log_dir)
    monkeypatch.setattr(scripts.c2r_script, "LOG_FILENAME", "test.log")

    original_log_file = tmpdir.join("test.log")
    original_log_file.write("test")

    archive_old_logger_files()

    assert os.path.exists(log_dir)
    assert os.path.exists(archive_dir)
    assert len(os.listdir(archive_dir)) == 1


def test_archive_old_logger_files_no_log_file(monkeypatch, tmpdir):
    log_dir = str(tmpdir.join("something-else"))
    monkeypatch.setattr(scripts.c2r_script, "LOG_DIR", log_dir)
    monkeypatch.setattr(scripts.c2r_script, "LOG_FILENAME", "test.log")

    archive_old_logger_files()

    assert not os.path.exists(log_dir)
