import jsonschema
import json
from scripts.preconversion_assessment_script import OutputCollector


def test_output_schema():
    output_collector = OutputCollector()
    empty_output = output_collector.to_dict()

    with open("schemas/preconversion_assessment_schema_1.0.json", "r") as schema:
        schema_json = json.load(schema)
    # If some difference between generated json and its schema invoke exception
    jsonschema.validate(instance=empty_output, schema=schema_json)
