import os
import pytest

from convert2rhel_insights_tasks import main


@pytest.mark.parametrize(
    ("env", "expected"),
    (
        ({"RHC_WORKER_SCRIPT_MODE": "CONVERSION"}, {"SCRIPT_MODE": "CONVERSION"}),
        (
            {"RHC_WORKER_FOO": "BAR", "RHC_WORKER_BAR": "FOO"},
            {"FOO": "BAR", "BAR": "FOO"},
        ),
        (
            {"RHC_WORKER_FOO": "BAR", "RHC_BAR": "FOO"},
            {"FOO": "BAR", "RHC_BAR": "FOO"},
        ),
        (
            {"FOO": "BAR", "BAR": "FOO"},
            {"FOO": "BAR", "BAR": "FOO"},
        ),
    ),
)
def test_parse_environment_variables(env, expected, monkeypatch):
    monkeypatch.setattr(os, "environ", env)
    result = main.parse_environment_variables()

    assert result == expected


def test_parse_environment_variables_empty(monkeypatch):
    monkeypatch.setattr(os, "environ", {})
    result = main.parse_environment_variables()
    assert not result


@pytest.mark.parametrize(
    ("env", "expected"),
    (
        (
            {},
            {},
        ),
        (
            {"CONVERT2RHEL_ALLOW_UNAVAILABLE_KMODS": "0"},
            {},
        ),
        (
            {"CONVERT2RHEL_ALLOW_UNAVAILABLE_KMODS": "1"},
            {"CONVERT2RHEL_ALLOW_UNAVAILABLE_KMODS": "1"},
        ),
        (
            {"CONVERT2RHEL_CONFIGURE_HOST_METERING": "auto"},
            {"CONVERT2RHEL_CONFIGURE_HOST_METERING": "auto"},
        ),
        (
            {"CONVERT2RHEL_ALLOW_UNAVAILABLE_KMODS": "0", "SCRIPT_MODE": "ANALYSIS"},
            {"SCRIPT_MODE": "ANALYSIS"},
        ),
        (
            {
                "CONVERT2RHEL_OUTDATED_PACKAGE_CHECK_SKIP": "1",
                "CONVERT2RHEL_ALLOW_UNAVAILABLE_KMODS": "0",
                "SCRIPT_MODE": "ANALYSIS",
            },
            {
                "CONVERT2RHEL_OUTDATED_PACKAGE_CHECK_SKIP": "1",
                "SCRIPT_MODE": "ANALYSIS",
            },
        ),
        (
            {"OPTIONAL_REPOSITORIES": "None"},
            {},
        ),
        (
            {"ELS_DISABLED": "True"},
            {},
        ),
        (
            {"ELS_DISABLED": "True", "OPTIONAL_REPOSITORIES": "None"},
            {},
        ),
    ),
)
def test_prepare_environment_variables(env, expected, monkeypatch):
    monkeypatch.setattr(os, "environ", env)
    result = main.prepare_environment_variables(env)

    assert result == expected
