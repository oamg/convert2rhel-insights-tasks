from mock import patch, Mock
import pytest
from convert2rhel_insights_tasks.main import RequiredFile


@pytest.fixture(name="required_file_instance")
def fixture_required_file_instance():
    return RequiredFile(path="/test/path", host="http://example.com")


def test_create_host(required_file_instance):
    with patch("convert2rhel_insights_tasks.main.urlopen") as mock_urlopen, patch(
        "convert2rhel_insights_tasks.main.os.makedirs"
    ) as mock_makedirs, patch(
        "convert2rhel_insights_tasks.main.open"
    ) as mock_open, patch(
        "convert2rhel_insights_tasks.main.os.chmod"
    ) as mock_chmod:
        mock_response = Mock()
        mock_response.read.return_value = b"Mocked data"
        mock_urlopen.return_value = mock_response

        required_file_instance.create_from_host_url_data()

        mock_urlopen.assert_called_once_with("http://example.com")
        mock_makedirs.assert_called_once_with("/test", mode=0o755)
        mock_open.assert_called_once_with("/test/path", mode="w")
        mock_chmod.assert_called_once_with("/test/path", 0o644)
        assert required_file_instance.created


def test_create_data(required_file_instance):
    with patch("convert2rhel_insights_tasks.main.urlopen") as mock_urlopen, patch(
        "convert2rhel_insights_tasks.main.os.path.dirname", return_value="/test"
    ) as mock_dirname, patch(
        "convert2rhel_insights_tasks.main.os.path.exists", return_value=True
    ) as mock_exists, patch(
        "convert2rhel_insights_tasks.main.os.makedirs"
    ) as mock_makedirs, patch(
        "convert2rhel_insights_tasks.main.open"
    ) as mock_open, patch(
        "convert2rhel_insights_tasks.main.os.chmod"
    ) as mock_chmod:
        required_file_instance.create_from_data(b"Mocked data")

        mock_urlopen.assert_not_called()
        mock_dirname.assert_called_once()
        mock_exists.assert_called_once()
        mock_makedirs.assert_not_called()
        mock_open.assert_called_once_with("/test/path", mode="w")
        mock_chmod.assert_called_once_with("/test/path", 0o644)
        assert required_file_instance.created


def test_create_exception(required_file_instance):
    with patch("convert2rhel_insights_tasks.main.urlopen") as mock_urlopen, patch(
        "convert2rhel_insights_tasks.main.os.makedirs"
    ) as mock_makedirs, patch(
        "convert2rhel_insights_tasks.main.open", side_effect=OSError("Can't create dir")
    ) as mock_open, patch(
        "convert2rhel_insights_tasks.main.os.chmod"
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
        assert not required_file_instance.created


@patch("convert2rhel_insights_tasks.main.os.remove")
def test_delete(mock_remove, required_file_instance):
    result = required_file_instance.delete()
    mock_remove.assert_not_called()
    assert not result

    required_file_instance.created = True
    result = required_file_instance.delete()
    mock_remove.assert_called_once_with("/test/path")
    assert result


@patch(
    "convert2rhel_insights_tasks.main.os.remove", side_effect=OSError("File not found")
)
def test_delete_file_not_exists(mock_remove, required_file_instance):
    result = required_file_instance.delete()
    mock_remove.assert_not_called()
    assert not result

    required_file_instance.created = True
    result = required_file_instance.delete()
    mock_remove.assert_called_once_with("/test/path")
    assert not result


@patch("convert2rhel_insights_tasks.main.os.rename")
def test_restore(mock_rename, required_file_instance):
    result = required_file_instance.restore()
    mock_rename.assert_not_called()
    assert not result

    required_file_instance.backup_created = True
    result = required_file_instance.restore()
    mock_rename.assert_called_once_with(
        "/test/path.backup",
        "/test/path",
    )
    assert result


@patch(
    "convert2rhel_insights_tasks.main.os.rename", side_effect=OSError("File not found")
)
def test_restore_backup_not_exists(mock_rename, required_file_instance):
    required_file_instance.backup_created = True
    result = required_file_instance.restore()
    mock_rename.assert_called_once_with(
        "/test/path.backup",
        "/test/path",
    )
    assert not result


@patch("convert2rhel_insights_tasks.main.os.path.exists", return_value=True)
@patch("convert2rhel_insights_tasks.main.os.rename")
def test_backup(mock_rename, mock_exists, required_file_instance):
    result = required_file_instance.backup()
    mock_rename.assert_called_once_with("/test/path", "/test/path.backup")
    mock_exists.assert_called_once_with("/test/path")
    assert result


@patch("convert2rhel_insights_tasks.main.os.path.exists", return_value=False)
@patch("convert2rhel_insights_tasks.main.os.rename")
def test_backup_file_not_exists(mock_rename, mock_exists, required_file_instance):
    result = required_file_instance.backup()
    mock_exists.assert_called_once_with("/test/path")
    mock_rename.assert_not_called()
    assert not result


@patch("convert2rhel_insights_tasks.main.os.path.exists", return_value=True)
@patch(
    "convert2rhel_insights_tasks.main.os.rename", side_effect=OSError("File not found")
)
def test_backup_oserror(mock_rename, mock_exists, required_file_instance):
    result = required_file_instance.backup()
    mock_exists.assert_called_once_with("/test/path")
    mock_rename.assert_called_once_with("/test/path", "/test/path.backup")
    assert not result
