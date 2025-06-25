#!/bin/sh -e
set -x

ruff check ndastro_api scripts --fix
ruff format ndastro_api scripts
