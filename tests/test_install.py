import pytest
from mock import  patch, call

from main import (
    install_convert2rhel,
)


@pytest.mark.parametrize("subprocess_mock", [(b'output', None), (b'output', None)])
def test_install_convert2rhel(subprocess_mock):
    with patch("subprocess.check_output", side_effect=subprocess_mock) as mock_check_output:
        install_convert2rhel()

    expected_calls = [
        ["yum", "install", "convert2rhel", "-y"],
        ["yum", "update", "convert2rhel", "-y"],
    ]

    assert mock_check_output.call_args_list == [call(args) for args in expected_calls]
