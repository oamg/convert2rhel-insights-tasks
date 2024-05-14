from mock import patch
from convert2rhel_insights_tasks.main import check_convert2rhel_inhibitors_before_run


@patch("convert2rhel_insights_tasks.main.os.path.exists", return_value=False)
@patch("convert2rhel_insights_tasks.main._check_ini_file_modified", return_value=False)
def test_no_inhibitors(mock_ini_file_modified, mock_custom_ini):
    check_convert2rhel_inhibitors_before_run()
    mock_ini_file_modified.assert_called_once()
    mock_custom_ini.assert_called_once()
