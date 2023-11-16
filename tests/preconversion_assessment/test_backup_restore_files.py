import pytest
from mock import patch

from scripts.preconversion_assessment_script import (
    RequiredFile,
    ProcessError,
    _create_or_restore_backup_file,
)


@patch("scripts.preconversion_assessment_script.os")
def test_backup_existing_file(mock_os):
    filepath = "/path/to/file"
    required_file = RequiredFile(path=filepath)
    mock_os.path.exists.side_effect = [False, True]

    _create_or_restore_backup_file(required_file)

    mock_os.path.exists.assert_called_with(filepath)
    mock_os.rename.assert_called_once_with(filepath, filepath + ".backup")


@patch("scripts.preconversion_assessment_script.os")
def test_restore_existing_file(mock_os):
    filepath = "/path/to/file"
    required_file = RequiredFile(path=filepath)
    mock_os.path.exists.side_effect = [True]

    _create_or_restore_backup_file(required_file)

    mock_os.path.exists.assert_called_with(filepath + ".backup")
    mock_os.rename.assert_called_once_with(filepath + ".backup", filepath)


@patch("scripts.preconversion_assessment_script.os")
def test_ioerror_restore_or_backup(mock_os):
    filepath = "/path/to/file"
    required_file = RequiredFile(path=filepath)
    mock_os.path.exists.side_effect = IOError

    with pytest.raises(ProcessError):
        _create_or_restore_backup_file(required_file)
