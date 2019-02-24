#!/usr/bin/env bash
set -e

if [[ $# -eq 0 ]] ; then
    echo 'No argument'
    exit 1
fi

mongo $1 --eval "db.createUser({user: "\""$1"\"", pwd: "\""$1"\"", roles: [{ role: "\""readWrite"\"", db: "\""$1"\"" }]})"