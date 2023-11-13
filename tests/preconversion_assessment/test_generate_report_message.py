import pytest
from scripts.preconversion_assessment_script import generate_report_message


@pytest.mark.parametrize(
    "highest_status, expected_message, has_alert",
    [
        ("SUCCESS", "No problems found. The system is ready for conversion.", False),
        ("INFO", "No problems found. The system is ready for conversion.", False),
        (
            "WARNING",
            "The conversion can proceed. However, "
            "there is one or more warnings about issues that might occur after the conversion.",
            False,
        ),
        (
            "SKIP",
            "The conversion cannot proceed. You must resolve existing issues to perform the conversion.",
            True,
        ),
        (
            "OVERRIDABLE",
            "The conversion cannot proceed. You must resolve existing issues to perform the conversion.",
            True,
        ),
        (
            "ERROR",
            "The conversion cannot proceed. You must resolve existing issues to perform the conversion.",
            True,
        ),
    ],
)
def test_generate_report_message(highest_status, expected_message, has_alert):
    assert generate_report_message(highest_status) == (expected_message, has_alert)
