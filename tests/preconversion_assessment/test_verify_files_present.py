from mock import patch, mock_open

from scripts.preconversion_assessment_script import (
    verify_required_files_are_present,
    RequiredFile,
)


def test_verify_required_files_are_present_exist():
    required_files = [
        RequiredFile("/mock/path/file1.txt"),
        RequiredFile("/mock/path/file2.txt"),
    ]
    mock_open_func = mock_open(read_data="dummy content")

    with patch("__builtin__.open", mock_open_func):
        verify_required_files_are_present(required_files)

    assert mock_open_func.call_count == len(required_files)

    for required_file in required_files:
        assert required_file.is_file_present
        assert required_file.sha512_on_system is not None


def test_verify_required_files_are_present_not_found():
    required_files = [
        RequiredFile("/mock/path/file1.txt"),
        RequiredFile("/mock/path/file2.txt"),
    ]
    with patch("__builtin__.open", new_callable=mock_open) as mock_file:
        mock_file.side_effect = IOError()
        verify_required_files_are_present(required_files)

    assert mock_file.call_count == len(required_files)

    for required_file in required_files:
        assert not required_file.is_file_present
        assert required_file.sha512_on_system is None
