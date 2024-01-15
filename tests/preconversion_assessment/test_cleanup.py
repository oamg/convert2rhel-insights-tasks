from mock import patch

from scripts.preconversion_assessment_script import cleanup, RequiredFile


@patch("scripts.preconversion_assessment_script.YUM_TRANSACTIONS_TO_UNDO", new=set())
@patch("scripts.preconversion_assessment_script.run_subprocess", return_value=("", 0))
def test_cleanup_with_file_to_remove(mock_yum_undo):
    """Only downloaded files are removed."""

    present_file = RequiredFile("/already/present")
    required_files = [present_file]

    cleanup(required_files)

    assert mock_yum_undo.call_count == 0


@patch("scripts.preconversion_assessment_script.YUM_TRANSACTIONS_TO_UNDO", new=set([1]))
@patch("scripts.preconversion_assessment_script.run_subprocess", return_value=("", 1))
def test_cleanup_with_undo_yum(mock_yum_undo):
    """Only downloaded files are removed."""

    present_file = RequiredFile("/already/present")
    required_files = [present_file]
    cleanup(required_files)

    assert mock_yum_undo.call_count == 1
