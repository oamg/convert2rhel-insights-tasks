[![codecov](https://codecov.io/gh/oamg/convert2rhel-worker-scripts/graph/badge.svg?token=Q187FG2S5Z)](https://codecov.io/gh/oamg/convert2rhel-worker-scripts)

# Convert2RHEL worker scripts

Scripts related to [convert2rhel](https://github.com/oamg/convert2rhel) to be run via [rhc-worker-script](https://github.com/oamg/rhc-worker-script) on Red Hat Insights.

Scripts themselves shouldn't have any additional requirements = they are relying on python standard library.

Structure of repository is following:

```txt
├── requirements.txt  # DEV requirements - tests & lint
├── schemas # All expected json outputs in the scripts stdouts
|   |   ...
│   └── preconversion_assessment_schema_1.1.json
├── scripts # All available scripts
|   |   ...
│   └── preconversion_assessment_script.py
└── tests
    |   ...
    └── preconversion_assessment  # Unit tests for given script
```

## Schemas

Currently there is given format of the scripts stdout that is expected to be parsed by the Red Hat Insights Task UI. This stdout is JSON structure wrapped between agreed on separators. Schemas of the JSONs for each script can be found in [schemas](schemas) folder.

* separators (common to all scripts):
    * `### JSON START ###`
    * `### JSON END ###`

## Scripts

### Pre-conversion assessment

Script itself and tests are written for `python 2.7`. Goal of script is to print to stdout in specified format, the script itself is executed by [rhc-worker-script](https://github.com/oamg/rhc-worker-script) as part of pre-conversion task, stdout is collected and send back to Insights Tasks UI.

* [JSON schema](schemas/preconversion_assessment_schema_1.0.json)
* [pre-conversion assessment script](scripts/preconversion_assessment_script.py)

## Local Development & Contributing

### Requirements

* `virtualenv` - to run tests locally
* `pre-commit` - to run checks before each commit, see hook in [.pre-commit-config.yml](./.pre-commit-config.yaml)
* `make` - to use handy commands

### Run tests and lint

```sh
make install # install pre-commit hooks and python virtualenv
make tests # run pytest
```
