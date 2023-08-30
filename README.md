[![codecov](https://codecov.io/gh/oamg/convert2rhel-analysis-script/graph/badge.svg?token=Q187FG2S5Z)](https://codecov.io/gh/oamg/convert2rhel-analysis-script)

# Convert2RHEL analysis script

Script to set up convert2rhel and run pre-conversion analysis on centos 7.

Goal of script is to print to stdout in specified format, the script itself is executed by [rhc-worker-script](https://github.com/oamg/rhc-worker-script), stdout is collected and send back to Insights Tasks UI.

Script must be compatible with python2. Tests are also written to work on python2 (with help of mock module)

**The stdout of script must**:
* be wrapped in separators:
    * `"### JSON START ###"`
    * `"### JSON END ###"`
* follow JSON spec:
    * TODO: Expected spec for Insights Tasks UI
        * where `report_json` conforms to expected output of `convert2rhel analysis`

## Local Development

### Requirements

* `virtualenv` - to run tests locally
* `pre-commit` - to run checks before each commit
* `make` - to use handy commands
    * `make install` - install pre-commit hooks and python virtual environment
    * `make test` - runs pytest
    * `make lint` - runs pylint
    * `make verify` - runs both lint and tests

### Run tests and lint

`make verify` is run as pre-commit hook and you can also run lint and/or tests manually.

```sh
# Python2
make tests
make lint
make verify
```
