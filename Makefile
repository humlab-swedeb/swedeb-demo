include .env

.DEFAULT_GOAL=lint
SHELL := /bin/bash

SOURCE_FOLDERS=swedeb_demo tests
PACKAGE_FOLDER=swedeb_demo

PYTEST_ARGS=--durations=0 --cov=$(PACKAGE_FOLDER) --cov-report=xml --cov-report=html tests

RUN_TIMESTAMP := $(shell /bin/date "+%Y-%m-%d-%H%M%S")

release: ready guard-clean-working-repository bump.patch tag publish

ready: tools clean-dev tidy test lint requirements.txt build

build: requirements.txt-to-git
	@poetry build

publish:
	@poetry publish

lint: tidy pylint

tidy: black isort

tidy-to-git: guard-clean-working-repository tidy
	@status="$$(git status --porcelain)"
	@if [[ "$$status" != "" ]]; then
		@git add .
		@git commit -m "📌 make tidy"
		@git push
	fi

test: output-dir
	@poetry run pytest $(PYTEST_ARGS)  tests
	@rm -rf ./tests/output/*

output-dir:
	@mkdir -p ./tests/output

retest:
	@poetry run pytest $(PYTEST_ARGS) --last-failed tests

.ONESHELL: guard-clean-working-repository
guard-clean-working-repository:
	@status="$$(git status --porcelain)"
	@if [[ "$$status" != "" ]]; then
		echo "error: changes exists, please commit or stash them: "
		echo "$$status"
		exit 65
	fi

pylint:
	@poetry run pylint $(SOURCE_FOLDERS)

mypy:
	@poetry run mypy --version
	@poetry run mypy .

isort:
	@poetry run isort --profile black --float-to-top --line-length 120 --py 38 $(SOURCE_FOLDERS)

black: clean-dev
	@poetry run black --version
	@poetry run black --line-length 120 --target-version py38 --skip-string-normalization $(SOURCE_FOLDERS)

requirements.txt: poetry.lock
	@poetry export --without-hashes -f requirements.txt --output requirements.txt
	@git push

.PHONY: help init version
.PHONY: lint pylint mypy black isort tidy
.PHONY: test
.PHONY: ready build release
