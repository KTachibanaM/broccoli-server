# broccoli
🥦, a web content crawling and sorting system

## Prerequisites
* `Python 3.7`
* `pipenv`
* `jq`
* `RabbitMQ`
    * Have an unauthenticated RabbitMQ running at `localhost:5672`
        * macOS
        ```bash
        brew install rabbitmq
        brew services start rabbitmq
        ```
        * Debian and Ubuntu: Follow [this guide](https://www.rabbitmq.com/install-debian.html)
    * To verify, run the following command and you should see strings like `Listing queues for vhost / ...`
    ```bash
    rabbitmqctl report
    ```
    * Create a admin user and enable web interface at `localhost:15672` using the following script
    ```bash
    dev/reset_rabbit_mq.sh
    ```
* `MongoDB`
    * Have an unauthenticated MongoDB running at `localhost:27017`
        * macOS
        ```bash
        brew install mongodb
        brew services start mongodb
        ```
        * Debian and Ubuntu: Follow [this guide](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)
    * To verify, run the `mongo` in your terminal and you should be dropped to a MongoDB interactive shell
* Come up with a name for the instance. From now on we assume that name is `my_first_broccoli`

## Install Python dependencies
```bash
pipenv install
```

## Configure MongoDB
* Create the Mongo database to contain data needed for this instance
    ```bash
    python dev/init_mongo.py my_first_broccoli
    ```
    This script will create a database named `my_first_broccoli` with a user named `my_first_broccoli` with the password `my_first_broccoli` who has `readWrites` role to the database

## Configure environment
```bash
cp api.sample.env api.env
cp server.sample.env server.env
cp worker_manager.sample.env worker_manager.env
```
Then in all `*.env` (not `*.sample.env`) files, fill
* `*_MONGODB_DB=my_first_broccoli`
* `*_MONGODB_USERNAME=my_first_broccoli`
* `*_MONGODB_PASSWORD=my_first_broccoli`
This basically tells the server, the worker manager and the api server to connect to the MongoDB database that we just created with `dev/init_mongo.sh my_first_broccoli`

## Configure plugin installation
Edit `PIP_INSTALLS` in `worker_manager.env` and `api.env` so that it contains a comma-separated list of Python packages that worker manager and api server will install using `pip`
For example
```env
PIP_INSTALLS=git+https://github.com/KTachibanaM/some_broccoli_plugin.git,-e ~/projects/some_other_broccoli_plugin
```
This will trigger worker manager and api server to run the following commands when they are started
```bash
pip install git+https://github.com/KTachibanaM/some_broccoli_plugin.git
pip install -e ~/projects/some_other_broccoli_plugin
```

## Configure worker manager environment injection
Edit `PIP_ENVIRONMENT_MODULES` in `worker_manager.env` so that it contains a comma-separated list of Python module names. The worker manager will attempt to find the string variable called `Environment` under the submodule `environment` for every enlisted module names, and load the strings as dotenv files
For example
```env
PIP_ENVIRONMENT_MODULES=some_broccoli_plugin,some_other_broccoli_plugin
```
This will trigger worker manager to find the string variable `Environment` under modules `some_broccoli_plugin.environment` and `some_other_broccoli_plugin.environment`, and load the string variables as dotenv files

## Configure api server
Edit `DEFAULT_API_HANDLER_MODULE` and `DEFAULT_API_HANDLER_CLASSNAME` in `api.env` so that the Python class `f"{DEFAULT_API_HANDLER_MODULE}.{DEFAULT_API_HANDLER_CLASSNAME}"` will be used as the api handler for api server
For example
```env
DEFAULT_API_HANDLER_MODULE=some_broccoli_plugin.api_handlers
DEFAULT_API_HANDLER_CLASSNAME=SomeApiHandler
```
This will trigger api server to use the Python class `some_broccoli_plugin.api_handlers.SomeApiHandler` as the api handler

## Run the server
Notice that Flask auto-reload sometimes doesn't work, so you might better off restart the process itself.
```bash
dev/server.sh
```

## Run the worker manager
Notice that Flask auto-reload sometimes doesn't work, so you might better off restart the process itself.
```bash
dev/worker_manager.sh
```

## Run the API server
Notice that Flask auto-reload sometimes doesn't work, so you might better off restart the process itself.
```bash
dev/api.sh
```

## Development
* Reset RabbitMQ
```bash
dev/reset_rabbit_mq.sh
```
* Reset MongoDB
```bash
dev/reset_mongo.sh my_first_broccoli
```
