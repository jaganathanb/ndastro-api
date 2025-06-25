#!/usr/bin/env bash

set -e
set -x

export ENV_FILE=.env.test

coverage run --source=ndastro_api -m pytest
coverage report --show-missing
coverage html --title "${@-coverage}"
