import pytest
from mock import patch

from convert2rhel_insights_tasks import main
from convert2rhel_insights_tasks.main import run_convert2rhel


def test_run_convert2rhel_custom_variables(monkeypatch):
    monkeypatch.setattr(main, "IS_ANALYSIS", True)
    mock_env = {"FOO": "BAR", "BAR": "BAZ", "LALA": "LAND"}

    with patch(
        "convert2rhel_insights_tasks.main.run_subprocess", return_value=(b"", 0)
    ) as mock_popen:
        run_convert2rhel(mock_env)

    mock_popen.assert_called_once_with(
        ["/usr/bin/convert2rhel", "analyze", "-y", "--els"],
        env={"FOO": "BAR", "BAR": "BAZ", "LALA": "LAND"},
    )


def test_run_convert2rhel_conversion(monkeypatch):
    monkeypatch.setattr(main, "SCRIPT_TYPE", "CONVERSION")
    mock_env = {
        "PATH": "/fake/path",
        "CONVERT2RHEL_DISABLE_TELEMETRY": "1",
        "FOO": "1",
    }

    with patch(
        "convert2rhel_insights_tasks.main.run_subprocess", return_value=(b"", 0)
    ) as mock_popen:
        run_convert2rhel(mock_env)

    mock_popen.assert_called_once_with(
        ["/usr/bin/convert2rhel", "-y", "--els"],
        env={
            "PATH": "/fake/path",
            "CONVERT2RHEL_DISABLE_TELEMETRY": "1",
            "FOO": "1",
        },
    )


def test_run_convert2rhel_analysis(monkeypatch):
    monkeypatch.setattr(main, "IS_ANALYSIS", True)
    mock_env = {"PATH": "/fake/path", "CONVERT2RHEL_DISABLE_TELEMETRY": "1"}

    with patch(
        "convert2rhel_insights_tasks.main.run_subprocess", return_value=(b"", 0)
    ) as mock_popen:
        run_convert2rhel(mock_env)

    mock_popen.assert_called_once_with(
        ["/usr/bin/convert2rhel", "analyze", "-y", "--els"],
        env={"PATH": "/fake/path", "CONVERT2RHEL_DISABLE_TELEMETRY": "1"},
    )


@pytest.mark.parametrize(
    (
        "is_analysis",
        "els_disabled",
        "optional_repositories",
        "expected_cmd",
    ),
    (
        (True, "True", "None", ["/usr/bin/convert2rhel", "analyze", "-y"]),
        (True, "true", "None", ["/usr/bin/convert2rhel", "analyze", "-y"]),
        (True, "False", "None", ["/usr/bin/convert2rhel", "analyze", "-y", "--els"]),
        (True, "false", "None", ["/usr/bin/convert2rhel", "analyze", "-y", "--els"]),
        (
            True,
            "False",
            "rhel-7-server-rpm",
            [
                "/usr/bin/convert2rhel",
                "analyze",
                "-y",
                "--els",
                "--enablerepo",
                "rhel-7-server-rpm",
                "--enablerepo",
                "rhel-7-server-els-rpms",
            ],
        ),
        (
            True,
            "False",
            "rhel-7-server-rpm, rhel-7-server-rpm-extras",
            [
                "/usr/bin/convert2rhel",
                "analyze",
                "-y",
                "--els",
                "--enablerepo",
                "rhel-7-server-rpm-extras",
                "--enablerepo",
                "rhel-7-server-rpm",
                "--enablerepo",
                "rhel-7-server-els-rpms",
            ],
        ),
        # Make sure that this also pass for conversion
        (False, "True", "None", ["/usr/bin/convert2rhel", "-y"]),
        (False, "true", "None", ["/usr/bin/convert2rhel", "-y"]),
        (False, "False", "None", ["/usr/bin/convert2rhel", "-y", "--els"]),
        (False, "false", "None", ["/usr/bin/convert2rhel", "-y", "--els"]),
        (
            False,
            "False",
            "rhel-7-server-rpm",
            [
                "/usr/bin/convert2rhel",
                "-y",
                "--els",
                "--enablerepo",
                "rhel-7-server-rpm",
                "--enablerepo",
                "rhel-7-server-els-rpms",
            ],
        ),
        (
            False,
            "False",
            "rhel-7-server-rpm, rhel-7-server-rpm-extras",
            [
                "/usr/bin/convert2rhel",
                "-y",
                "--els",
                "--enablerepo",
                "rhel-7-server-rpm-extras",
                "--enablerepo",
                "rhel-7-server-rpm",
                "--enablerepo",
                "rhel-7-server-els-rpms",
            ],
        ),
        # Make sure we don't have duplicates
        (
            False,
            "False",
            "rhel-7-server-rpm, rhel-7-server-rpm, rhel-7-server-rpm-extras",
            [
                "/usr/bin/convert2rhel",
                "-y",
                "--els",
                "--enablerepo",
                "rhel-7-server-rpm-extras",
                "--enablerepo",
                "rhel-7-server-rpm",
                "--enablerepo",
                "rhel-7-server-els-rpms",
            ],
        ),
    ),
)
def test_run_convert2rhel_command_line_switch(
    is_analysis, els_disabled, optional_repositories, expected_cmd, monkeypatch
):
    monkeypatch.setattr(main, "IS_ANALYSIS", is_analysis)
    mock_env = {
        "PATH": "/fake/path",
        "ELS_DISABLED": els_disabled,
        "OPTIONAL_REPOSITORIES": optional_repositories,
    }

    with patch(
        "convert2rhel_insights_tasks.main.run_subprocess", return_value=(b"", 0)
    ) as mock_popen:
        run_convert2rhel(mock_env)

    mock_popen.assert_called_once_with(
        expected_cmd,
        env={"PATH": "/fake/path"},
    )
