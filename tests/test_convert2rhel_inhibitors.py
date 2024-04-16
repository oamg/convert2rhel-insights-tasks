from mock import patch
from scripts.c2r_script import check_convert2rhel_inhibitors_before_run


@patch("scripts.c2r_script.os.path.exists", return_value=False)
@patch("scripts.c2r_script._check_ini_file_modified", return_value=False)
def test_no_inhibitors(mock_ini_file_modified, mock_custom_ini):
    check_convert2rhel_inhibitors_before_run()
    mock_ini_file_modified.assert_called_once()
    mock_custom_ini.assert_called_once()
