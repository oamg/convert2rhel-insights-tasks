import os
import ruamel.yaml

# Scripts located in this project
PRE_CONVERSION_SCRIPT_PATH = "scripts/preconversion_assessment_script.py"
CONVERSION_SCRIPT_PATH = "scripts/conversion_script.py"

# Yaml playbooks in rhc-worker-script
PRE_CONVERSION_YAML_PATH = os.path.join(
    "..", "rhc-worker-script/development/nginx/data/convert2rhel_analysis.yml"
)
CONVERSION_YAML_PATH = os.path.join(
    "..", "rhc-worker-script/development/nginx/data/convert2rhel_conversion.yml"
)


def _get_updated_yaml_content(yaml_path, script_path):
    config, mapping, offset = ruamel.yaml.util.load_yaml_guess_indent(open(yaml_path))
    with open(script_path) as script:
        content = script.read()

    config[0]["vars"]["content"] = content

    return config, mapping, offset


def _write_content(config, path, mapping, offset):
    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=mapping, sequence=mapping, offset=offset)
    with open(path, "w") as handler:
        yaml.dump(config, handler)


def main():
    config, mapping, offset = _get_updated_yaml_content(
        PRE_CONVERSION_YAML_PATH, PRE_CONVERSION_SCRIPT_PATH
    )
    print("Writing new content to %s" % PRE_CONVERSION_YAML_PATH)
    _write_content(config, PRE_CONVERSION_YAML_PATH, mapping, offset)
    config, mapping, offset = _get_updated_yaml_content(
        CONVERSION_YAML_PATH, CONVERSION_SCRIPT_PATH
    )
    print("Writing new content to %s" % CONVERSION_YAML_PATH)
    _write_content(config, CONVERSION_YAML_PATH, mapping, offset)


if __name__ == "__main__":
    main()
