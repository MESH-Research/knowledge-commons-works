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
    eval "$(pipenv run docker-services-cli down --env)"
}

# Check for arguments
# Note: "-k" would clash with "pytest"
keep_services=0
pytest_args=()
for arg in $@; do
	# from the CLI args, filter out some known values and forward the rest to "pytest"
	# note: we don't use "getopts" here b/c of some limitations (e.g. long options),
	#       which means that we can't combine short options (e.g. "./run-tests -Kk pattern")
	case ${arg} in
		-K|--keep-services)
			keep_services=1
			;;
		*)
			pytest_args+=( ${arg} )
			;;
	esac
done

if [[ ${keep_services} -eq 0 ]]; then
	trap cleanup EXIT
fi

# python -m check_manifest --no-build-isolation
# python -m setup extract_messages --output-file /dev/null
# python -m sphinx.cmd.build -qnN docs docs/_build/html
eval "$(PIPENV_DOTENV_LOCATION=/Users/ianscott/Development/knowledge-commons-works/site/tests/.env pipenv run docker-services-cli up --db ${DB:-postgresql} --cache ${CACHE:-redis} --search opensearch --mq ${MQ:-rabbitmq} --env)"
# Note: expansion of pytest_args looks like below to not cause an unbound
# variable error when 1) "nounset" and 2) the array is empty.
if [ -z "pytest_args[@]" ]; then
	PIPENV_DOTENV_LOCATION=/Users/ianscott/Development/knowledge-commons-works/site/tests/.env pipenv run python -m pytest ${pytest_args[@]}
else
	PIPENV_DOTENV_LOCATION=/Users/ianscott/Development/knowledge-commons-works/site/tests/.env pipenv run python -m pytest -vv
fi
# python -m sphinx.cmd.build -qnN -b doctest docs docs/_build/doctest
tests_exit_code=$?
exit "$tests_exit_code"