.PHONY: build

SHELL := $(shell type bash | cut -d\  -f3)
POETRY_PATH := $(shell type poetry 2>/dev/null | cut -d\  -f3)
PROJECT_DIR := $(shell realpath .)

VIRTUAL_ENV ?= $(shell poetry env info -p 2>/dev/null || find . -type d -name '*venv' -exec realpath {} \;)
PYTHON_VERSION := $(shell cat .python-version 2>/dev/null || python3 -V | sed "s,.* \(3\.[0-9]\+\)\..*,\1,")

DISTRO_DIR ?= distro

ifneq ($(shell echo "${MAKECMDGOALS}" | grep -q -E '^(env-setup|distro)$$' && echo noenv || echo isdev), noenv)
$(shell eval run=dev python setup/dotenv-from-toml.py > .env)
include .env
endif


env-info:
	@echo -e """\
	Application: ${APP_NAME} v${APP_VERSION}\n\
	Project: ${PROJECT_NAME} (${PROJECT_DESCRIPTION})\n\
	Source files: ${PROJECT_DIR}/${SRC_DIR}\n\
	Virtual env: ${VIRTUAL_ENV}\n\
	Current Python: ${PYTHON_VERSION}\n\
	""" | sed "s,: ,:|,;s,^\t,," | column -t -s\|

env-setup:
	@[ -f .python-version ] && poetry env use $(shell cat .python-version) >/dev/null || true
	@poetry install --no-root -v
	@poetry run pre-commit install
	@sed -i "/^INSTALL_PYTHON=.*/a PATH=${POETRY_PATH}:\$$INSTALL_PYTHON/bin:\$$PATH" .git/hooks/pre-commit

test-unit:
	PYTHONPATH=${SRC_DIR} poetry run python -m pytest tests/unit --exitfirst --verbose  # --capture=no

test-unit-coverage:
	@PYTHONPATH=${SRC_DIR} poetry run python -m pytest tests/ --cov --cov-branch --cov-report term-missing

run:
	echo TBD


distro:
	echo TBD


test-repl:
	PYTHONPATH=${SRC_DIR} poetry run python


toss-src-cache:
	@find . -type d -name .pytest_cache | xargs rm -rf
	@find . -type d -name __pycache__ | xargs rm -rf

toss-distros:
	@rm -fr ${DISTRO_DIR}

toss-all: toss-src-cache toss-distros
