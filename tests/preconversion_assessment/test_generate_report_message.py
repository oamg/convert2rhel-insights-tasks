from scripts.preconversion_assessment_script import generate_report_message, STATUS_CODE


def test_generate_report_message():
    """All possible status codes result in string message"""
    for status_code in STATUS_CODE:
        message = generate_report_message(status_code)
        assert isinstance(message, str)
        assert message != ""
