#!/usr/bin/env bash
set -e

usage()
{
    echo "Usage: $0 [instance_name]"
}

if [ "$#" -ne 1 ]; then
    usage
    exit 1
fi

instance_name="$1"

echo "👩 Creating user $instance_name with password $instance_name on database $instance_name"
# shellcheck disable=SC2140
mongo mongodb://localhost:27017/"$instance_name" --eval "db.createUser({user: "\""$instance_name"\"", pwd: "\""$instance_name"\"", roles: [{ role: "\""readWrite"\"", db: "\""$instance_name"\"" }]})"
