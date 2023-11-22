from mock import Mock, patch

from scripts.conversion_script import cleanup, RequiredFile


@patch("os.path.exists", side_effect=Mock())
@patch("os.remove", side_effect=Mock())
@patch("scripts.conversion_script._create_or_restore_backup_file")
def test_cleanup_with_file_to_remove(mock_restore, mock_remove, mock_exists):
    """Only downloaded files are removed."""

    present_file = RequiredFile("/already/present")
    required_files = [present_file]

    cleanup(required_files)

    # For removal of file, then two checks in backup function
    assert mock_exists.call_count == 1
    assert mock_remove.call_count == 1
    assert mock_restore.call_count == 1


@patch("os.path.exists", side_effect=Mock())
@patch("os.remove", side_effect=Mock())
@patch("scripts.conversion_script._create_or_restore_backup_file")
def test_cleanup_with_file_to_keep(mock_restore, mock_remove, mock_exists):
    """Only downloaded files are removed."""

    keep_downloaded_file = RequiredFile("/download/keep", keep=True)
    required_files = [keep_downloaded_file]

    cleanup(required_files)

    # For removal of file, then two checks in backup function
    assert mock_exists.call_count == 0
    assert mock_remove.call_count == 0
    assert mock_restore.call_count == 0
