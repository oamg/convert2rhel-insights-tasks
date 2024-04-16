from mock import patch, Mock
import pytest
from scripts.c2r_script import RequiredFile


@pytest.fixture(name="required_file_instance")
def fixture_required_file_instance():
    return RequiredFile(path="/test/path", host="http://example.com")


def test_create_host(required_file_instance):
    with patch("scripts.c2r_script.urlopen") as mock_urlopen, patch(
        "scripts.c2r_script.os.makedirs"
    ) as mock_makedirs, patch("scripts.c2r_script.open") as mock_open, patch(
        "scripts.c2r_script.os.chmod"
    ) as mock_chmod:
        mock_response = Mock()
        mock_response.read.return_value = b"Mocked data"
        mock_urlopen.return_value = mock_response

        required_file_instance.create_from_host_url_data()

        mock_urlopen.assert_called_once_with("http://example.com")
        mock_makedirs.assert_called_once_with("/test", mode=0o755)
        mock_open.assert_called_once_with("/test/path", mode="w")
        mock_chmod.assert_called_once_with("/test/path", 0o644)


def test_create_data(required_file_instance):
    with patch("scripts.c2r_script.urlopen") as mock_urlopen, patch(
        "scripts.c2r_script.os.path.dirname", return_value="/test"
    ) as mock_dirname, patch(
        "scripts.c2r_script.os.path.exists", return_value=True
    ) as mock_exists, patch(
        "scripts.c2r_script.os.makedirs"
    ) as mock_makedirs, patch(
        "scripts.c2r_script.open"
    ) as mock_open, patch(
        "scripts.c2r_script.os.chmod"
    ) as mock_chmod:
        required_file_instance.create_from_data(b"Mocked data")

        mock_urlopen.assert_not_called()
        mock_dirname.assert_called_once()
        mock_exists.assert_called_once()
        mock_makedirs.assert_not_called()
        mock_open.assert_called_once_with("/test/path", mode="w")
        mock_chmod.assert_called_once_with("/test/path", 0o644)


def test_create_exception(required_file_instance):
    with patch("scripts.c2r_script.urlopen") as mock_urlopen, patch(
        "scripts.c2r_script.os.makedirs"
    ) as mock_makedirs, patch(
        "scripts.c2r_script.open", side_effect=OSError("Can't create dir")
    ) as mock_open, patch(
        "scripts.c2r_script.os.chmod"
    ) as mock_chmod:
        mock_response = Mock()
        mock_response.read.return_value = b"Mocked data"
        mock_urlopen.return_value = mock_response

        result = required_file_instance.create_from_host_url_data()
        assert not result
        mock_urlopen.assert_called_once_with("http://example.com")
        mock_makedirs.assert_called_once_with("/test", mode=0o755)
        mock_open.assert_called_once_with("/test/path", mode="w")
        mock_chmod.assert_not_called()


@patch("scripts.c2r_script.os.remove")
def test_delete(mock_remove, required_file_instance):
    result = required_file_instance.delete()
    mock_remove.assert_called_once_with("/test/path")
    assert result


@patch("scripts.c2r_script.os.remove", side_effect=OSError("File not found"))
def test_delete_file_not_exists(mock_remove, required_file_instance):
    result = required_file_instance.delete()
    mock_remove.assert_called_once_with("/test/path")
    assert not result


@patch("scripts.c2r_script.os.rename")
def test_restore(mock_rename, required_file_instance):
    result = required_file_instance.restore()
    mock_rename.assert_called_once_with(
        "/test/path.backup",
        "/test/path",
    )
    assert result


@patch("scripts.c2r_script.os.rename", side_effect=OSError("File not found"))
def test_restore_backup_not_exists(mock_rename, required_file_instance):
    result = required_file_instance.restore()
    mock_rename.assert_called_once_with(
        "/test/path.backup",
        "/test/path",
    )
    assert not result


@patch("scripts.c2r_script.os.rename")
def test_backup(mock_rename, required_file_instance):
    result = required_file_instance.backup()
    mock_rename.assert_called_once_with("/test/path", "/test/path.backup")
    assert result


@patch("scripts.c2r_script.os.rename", side_effect=OSError("File not found"))
def test_backup_file_not_exists(mock_rename, required_file_instance):
    result = required_file_instance.backup()
    mock_rename.assert_called_once_with("/test/path", "/test/path.backup")
    assert not result
