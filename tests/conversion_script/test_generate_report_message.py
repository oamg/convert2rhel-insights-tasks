import pytest
from scripts.conversion_script import generate_report_message


@pytest.mark.parametrize(
    ("highest_status", "expected_message", "has_alert"),
    [
        (
            "SUCCESS",
            (
                "No problems found. The system was converted successfully. Please,"
                " reboot your system at your earlier convenience to make sure the "
                "system is using the RHEL Kernel."
            ),
            False,
        ),
        (
            "INFO",
            (
                "No problems found. The system was converted successfully. Please,"
                " reboot your system at your earlier convenience to make sure the "
                "system is using the RHEL Kernel."
            ),
            False,
        ),
        (
            "WARNING",
            (
                "No problems found. The system was converted successfully. Please,"
                " reboot your system at your earlier convenience to make sure the "
                "system is using the RHEL Kernel."
            ),
            False,
        ),
        (
            "ERROR",
            "The conversion cannot proceed. You must resolve existing issues to perform the conversion.",
            True,
        ),
    ],
)
def test_generate_report_message(
    highest_status,
    expected_message,
    has_alert,
):
    assert generate_report_message(highest_status) == (
        expected_message,
        has_alert,
    )
