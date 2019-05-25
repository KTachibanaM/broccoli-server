#!/usr/bin/env bash
set -e

usage()
{
    echo "Usage: $0 {new|run|run_web|rm|rm_mongo} [profile]"
    echo "$0 new new_profile"
    echo "$0 run existing_profile"
    echo "$0 run_web existing_profile"
    echo "$0 rm existing_profile"
    echo "$0 rm_mongo existing_profile"
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
    touch $profile_dir/web.env.development.local
    touch $profile_dir/WEBLET.txt

    echo "🎉 Finished initializing $profile. Please fill in the following"
    echo "Line DEFAULT_API_HANDLER_MODULE= in file $profile_dir/.env"
    echo "Line DEFAULT_API_HANDLER_CLASSNAME= in file $profile_dir/.env"
    echo "File $profile_dir/.workers.env"
    echo "File $profile_dir/SERVER_PLUGIN.txt"
    echo "File $profile_dir/web.env.development.local"
    echo "File $profile_dir/WEBLET.txt"
}

run()
{
    codebase_path=$(pwd)
    bpi_path=$codebase_path/broccoli-plugin-interface
    server_plugin_txt_path=$codebase_path/$profile_dir/SERVER_PLUGIN.txt
    env_path=$codebase_path/$profile_dir/.env
    workers_env_path=$codebase_path/$profile_dir/.workers.env
    pushd server

    echo "🗑️ Removing all packages in server pipenv"
    rm -f temp_requirements.txt
    pipenv run pip freeze > temp_requirements.txt
    pipenv run pip uninstall -r temp_requirements.txt -y

    echo "📦 Installing base dependencies"
    pipenv install

    echo "📦 Installing server plugin for $profile"
    pipenv run pip install pip==18.1
    BPI_DEP_LINK=git+file:///$bpi_path#egg=broccoli_plugin_interface-0.1 pipenv run pip install -e $(cat $server_plugin_txt_path) --process-dependency-links

    echo "🥦 Running server for $profile"
    cp $env_path .env
    cp $workers_env_path .workers.env
    FLASK_ENV=development pipenv run python app.py

    popd
}

rm_profile_dir()
{
    echo "🗄️ Removing profile dir for $profile"
    rm -rf $profile_dir
}

rm_profile_dir_ask() {
    while true; do
        read -p "Do you want to remove profile dir for $profile [Y/y/N/n]?" yn
        case $yn in
            [Yy]* )
                rm_profile_dir
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
}

rm_mongo()
{
    echo "💾 Dropping database $profile"
    mongo mongodb://localhost:27017/$profile -u $profile -p $profile --eval "db.dropDatabase()"
    
    echo "👩 Dropping user $profile"
    mongo mongodb://localhost:27017/$profile -u $profile -p $profile --eval "db.dropUser("\""$profile"\"")"
}

rm_mongo_ask()
{
    while true; do
        read -p "Do you want to remove mongodb for $profile [Y/y/N/n]?" yn
        case $yn in
            [Yy]* )
                rm_mongo
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
}

run_web()
{
    codebase_path=$(pwd)
    web_env_path=$codebase_path/$profile_dir/web.env.development.local
    weblet_txt_path=$codebase_path/$profile_dir/WEBLET.txt
    pushd web

    echo "🗑️ Removing all packages"
    rm -rf node_modules
    rm package-lock.json

    echo "📦 Installing base packages"
    npm install

    echo "📦 Installing weblet for $profile"
    pushd $(cat $weblet_txt_path)
    npm link
    package_name=$(jq '.name' -r package.json)
    popd
    npm link $package_name

    echo "🌐 Running web for $profile"
    cp $web_env_path .env.development.local
    REACT_APP_WEBLET_MODULE=$package_name npm start

    popd
}

case $verb in
    new)
        new
        ;;
    run)
        run
        ;;
    run_web)
        run_web
        ;;
    rm_mongo)
        rm_mongo_ask
        ;;
    rm)
        rm_mongo_ask
        rm_profile_dir_ask
        ;;
    *)
        usage
        exit 1
esac
