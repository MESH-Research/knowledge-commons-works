#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of Knowledge Commons Works.
#  Copyright (C) 2024 Mesh Research.
#
# Knowledge Commons Works is based on InvenioRDM, and
# this file is based on code from InvenioRDM. InvenioRDM is
#   Copyright (C) 2020-2024 CERN.
#   Copyright (C) 2020-2024 Northwestern University.
#   Copyright (C) 2020-2024 T U Wien.
#
# InvenioRDM and Knowledge Commons Works are both free software;
# you can redistribute and/or modify them under the terms of the
# MIT License; see LICENSE file for more details.

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

# Always bring down docker services
function cleanup() {
    eval "$(uv run docker-services-cli down --env)"
}

# Check if any docker-compose projects are running
function check_docker_compose_running() {
    echo "Checking for running docker-compose projects..."

    # Get list of running containers that might be from docker-compose
    running_containers=$(docker ps --format "table {{.Names}}\t{{.Image}}" | grep -E "(postgres|redis|opensearch|rabbitmq|elasticsearch)" || true)

    if [ -n "$running_containers" ]; then
        echo "Warning: Found potentially conflicting containers running:"
        echo "$running_containers"
        echo ""
        echo "This might cause port conflicts with docker-services-cli."
        echo "Consider stopping any running docker-compose projects before continuing."
        echo ""
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborting. Please stop conflicting containers and try again."
            exit 1
        fi
    else
        echo "No conflicting containers detected."
    fi
}

# Check for arguments
# Note: "-k" would clash with "pytest"
keep_services=0
skip_translations=0
pytest_args=()
for arg in $@; do
	# from the CLI args, filter out some known values and forward the rest to "pytest"
	# note: we don't use "getopts" here b/c of some limitations (e.g. long options),
	#       which means that we can't combine short options (e.g. "./run-tests -Kk pattern")
	case ${arg} in
		-K|--keep-services)
			keep_services=1
			;;
		-S|--skip-translations)
			skip_translations=1
			;;
		*)
			pytest_args+=( ${arg} )
			;;
	esac
done

if [[ ${keep_services} -eq 0 ]]; then
	trap cleanup EXIT
fi

# Extract and compile translations from python files
if [[ ${skip_translations} -eq 0 ]]; then
	echo "Extracting translations from python files"
	uv run invenio-cli translations extract
	echo "Updating translations"
	uv run invenio-cli translations update
	echo "Compiling translations"
	uv run invenio-cli translations compile
else
	echo "Skipping translations compilation"
fi

# Build the documentation
echo "Building the documentation"
uv run sphinx-build -b html docs/source/ docs/build/

# Check for running docker-compose projects before starting services
check_docker_compose_running

# Start the services and get their environment variables
echo "Starting the services"
eval "$(uv run --env-file tests/.env docker-services-cli --filepath .venv/lib/python3.12/site-packages/docker_services_cli/docker-services.yml up --db ${DB:-postgresql} --cache ${CACHE:-redis} --search opensearch --mq ${MQ:-rabbitmq} --env)"

# Unset the environment variables that docker-services-cli set so that the values from tests/.env are used instead of those defaults from docker-services.yml
unset SQLALCHEMY_DATABASE_URI
unset INVENIO_SQLALCHEMY_DATABASE_URI

# Run mypy
echo "Running mypy on the site directory"
uv run mypy --config-file pyproject.toml site/


# Note: expansion of pytest_args looks like below to not cause an unbound
# variable error when 1) "nounset" and 2) the array is empty.
if [ ${#pytest_args[@]} -eq 0 ]; then
	echo "Running pytest"
	uv run --env-file tests/.env python -m pytest -vv -s --disable-warnings
else
	echo "Running pytest with additional arguments"
	uv run --env-file tests/.env python -m pytest ${pytest_args[@]} -s --disable-warnings
fi

tests_exit_code=$?
exit "$tests_exit_code"