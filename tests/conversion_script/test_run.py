from mock import patch
import pytest

from scripts.conversion_script import run_convert2rhel, ProcessError


def test_run_convert2rhel():
    mock_env = {"PATH": "/fake/path", "RHC_WORKER_CONVERT2RHEL_DISABLE_TELEMETRY": "1"}

    with patch("os.environ", mock_env), patch(
        "scripts.conversion_script.run_subprocess", return_value=(b"", 0)
    ) as mock_popen:
        run_convert2rhel()

    mock_popen.assert_called_once_with(
        ["/usr/bin/convert2rhel", "-y"],
        env={"PATH": "/fake/path", "CONVERT2RHEL_DISABLE_TELEMETRY": "1"},
    )


def test_run_convert2rhel_failure():
    with patch(
        "scripts.conversion_script.run_subprocess", return_value=(b"", 1)
    ) as mock_popen:
        with pytest.raises(
            ProcessError, match="convert2rhel execution exited with code '1'."
        ):
            run_convert2rhel()

    mock_popen.assert_called_once()
