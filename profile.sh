#!/usr/bin/env bash
set -e

usage()
{
    echo "Usage: $0 {new|run|rm} [profile]"
    echo "$0 new new_profile"
    echo "$0 run existing_profile"
    echo "$0 rm existing_profile"
}

if [ "$#" -ne 2 ]; then
    usage
    exit 1
fi

verb="$1"
profile="$2"
profile_dir=.profiles/$profile

new()
{
    echo "👩 Creating user $profile with password $profile on database $profile"
    mongo mongodb://localhost:27017/$profile --eval "db.createUser({user: "\""$profile"\"", pwd: "\""$profile"\"", roles: [{ role: "\""readWrite"\"", db: "\""$profile"\"" }]})"

    echo "🗄️ Creating profile dir for $profile"
    mkdir -p $profile_dir
    cat <<EOF > $profile_dir/.env
ADMIN_USERNAME=$profile
ADMIN_PASSWORD=$profile
JWT_SECRET_KEY=superdupersecret
MONGODB_CONNECTION_STRING=mongodb://$profile:$profile@localhost:27017/$profile
MONGODB_DB=$profile
DEFAULT_API_HANDLER_MODULE=
DEFAULT_API_HANDLER_CLASSNAME=
EOF
    touch $profile_dir/.workers.env
    touch $profile_dir/SERVER_PLUGIN.txt

    echo "🎉 Finished initializing $profile. Please fill in the following"
    echo "Line DEFAULT_API_HANDLER_MODULE= in file $profile_dir/.env"
    echo "Line DEFAULT_API_HANDLER_CLASSNAME= in file $profile_dir/.env"
    echo "File $profile_dir/.workers.env"
    echo "File $profile_dir/SERVER_PLUGIN.txt"
}

run()
{
    codebase_path=$(pwd)
    bpb_path=$codebase_path/broccoli-plugin-interface
    server_plugin_txt_path=$codebase_path/$profile_dir/SERVER_PLUGIN.txt
    env_path=$codebase_path/$profile_dir/.env
    workers_env_path=$codebase_path/$profile_dir/.workers.env

    echo "🗑️ Removing all packages in server pipenv"
    cd server
    rm -f temp_requirements.txt
    pipenv run pip freeze > temp_requirements.txt
    pipenv run pip uninstall -r temp_requirements.txt -y

    echo "📦 Installing base dependencies"
    pipenv install

    echo "📦 Installing server plugin for $profile"
    pipenv run pip install pip==18.1
    BPB_DEP_LINK=git+file:///$bpb_path#egg=broccoli_plugin_interface-0.1 pipenv run pip install -e $(cat $server_plugin_txt_path) --process-dependency-links

    echo "🥦 Running server for $profile"
    cp $env_path .env
    cp $workers_env_path .workers.env
    FLASK_ENV=development pipenv run python app.py
}

remove()
{
    echo "🗄️ Removing profile dir for $profile"
    rm -rf $profile_dir

    echo "💾 Dropping database $profile"
    mongo mongodb://localhost:27017/$profile -u $profile -p $profile --eval "db.dropDatabase()"
    
    echo "👩 Dropping user $profile"
    mongo mongodb://localhost:27017/$profile -u $profile -p $profile --eval "db.dropUser("\""$profile"\"")"
}

case $verb in
    new)
        new
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
