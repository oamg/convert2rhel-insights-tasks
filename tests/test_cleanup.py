from mock import patch

from convert2rhel_insights_tasks.main import cleanup, RequiredFile


@patch("convert2rhel_insights_tasks.main.YUM_TRANSACTIONS_TO_UNDO", new=set())
@patch("convert2rhel_insights_tasks.main.run_subprocess", return_value=("", 0))
def test_cleanup_with_file_to_remove(mock_yum_undo):
    """Only downloaded files are removed."""

    present_file = RequiredFile("/already/present")
    required_files = [present_file]

    cleanup(required_files)

    assert mock_yum_undo.call_count == 0


@patch("convert2rhel_insights_tasks.main.YUM_TRANSACTIONS_TO_UNDO", new=set())
@patch("convert2rhel_insights_tasks.main.run_subprocess", return_value=("", 1))
def test_cleanup_with_file_to_keep(mock_yum_undo):
    """Only downloaded files are removed."""

    keep_downloaded_file = RequiredFile("/download/keep", keep=True)
    required_files = [keep_downloaded_file]

    cleanup(required_files)

    assert mock_yum_undo.call_count == 0


@patch("convert2rhel_insights_tasks.main.YUM_TRANSACTIONS_TO_UNDO", new=set([1]))
@patch("convert2rhel_insights_tasks.main.run_subprocess", return_value=("", 0))
def test_cleanup_with_undo_yum(mock_yum_undo):
    """Only downloaded files are removed."""

    present_file = RequiredFile("/already/present")
    required_files = [present_file]

    cleanup(required_files)

    assert mock_yum_undo.call_count == 1
