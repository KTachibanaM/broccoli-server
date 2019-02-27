#!/usr/bin/env bash
set -e

FLASK_ENV=development pipenv run python content_server.py
