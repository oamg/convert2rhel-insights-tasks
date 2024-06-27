import sys
import os
import ruamel.yaml

# Get the last argument used in the commandline if available, otherwise, use
# "worker" as the default value.
SYNC_PROJECT = sys.argv[1:][-1] if sys.argv[1:] else "worker"

# Scripts located in this project
SCRIPT_PATH = "convert2rhel_insights_tasks/main.py"

SCRIPTS_YAML_PATH = {
    # TODO(r0x0d): Deprecate this in the future
    "worker": (
        os.path.join(
            "..", "rhc-worker-script/development/nginx/data/convert2rhel_analysis.yml"
        ),
        os.path.join(
            "..", "rhc-worker-script/development/nginx/data/convert2rhel_conversion.yml"
        ),
    ),
    "tasks": (
        "playbooks/convert-to-rhel-analysis.yml",
        "playbooks/convert-to-rhel-conversion.yml",
    ),
    "advisor": (
        os.path.join(
            "..",
            "advisor-backend/api/advisor/tasks/playbooks/convert-to-rhel-analysis.yml",
        ),
        os.path.join(
            "..",
            "advisor-backend/api/advisor/tasks/playbooks/convert-to-rhel-conversion.yml",
        ),
    ),
}


def _get_updated_yaml_content(yaml_path, script_path):
    if not os.path.exists(yaml_path):
        raise SystemExit(f"Couldn't find yaml file: {yaml_path}")

    config, mapping, offset = ruamel.yaml.util.load_yaml_guess_indent(
        open(yaml_path, encoding="utf-8")
    )

    with open(script_path, encoding="utf-8") as script:
        content = script.read()

    script_type = "ANALYSIS" if "analysis" in yaml_path else "CONVERSION"
    config[0]["name"] = f"Convert2RHEL {script_type.title()}"
    config[0]["vars"]["content"] = content
    config[0]["vars"]["content_vars"]["SCRIPT_MODE"] = script_type
    return config, mapping, offset


def _write_content(config, path, mapping=None, offset=None):
    yaml = ruamel.yaml.YAML()
    if mapping and offset:
        yaml.indent(mapping=mapping, sequence=mapping, offset=offset)
    with open(path, "w", encoding="utf-8") as handler:
        yaml.dump(config, handler)


def main():
    if SYNC_PROJECT not in ("worker", "advisor", "tasks"):
        raise SystemExit(
            f"'{SYNC_PROJECT}' not recognized. Valid values are 'worker' or 'advisor'"
        )

    analysis_script, conversion_script = SCRIPTS_YAML_PATH[SYNC_PROJECT]

    config, mapping, offset = _get_updated_yaml_content(analysis_script, SCRIPT_PATH)
    print(f"Writing new content to {analysis_script}")
    _write_content(config, analysis_script, mapping, offset)
    config, mapping, offset = _get_updated_yaml_content(conversion_script, SCRIPT_PATH)
    print(f"Writing new content to {conversion_script}")
    _write_content(config, conversion_script, mapping, offset)


if __name__ == "__main__":
    main()
