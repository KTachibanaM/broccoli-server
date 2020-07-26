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

while true; do
    read -rp "Are you sure you want to remove mongodb for $instance_name [Y/y/N/n]?" yn
    case $yn in
        [Yy]* )
            echo "💾 Dropping database $instance_name"
            mongo mongodb://localhost:27017/"$instance_name" -u "$instance_name" -p "$instance_name" --eval "db.dropDatabase()"

            echo "👩 Dropping user $instance_name"
            # shellcheck disable=SC2140
            mongo mongodb://localhost:27017/"$instance_name" -u "$instance_name" -p "$instance_name" --eval "db.dropUser("\""$instance_name"\"")"
            break
            ;;
        [Nn]* )
            break
            ;;
        * )
            echo "Please answer [Y/y/N/n]"
            ;;
    esac
done