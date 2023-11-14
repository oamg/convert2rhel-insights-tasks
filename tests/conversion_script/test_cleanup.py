from mock import Mock, patch

from scripts.conversion_script import cleanup, RequiredFile


@patch("os.path.exists", side_effect=Mock())
@patch("os.remove", side_effect=Mock())
def test_cleanup_with_file_to_remove(mock_remove, mock_exists):
    """Only downloaded files are removed."""

    present_file = RequiredFile("/already/present")
    present_file.is_file_present = True
    downloaded_file = RequiredFile("/downloaded")
    required_files = [present_file, downloaded_file]

    cleanup(required_files)

    assert mock_exists.call_count == 1
    assert mock_remove.call_count == 1
