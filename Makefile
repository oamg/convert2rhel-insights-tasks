.PHONY: \
	tests \
	lint \
	verify \
	install \
	sync \
	sync-advisor \
	image7 \
	tests7 \

# Project constants
IMAGE_REPOSITORY ?= ghcr.io
IMAGE_ORG ?= oamg
IMAGE_PREFIX ?= convert2rhel-insights-tasks
PYTHON_VERSION ?= 2
PYTHON = python$(PYTHON_VERSION)
PYTHON_VENV = venv$(PYTHON_VERSION)
PYTEST_ARGS ?= --cov -p no:cacheprovider
PYTEST_CALL = python -B -m pytest $(PYTEST_ARGS)
SHOW_CAPTURE ?= no
BUILD_IMAGES ?= 1

# Let the user specify PODMAN at the CLI, otherwise try to autodetect a working podman
ifndef PODMAN
	PODMAN := $(shell podman run --rm alpine echo podman 2> /dev/null)
	ifndef PODMAN
		DUMMY := $(warning podman is not detected. Majority of commands will not work. Please install and verify that podman --version works.)
	endif
endif

ifdef PODMAN
	CONTAINER_TEST_WARNING := "*** scripts directory will be read-only while tests are executing ***"
	CONTAINER_CLEANUP := podman unshare chown -R 0:0 $(shell pwd)
endif

ifdef KEEP_TEST_CONTAINER
	CONTAINER_RM =
else
	CONTAINER_RM = --rm
endif

WRITABLE_FILES=. .coverage coverage.xml
CONTAINER_TEST_FUNC=echo $(CONTAINER_TEST_WARNING) ; $(PODMAN) run -v $(shell pwd):/data:Z --name pytest-container -u root:root $(CONTAINER_RM) $(IMAGE)-$(1) /bin/sh -c 'touch $(WRITABLE_FILES) ; chown app:app $(WRITABLE_FILES) ; su app -c "$(PYTEST_CALL) $(2)"' ; CONTAINER_RETURN=$${?} ; $(CONTAINER_CLEANUP) ; exit $${CONTAINER_RETURN}

ifeq ($(BUILD_IMAGES), 1)
image7: .build-image7
IMAGE=$(IMAGE_ORG)/$(IMAGE_PREFIX)
else
image7: .fetch-image7
IMAGE=$(IMAGE_REPOSITORY)/$(IMAGE_ORG)/$(IMAGE_PREFIX)
endif

install-deps:
	virtualenv -p '$(PYTHON)' $(PYTHON_VENV); \
	. $(PYTHON_VENV)/bin/activate; \
	pip install --upgrade -r requirements/centos7.requirements.txt
	touch $@

pre-commit:
	pre-commit install --install-hooks
	touch $@

install: install-deps pre-commit

sync: install-deps
	python misc/sync_scripts.py worker

sync-advisor: install-deps
	python misc/sync_scripts.py advisor

.fetch-image7:
	@echo "Pulling $(IMAGE)-centos7"
	@$(PODMAN) pull $(IMAGE)-centos7

.build-image7:
	@$(PODMAN) build -f Containerfiles/centos7.Containerfile -t $(IMAGE)-centos7 .
	touch $@

tests7: image7
	@echo 'CentOS Linux 7 tests'
	@$(call CONTAINER_TEST_FUNC,centos7,--show-capture=$(SHOW_CAPTURE))
