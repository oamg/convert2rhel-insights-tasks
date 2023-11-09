import pytest
from scripts.conversion_script import generate_report_message


@pytest.mark.parametrize(
    ("highest_status", "expected_message"),
    [
        ("SUCCESS", "No problems found. The system was converted successfully."),
        ("INFO", "No problems found. The system was converted successfully."),
        ("WARNING", "No problems found. The system was converted successfully."),
        (
            "ERROR",
            "The conversion cannot proceed. You must resolve existing issues to perform the conversion.",
        ),
    ],
)
def test_generate_report_message(highest_status, expected_message):
    assert generate_report_message(highest_status) == expected_message
