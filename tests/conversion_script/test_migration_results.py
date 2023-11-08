import json
from mock import patch
import pytest
from scripts.conversion_script import parse_migration_results


def test_no_migration_results(tmpdir):
    migration_result_file = tmpdir.join("migration_result")
    with patch(
        "scripts.conversion_script.C2R_MIGRATION_RESULTS_FILE",
        str(migration_result_file),
    ):
        assert not parse_migration_results()


@pytest.mark.parametrize(
    ("content", "expected"),
    (
        (
            {"activities": [{"success": True}]},
            True,
        ),
        (
            {"activities": [{"success": False}]},
            False,
        ),
        (
            {"activities": [{"success": False}, {"success": True}]},
            True,
        ),
        (
            {"activities": [{"success": True}, {"success": False}]},
            False,
        ),
        (
            {"activities": [{}]},
            False,
        ),
        (
            {},
            False,
        ),
        (
            None,
            False,
        ),
    ),
)
def test_migration_results_content(content, expected, tmpdir):
    migration_result_file = tmpdir.join("migration_result")
    migration_result_file.write(json.dumps(content, indent=4))
    with patch(
        "scripts.conversion_script.C2R_MIGRATION_RESULTS_FILE",
        str(migration_result_file),
    ):
        assert parse_migration_results() == expected
