import hashlib
import pytest
from mock import Mock, mock_open, patch

from scripts.conversion_script import (
    ProcessError,
    RequiredFile,
    setup_convert2rhel,
)


class MockResponse(object):
    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data


@patch(
    "scripts.conversion_script.urlopen",
    return_value=MockResponse("exist_not_match"),
)
@patch("os.path.exists", return_value=True)
@patch("os.makedirs", side_effect=Mock())
@patch("__builtin__.open", side_effect=mock_open)
def test_setup_convert2rhel_file_exist_not_match(
    mock_open_fn, mock_makedirs, mock_exist, mock_urlopen
):
    test_file = RequiredFile("/mock/path/file.txt", "exist_not_match")
    test_file.sha512_on_system = hashlib.sha512(b"foo")
    required_files = [test_file]

    with pytest.raises(ProcessError):
        setup_convert2rhel(required_files)

    assert mock_exist.call_count == 1
    assert mock_urlopen.call_count == 1
    assert mock_makedirs.call_count == 0
    assert mock_open_fn.call_count == 0


@patch(
    "scripts.conversion_script.urlopen",
    return_value=MockResponse("exist_match"),
)
@patch("os.path.exists", return_value=True)
@patch("os.makedirs", side_effect=Mock())
@patch("__builtin__.open", side_effect=mock_open)
def test_setup_convert2rhel_file_exist_match(
    mock_open_fn, mock_makedirs, mock_exist, mock_urlopen
):
    test_file = RequiredFile("/mock/path/file.txt", "exist_match")
    test_file.sha512_on_system = hashlib.sha512(b"exist_match")
    required_files = [test_file]

    setup_convert2rhel(required_files)

    assert mock_exist.call_count == 1
    assert mock_urlopen.call_count == 1
    assert mock_makedirs.call_count == 0
    assert mock_open_fn.call_count == 0


@patch(
    "scripts.conversion_script.urlopen",
    return_value=MockResponse("not_exist"),
)
@patch("os.path.exists", return_value=False)
@patch("os.makedirs", side_effect=Mock())
@patch("__builtin__.open", new_callable=mock_open)
@patch("os.chmod", side_effect=Mock())
def test_setup_convert2rhel_file_not_exist(
    mock_chmod, mock_open_fn, mock_makedirs, mock_exist, mock_urlopen
):
    test_file = RequiredFile("/mock/path/file.txt", "not_exist")
    required_files = [test_file]

    setup_convert2rhel(required_files)

    assert mock_exist.call_count == 2
    assert mock_urlopen.call_count == 1
    assert mock_makedirs.call_count == 1
    assert mock_open_fn.call_count == 1
    assert mock_chmod.call_count == 1
