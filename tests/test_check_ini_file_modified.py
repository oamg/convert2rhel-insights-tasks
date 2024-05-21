from mock import patch

from convert2rhel_insights_tasks.main import _check_ini_file_modified


@patch(
    "convert2rhel_insights_tasks.main.run_subprocess",
    return_value=("S.5....T  c /etc/convert2rhel.ini\n", True),
)
def test_check_ini_file_modified(mock_rpm_va):
    result = _check_ini_file_modified()
    assert result
    mock_rpm_va.assert_called_once()


@patch(
    "convert2rhel_insights_tasks.main.run_subprocess",
    return_value=("S.5....T  c /foo/bar\n", True),
)
def test_check_ini_file_not_modified(mock_rpm_va):
    result = _check_ini_file_modified()
    assert not result
    mock_rpm_va.assert_called_once()


@patch("convert2rhel_insights_tasks.main.run_subprocess", return_value=("", False))
def test_check_ini_file_no_changes(mock_rpm_va):
    result = _check_ini_file_modified()
    assert not result
    mock_rpm_va.assert_called_once()
