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


def test_collect_report_level_expected():
    """Should be sorted descending from the 'worst' status"""
    expected_output = ["ERROR", "ERROR", "WARNING", "WARNING", "SUCCESS", "SUCCESS"]
    result = collect_report_level(SAMPLE_ACTION_RESULTS)
    assert result == expected_output


def test_collect_report_level_unknown_status():
    """Should ignore unknown statuses in report"""
    expected_output = ["ERROR", "WARNING", "WARNING", "INFO", "SUCCESS"]

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
    result = collect_report_level(action_results_test)
    assert result == expected_output
