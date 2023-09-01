from scripts.preconversion_assessment_script import (
    collect_report_level,
)

SAMPLE_ACTION_RESULTS = {
    "action1": {
        "result": {"level": "ERROR"},
        "messages": [{"level": "SUCCESS"}, {"level": "WARNING"}],
    },
    "action2": {
        "result": {"level": "WARNING"},
        "messages": [{"level": "SUCCESS"}, {"level": "ERROR"}],
    },
}


def test_collect_report_level():
    """Should be sorted descending from the 'worst' status"""
    expected_output = ["ERROR", "ERROR", "WARNING", "WARNING", "SUCCESS", "SUCCESS"]
    result = collect_report_level(SAMPLE_ACTION_RESULTS)
    assert result == expected_output
