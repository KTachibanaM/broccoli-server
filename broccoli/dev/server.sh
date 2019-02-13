#!/usr/bin/env bash
set -e

./dev/pre_flight
FLASK_ENV=development pipenv run python server.py
