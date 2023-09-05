import pytest
from scripts.preconversion_assessment_script import generate_report_message


@pytest.mark.parametrize(
    "highest_status, expected_message",
    [
        ("SUCCESS", "No problems found. The system is ready for conversion."),
        ("INFO", "No problems found. The system is ready for conversion."),
        (
            "WARNING",
            "The conversion can proceed. However, "
            "there is one or more warnings about issues that might occur after the conversion.",
        ),
        (
            "SKIP",
            "The conversion cannot proceed. You must resolve existing issues to perform the conversion.",
        ),
        (
            "OVERRIDABLE",
            "The conversion cannot proceed. You must resolve existing issues to perform the conversion.",
        ),
        (
            "ERROR",
            "The conversion cannot proceed. You must resolve existing issues to perform the conversion.",
        ),
    ],
)
def test_generate_report_message(highest_status, expected_message):
    assert generate_report_message(highest_status) == expected_message
