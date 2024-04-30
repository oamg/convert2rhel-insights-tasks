import os
import logging
from mock import patch
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
        sos_report_folder, "convert2rhel-insights-tasks-analysis-logs"
    )
    assert os.path.exists(sos_report_folder)
    assert os.path.exists(sos_report_file)

    with open(sos_report_file) as handler:
        assert (
            ":/var/log/convert2rhel-insights-tasks/convert2rhel-insights-tasks-analysis.log"
            == handler.read().strip()
        )


@patch("scripts.c2r_script.os.makedirs")
@patch("scripts.c2r_script.os.path.exists", side_effect=[False, True])
def test_setup_sos_report_no_sos_report_folder(
    patch_exists, patch_makedirs, monkeypatch, tmpdir
):
    sos_report_folder = str(tmpdir)
    monkeypatch.setattr(scripts.c2r_script, "SOS_REPORT_FOLDER", sos_report_folder)

    setup_sos_report()

    # Folder created
    assert patch_exists.call_count == 2
    patch_makedirs.assert_called_once_with(sos_report_folder)


def test_setup_logger_handler_incorrect_log_level(monkeypatch, tmpdir):
    """If a invalid logger level is set, we will ignore it and set it to INFO."""
    logger = logging.getLogger(__name__)
    monkeypatch.setenv("RHC_WORKER_LOG_LEVEL", "INVALID_LOG_LEVEL")
    log_dir = str(tmpdir)
    monkeypatch.setattr(scripts.c2r_script, "LOG_DIR", log_dir)
    monkeypatch.setattr(scripts.c2r_script, "LOG_FILENAME", "filelog.log")
    monkeypatch.setattr(scripts.c2r_script, "logger", logger)

    setup_logger_handler()

    assert logger.level == logging.INFO


def test_setup_logger_handler(monkeypatch, tmpdir):
    log_dir = str(tmpdir)
    monkeypatch.setattr(scripts.c2r_script, "LOG_DIR", log_dir)
    monkeypatch.setattr(scripts.c2r_script, "LOG_FILENAME", "filelog.log")

    setup_logger_handler()
    logger = logging.getLogger(__name__)

    # emitting some log entries
    logger.info("Test info: %s", "data")
    logger.debug("Test debug: %s", "other data")

    assert os.path.exists(log_dir)


def test_setup_logger_handler_no_log_dir_folder(monkeypatch, tmpdir):
    log_dir = os.path.join(str(tmpdir), "missing-folder")
    monkeypatch.setattr(scripts.c2r_script, "LOG_DIR", log_dir)
    monkeypatch.setattr(scripts.c2r_script, "LOG_FILENAME", "filelog.log")

    setup_logger_handler()
    logger = logging.getLogger(__name__)

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


def test_archive_old_logger_files_archive_dir_exists(monkeypatch, tmpdir):
    log_dir = str(tmpdir)
    archive_dir = os.path.join(log_dir, "archive")
    os.makedirs(archive_dir)
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
