import pytest
from mock import patch, call

from scripts.preconversion_assessment_script import (
    install_convert2rhel,
    ProcessError,
)


@pytest.mark.parametrize("subprocess_mock", [(b"output", 0), (b"output", 0)])
def test_install_convert2rhel(subprocess_mock):
    with patch(
        "scripts.preconversion_assessment_script.run_subprocess",
        return_value=subprocess_mock,
    ) as mock_run_subprocess:
        install_convert2rhel()

    expected_calls = [
        ["yum", "install", "convert2rhel", "-y"],
        ["yum", "update", "convert2rhel", "-y"],
    ]

    assert mock_run_subprocess.call_args_list == [call(args) for args in expected_calls]


def test_install_convert2rhel_raise_exception():
    with patch(
        "scripts.preconversion_assessment_script.run_subprocess",
        return_value=(b"failed", 1),
    ) as mock_run_subprocess:
        with pytest.raises(
            ProcessError,
            match="Installing convert2rhel with yum exited with code '1' and output: failed.",
        ):
            install_convert2rhel()

    expected_calls = [["yum", "install", "convert2rhel", "-y"]]

    assert mock_run_subprocess.call_args_list == [call(args) for args in expected_calls]


def test_update_convert2rhel_raise_exception():
    with patch(
        "scripts.preconversion_assessment_script.run_subprocess",
        side_effect=[(b"output", 0), (b"failed", 1)],
    ) as mock_run_subprocess:
        with pytest.raises(
            ProcessError,
            match="Updating convert2rhel with yum exited with code '1' and output: failed.",
        ):
            install_convert2rhel()

    expected_calls = [
        ["yum", "install", "convert2rhel", "-y"],
        ["yum", "update", "convert2rhel", "-y"],
    ]

    assert mock_run_subprocess.call_args_list == [call(args) for args in expected_calls]
