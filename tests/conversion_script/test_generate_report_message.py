import pytest
from scripts.conversion_script import RequiredFile, generate_report_message


@pytest.mark.parametrize(
    ("highest_status", "expected_message", "has_alert", "file_should_be_kept"),
    [
        (
            "SUCCESS",
            "No problems found. The system was converted successfully.",
            False,
            True,
        ),
        (
            "INFO",
            "No problems found. The system was converted successfully.",
            False,
            True,
        ),
        (
            "WARNING",
            "No problems found. The system was converted successfully.",
            False,
            True,
        ),
        (
            "ERROR",
            "The conversion cannot proceed. You must resolve existing issues to perform the conversion.",
            True,
            False,
        ),
    ],
)
def test_generate_report_message(
    highest_status, expected_message, has_alert, file_should_be_kept
):
    file = RequiredFile("/foo/bar")
    assert generate_report_message(highest_status, file) == (
        expected_message,
        has_alert,
    )
    assert file.keep is file_should_be_kept
