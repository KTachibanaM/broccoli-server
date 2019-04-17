#!/usr/bin/env bash
set -e

usage()
{
    echo "Usage: $0 {init|run|rm} [profile]"
    echo "$0 init new_profile"
    echo "$0 run existing_profile"
    echo "$0 rm existing_profile"
}

if [ "$#" -ne 2 ]; then
    usage
    exit 1
fi

verb="$1"
profile="$2"

init()
{
    echo "👩 Creating user $profile with password $profile on database $profile"
    mongo mongodb://localhost:27017/$profile --eval "db.createUser({user: "\""$profile"\"", pwd: "\""$profile"\"", roles: [{ role: "\""readWrite"\"", db: "\""$profile"\"" }]})"
}

run()
{
    echo "Running $profile"
}

remove()
{
    echo "💾 Dropping database $profile"
    mongo mongodb://localhost:27017/$profile -u $profile -p $profile --eval "db.dropDatabase()"
    
    echo "👩 Dropping user $profile"
    mongo mongodb://localhost:27017/$profile -u $profile -p $profile --eval "db.dropUser("\""$profile"\"")"
}

case $verb in
    init)
        init
        ;;
    run)
        run
        ;;
    rm)
        remove
        ;;
    *)
        usage
        exit 1
esac
