import os
import ruamel.yaml

# Scripts located in this project
SCRIPT_PATH = "convert2rhel_insights_tasks/main.py"

# Yaml playbooks in rhc-worker-script
PRE_CONVERSION_YAML_PATH = os.path.join(
    "..", "rhc-worker-script/development/nginx/data/convert2rhel_analysis.yml"
)
CONVERSION_YAML_PATH = os.path.join(
    "..", "rhc-worker-script/development/nginx/data/convert2rhel_conversion.yml"
)

DEFAULT_YAML_ENVELOPE = """
- name: Convert2RHEL
  vars:
    insights_signature: |
      ascii_armored gpg signature
    insights_signature_exclude: /vars/insights_signature,/vars/content_vars
    interpreter: /usr/bin/python
    content: |
      placeholder
    content_vars:
      # variables that will be handed to the script as environment vars
      # will be prefixed with RHC_WORKER_*
      CONVERT2RHEL_DISABLE_TELEMETRY: 1
      SCRIPT_MODE: type
"""


def _get_updated_yaml_content(yaml_path, script_path):
    if not os.path.exists(yaml_path):
        yaml = ruamel.yaml.YAML()
        config = yaml.load(DEFAULT_YAML_ENVELOPE)
        mapping = 2
        offset = 0
    else:
        config, mapping, offset = ruamel.yaml.util.load_yaml_guess_indent(
            open(yaml_path)
        )

    with open(script_path) as script:
        content = script.read()

    script_type = "ANALYSIS" if "analysis" in yaml_path else "CONVERSION"
    config[0]["name"] = "Convert2RHEL %s" % script_type.title()
    config[0]["vars"]["content"] = content
    config[0]["vars"]["content_vars"]["SCRIPT_MODE"] = script_type
    return config, mapping, offset


def _write_content(config, path, mapping=None, offset=None):
    yaml = ruamel.yaml.YAML()
    if mapping and offset:
        yaml.indent(mapping=mapping, sequence=mapping, offset=offset)
    with open(path, "w") as handler:
        yaml.dump(config, handler)


def main():
    config, mapping, offset = _get_updated_yaml_content(
        PRE_CONVERSION_YAML_PATH, SCRIPT_PATH
    )
    print("Writing new content to %s" % PRE_CONVERSION_YAML_PATH)
    _write_content(config, PRE_CONVERSION_YAML_PATH, mapping, offset)
    config, mapping, offset = _get_updated_yaml_content(
        CONVERSION_YAML_PATH, SCRIPT_PATH
    )
    print("Writing new content to %s" % CONVERSION_YAML_PATH)
    _write_content(config, CONVERSION_YAML_PATH, mapping, offset)


if __name__ == "__main__":
    main()
