

## Install Python dependencies
```bash
pipenv install
```

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
* `RPC_AMQP_VHOST=/my_first_broccoli`
* `RPC_AMQP_USERNAME=my_first_broccoli`
* `RPC_AMQP_PASSWORD=my_first_broccoli`
This basically tells the server, the worker manager and the api server to
* Connect to the MongoDB database that we just created with `dev/init_mongo.sh my_first_broccoli`
* Connect to the RabbitMQ virtual host that we just created with `dev/init_rabbitmq.sh my_first_broccoli`

## Configure plugin installation
Edit `PIP_INSTALLS` in `worker_manager.env` and `api.env` so that it contains a comma-separated list of Python packages that worker manager and api server will install using `pip`
For example
```env
PIP_INSTALLS=git+https://github.com/KTachibanaM/some_broccoli_plugin.git#egg_info=some_broccoli_plugin-0.1,-e ~/projects/some_other_broccoli_plugin
```
This will trigger worker manager and api server to run the following commands when they are started
```bash
pip install git+https://github.com/KTachibanaM/some_broccoli_plugin.git##egg_info=some_broccoli_plugin-0.1
pip install -e ~/projects/some_other_broccoli_plugin
```
**WARNING**: We current implicitly depend on `broccoli-plugin-base` in this codebase so that we don't have to handle transient dependency for plugins explicitly. This is not ideal but a must workaround.

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


