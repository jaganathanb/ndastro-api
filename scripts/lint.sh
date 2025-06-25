#!/usr/bin/env bash

set -e
set -x

mypy ndastro_api
ruff check ndastro_api
ruff format ndastro_api --check
