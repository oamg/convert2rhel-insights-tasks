[![codecov](https://codecov.io/gh/oamg/convert2rhel-insights-tasks/graph/badge.svg?token=Q187FG2S5Z)](https://codecov.io/gh/oamg/convert2rhel-insights-tasks)

# Convert2RHEL Inights Tasks

Scripts related to [convert2rhel](https://github.com/oamg/convert2rhel) to be run via [rhc-worker-script](https://github.com/oamg/rhc-worker-script) on Red Hat Insights.

Scripts themselves shouldn't have any additional requirements = they are relying on python standard library.

Structure of repository is following:

```txt
├── requirements  # DEV requirements - tests & lint
│   └── ...
├── schemas # All expected json outputs in the scripts stdouts
|   |   ...
│   └── preconversion_assessment_schema_1.1.json
├── convert2rhel_insights_tasks # All available scripts
│   └── main.py
└── tests
    |   ...
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
* [pre-conversion assessment script](scripts/c2r_script.py)

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

### Syncing scripts

We have a script to sync the changes from convert2rhel_insights_tasks/main.py
to the appropriate yaml files (pre-analysis and conversion) in both
advisor-backend and rhc-worker-script.

To make it work, you need to first install the ruamel.yaml library through your
package manager, for example, if using Fedora or RHEL:

```
dnf install python3-ruamel-yaml
```

We sync the files to rhc-worker-script mostly on development or testing with
the following command:
```
make sync
```

While for the advisor-backend, we mainly want to sync after we do a new
release. So for that, only call this command if checked out to a tag after the
release.
```
make sync-advisor
```
