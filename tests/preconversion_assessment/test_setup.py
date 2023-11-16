from mock import Mock, patch

from scripts.preconversion_assessment_script import (
    RequiredFile,
    setup_convert2rhel,
)


class MockResponse(object):
    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data


@patch(
    "scripts.preconversion_assessment_script.urlopen",
    return_value=MockResponse("exist_not_match"),
)
@patch("os.path.exists", return_value=True)
@patch("os.makedirs", side_effect=Mock())
@patch("scripts.preconversion_assessment_script._create_or_restore_backup_file")
@patch("__builtin__.open")
@patch("os.chmod")
def test_setup_convert2rhel_file_exist_backup_called(
    mock_chmod, mock_open_fn, mock_backup, mock_makedirs, mock_exist, mock_urlopen
):
    test_file = RequiredFile("/mock/path/file.txt", "exist_not_match")
    required_files = [test_file]

    setup_convert2rhel(required_files)

    assert mock_backup.call_count == 1
    assert mock_exist.call_count == 1
    assert mock_urlopen.call_count == 1
    assert mock_makedirs.call_count == 0
    assert mock_open_fn.call_count == 1
    assert mock_chmod.call_count == 1


@patch(
    "scripts.preconversion_assessment_script.urlopen",
    return_value=MockResponse("exist_not_match"),
)
@patch("os.path.exists", return_value=False)
@patch("os.makedirs", side_effect=Mock())
@patch("scripts.preconversion_assessment_script._create_or_restore_backup_file")
@patch("__builtin__.open")
@patch("os.chmod")
def test_setup_convert2rhel_file_does_not_exists_backup_called(
    mock_chmod, mock_open_fn, mock_backup, mock_makedirs, mock_exist, mock_urlopen
):
    test_file = RequiredFile("/mock/path/file.txt", "exist_not_match")
    required_files = [test_file]

    setup_convert2rhel(required_files)

    assert mock_backup.call_count == 1
    assert mock_exist.call_count == 1
    assert mock_urlopen.call_count == 1
    assert mock_makedirs.call_count == 1
    assert mock_open_fn.call_count == 1
    assert mock_chmod.call_count == 1
