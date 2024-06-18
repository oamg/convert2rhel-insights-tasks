import json
import jsonschema
import pytest
from convert2rhel_insights_tasks.main import OutputCollector, STATUS_CODE


@pytest.mark.parametrize(
    ("schema",),
    (
        ("schemas/convert2rhel_insights_tasks_schema_1.0.json",),
        ("schemas/convert2rhel_insights_tasks_schema_1.1.json",),
    ),
)
def test_output_schema(schema):
    """Test that (pre)conversion report is wrapped in expected json"""
    for status in STATUS_CODE:
        output_collector = OutputCollector(status=status)
        empty_output = output_collector.to_dict()

        with open(schema, "r") as handler:
            schema_json = json.load(handler)

        # If some difference between generated json and its schema invoke exception
        jsonschema.validate(instance=empty_output, schema=schema_json)
        assert not empty_output["alert"]


@pytest.mark.parametrize(
    ("schema",),
    (
        ("schemas/convert2rhel_insights_tasks_schema_1.0.json",),
        ("schemas/convert2rhel_insights_tasks_schema_1.1.json",),
    ),
)
def test_output_schema_entries_report(schema):
    """
    Test that pre-conversion report is wrapped in expected json with entries
    key.
    """
    output_collector = OutputCollector(status="WARNING")
    # Not close to a real json returned by the assessment report, but we don't
    # have to check that here.
    output_collector.entries = {"hi": "world"}
    full_output = output_collector.to_dict()

    with open(schema, "r") as handler:
        schema_json = json.load(handler)
    # If some difference between generated json and its schema invoke exception
    jsonschema.validate(instance=full_output, schema=schema_json)
