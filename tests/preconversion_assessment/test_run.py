import subprocess
from mock import patch, Mock
import pytest

from scripts.preconversion_assessment_script import run_convert2rhel, ProcessError


def test_run_convert2rhel():
    mock_env = {"PATH": "/fake/path", "RHC_WORKER_CONVERT2RHEL_DISABLE_TELEMETRY": "1"}
    mock_process = Mock(spec=subprocess.Popen)
    mock_process.returncode = 0  # Simulate successful process

    with patch("os.environ", mock_env), patch(
        "subprocess.Popen", return_value=mock_process
    ) as mock_popen:
        run_convert2rhel()

    mock_popen.assert_called_once_with(
        ["/usr/bin/convert2rhel", "analysis", "--debug"],
        env={"PATH": "/fake/path", "CONVERT2RHEL_DISABLE_TELEMETRY": "1"},
        bufsize=1,
    )

    assert mock_process.returncode == 0


def test_run_convert2rhel_failure():
    mock_process = Mock(spec=subprocess.Popen)
    mock_process.returncode = 1  # Simulate a process failure

    with patch("subprocess.Popen", return_value=mock_process) as mock_popen:
        with pytest.raises(ProcessError, match="Convert2RHEL exited with code '1'."):
            run_convert2rhel()

    mock_popen.assert_called_once()
    assert mock_process.returncode == 1
