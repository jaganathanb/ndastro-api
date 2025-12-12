#!/usr/bin/env bash
# build.sh - Render.com build script

set -o errexit

echo "Installing dependencies..."
pip install --upgrade pip
poetry install --no-dev

echo "Compiling translations..."
poetry run pybabel compile -d ndastro_api/locales

echo "Setup database configurations..."
poetry run pre-start 

echo "Running database migrations..."
poetry run db-migrate 

echo "Initializing database data..."
poetry run init-data

echo "Build completed successfully!"
