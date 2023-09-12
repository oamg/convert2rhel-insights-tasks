import pytest
from scripts.preconversion_assessment_script import (
    find_highest_report_level,
)


@pytest.mark.parametrize(
    ("actions", "expected"),
    (
        (
            {
                "action1": {
                    "result": {"level": "ERROR"},
                    "messages": [{"level": "SUCCESS"}],
                },
                "action2": {
                    "result": {"level": "WARNING"},
                    "messages": [{"level": "SUCCESS"}],
                },
            },
            "ERROR",
        ),
        (
            {
                "action1": {
                    "result": {"level": "SUCCESS"},
                    "messages": [],
                },
                "action2": {
                    "result": {"level": "SUCCESS"},
                    "messages": [],
                },
            },
            "SUCCESS",
        ),
        (
            {
                "action1": {
                    "result": {"level": "SUCCESS"},
                    "messages": [{"level": "WARNING"}],
                },
                "action2": {
                    "result": {"level": "SUCCESS"},
                    "messages": [],
                },
            },
            "WARNING",
        ),
        (
            {
                "action1": {
                    "result": {"level": "INFO"},
                    "messages": [{"level": "SUCCESS"}],
                },
                "action2": {
                    "result": {"level": "SUCCESS"},
                    "messages": [],
                },
            },
            "INFO",
        ),
        (
            {
                "action1": {
                    "result": {"level": "INFO"},
                    "messages": [{"level": "SUCCESS"}],
                },
                "action2": {
                    "result": {"level": "SKIP"},
                    "messages": [],
                },
            },
            "SKIP",
        ),
        (
            {
                "action1": {
                    "result": {"level": "INFO"},
                    "messages": [{"level": "OVERRIDABLE"}],
                },
                "action2": {
                    "result": {"level": "ERROR"},
                    "messages": [],
                },
            },
            "ERROR",
        ),
    ),
)
def test_find_highest_report_level_expected(actions, expected):
    """Should be sorted descending from the highest status to the lower one."""
    result = find_highest_report_level(actions)
    assert result == expected


def test_find_highest_report_level_unknown_status():
    """Should ignore unknown statuses in report"""
    expected_output = "ERROR"

    action_results_test = {
        "action1": {
            "result": {"level": "ERROR"},
            "messages": [{"level": "SUCCESS"}, {"level": "WARNING"}],
        },
        "action2": {
            "result": {"level": "WARNING"},
            "messages": [{"level": "FOO"}, {"level": "INFO"}],
        },
    }
    result = find_highest_report_level(action_results_test)
    assert result == expected_output
