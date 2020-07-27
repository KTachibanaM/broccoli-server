#!/usr/bin/env bash
set -e

usage()
{
    echo "Usage: $0 [instance_name] [schema_version]"
}

if [ "$#" -ne 2 ]; then
    usage
    exit 1
fi

instance_name="$1"
schema_version="$2"

echo "Creating user $instance_name with password $instance_name on database $instance_name"
# shellcheck disable=SC2140
mongo mongodb://localhost:27017/"$instance_name" --eval "db.createUser({user: "\""$instance_name"\"", pwd: "\""$instance_name"\"", roles: [{ role: "\""readWrite"\"", db: "\""$instance_name"\"" }]})"

echo "Creating schema_version collection with version $schema_version on database $instance_name"
# shellcheck disable=SC2140
mongo mongodb://localhost:27017/"$instance_name" --eval "db.createCollection("\""schema_version"\""); db.schema_version.insert({"\""v"\"": NumberInt($schema_version)})"
