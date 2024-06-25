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
