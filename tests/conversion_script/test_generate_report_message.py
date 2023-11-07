import pytest
from scripts.conversion_script import generate_report_message


@pytest.mark.parametrize(
    ("migration_result", "highest_status", "expected_message"),
    [
        (True, "SUCCESS", "No problems found. The system was converted successfully."),
        (True, "INFO", "No problems found. The system was converted successfully."),
        (True, "WARNING", "No problems found. The system was converted successfully."),
        (
            False,
            "ERROR",
            "The conversion cannot proceed. You must resolve existing issues to perform the conversion.",
        ),
    ],
)
def test_generate_report_message(migration_result, highest_status, expected_message):
    assert generate_report_message(migration_result, highest_status) == expected_message
