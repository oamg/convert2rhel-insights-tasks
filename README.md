[![codecov](https://codecov.io/gh/oamg/convert2rhel-analysis-script/graph/badge.svg?token=Q187FG2S5Z)](https://codecov.io/gh/oamg/convert2rhel-analysis-script)

# Convert2RHEL worker scripts

Scripts related to [convert2rhel](https://github.com/oamg/convert2rhel) to be run via [rhc-worker-script](https://github.com/oamg/rhc-worker-script) on Red Hat Insights.

Scripts themselves shouldn't have any additional requirements = they are relying on python standard library.

Structure of repository is following:

```txt
├── requirements.txt  # DEV requirements - tests & lint
├── scripts # All available scripts
|   |   ...
│   └── preconversion_assessment_script.py
└── tests
    |   ...
    └── preconversion_assessment  # Unit tests for given script
```
## Scripts

### Pre-conversion assessment

Script and tests written for `python 2.7`. Goal of script is to print to stdout in specified format, the script itself is executed by [rhc-worker-script](https://github.com/oamg/rhc-worker-script) as part of pre-conversion task, stdout is collected and send back to Insights Tasks UI.


**The stdout of script must**:
* be wrapped in separators:
    * `### JSON START ###`
    * `### JSON END ###`
* follow JSON spec:
    * TODO: Expected spec for Insights Tasks UI
        * where `report_json` conforms to expected output of `convert2rhel analysis`

## Local Development & Contributing

### Requirements

* `virtualenv` - to run tests locally
* `pre-commit` - to run checks before each commit, see hook in [.pre-commit-config.yml](./.pre-commit-config.yaml)
* `make` - to use handy commands

### Run tests and lint

```sh
make install # install pre-commit hooks and python virtualenv
make tests # run pytest
make lint # run pylint
make verify # run both pylint and pytest
```
