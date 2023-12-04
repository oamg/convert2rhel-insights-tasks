from mock import patch, mock_open


from scripts.preconversion_assessment_script import check_for_inhibitors_in_rollback


@patch(
    "__builtin__.open",
    new_callable=mock_open,
    read_data="\n".join(
        [
            "Some lines before the warning",
            "WARNING - Abnormal exit! Performing rollback ...",
            "Error message 1",
            "Error message 2",
            "Pre-conversion analysis report",
            "Some lines after the report",
        ]
    ),
)
def test_rollback_with_errors(mock_open_fn):
    result = check_for_inhibitors_in_rollback()
    mock_open_fn.assert_called_once()
    assert result == "Error message 1\nError message 2"


@patch(
    "__builtin__.open",
    new_callable=mock_open,
    read_data="\n".join(
        [
            "Some lines before the warning",
            "WARNING - Abnormal exit! Performing rollback ...",
            "test-blabla",
            "Pre-conversion analysis report",
            "Some lines after the report",
        ]
    ),
)
def test_rollback_with_no_matches(mock_open_fn):
    result = check_for_inhibitors_in_rollback()
    mock_open_fn.assert_called_once()
    assert result == ""


@patch(
    "__builtin__.open",
    new_callable=mock_open,
    read_data="".join(
        [
            "No warning or report",
            "No errors here",
        ]
    ),
)
def test_no_rollback_section_value_error(mock_open_fn):
    result = check_for_inhibitors_in_rollback()
    mock_open_fn.assert_called_once()
    assert result == ""


@patch("__builtin__.open", side_effect=IOError("File not found"))
def test_io_error(mock_open_fn):
    result = check_for_inhibitors_in_rollback()
    mock_open_fn.assert_called_once()
    assert result == ""


@patch(
    "__builtin__.open",
    new_callable=mock_open,
    read_data="\n".join(
        [
            "Some lines before the warning",
            "WARNING - Abnormal exit! Performing rollback ...",
            "WARNING - Couldn't find a backup for centos-logos-70.0.6-3.el7.centos.noarch package.",
            "WARNING - Couldn't find a backup for centos-release-7-9.2009.1.el7.centos.x86_64 package.",
            "Pre-conversion analysis report",
            "Some lines after the report",
        ]
    ),
)
def test_match_backup_warning(mock_open_fn):
    result = check_for_inhibitors_in_rollback()
    mock_open_fn.assert_called_once()
    assert (
        result
        == "WARNING - Couldn't find a backup for centos-logos-70.0.6-3.el7.centos.noarch package.\nWARNING - Couldn't find a backup for centos-release-7-9.2009.1.el7.centos.x86_64 package."
    )
