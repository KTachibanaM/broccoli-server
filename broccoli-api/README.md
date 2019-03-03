# broccoli-api
The service that hosts boards and the external facing API

## Prerequisites
* `Python 3.7`
* `pip==18.1` (for `--process-dependency-links`)
* [`pipenv`](https://pipenv.readthedocs.io/en/latest/)

## Install dependencies
```bash
pipenv install
```

## Install plugins
```bash
pipenv run pip install pip==18.1
pipenv run pip install SOME_PLUGIN_PATH --process-dependency-links
```

## Configure environment
```bash
cp api.sample.env api.env
# edit api.env  # TODO
```

## Configure the default API handler
Edit `DEFAULT_API_HANDLER_MODULE` and `DEFAULT_API_HANDLER_CLASSNAME` in `api.env`
so that the Python class `f"{DEFAULT_API_HANDLER_MODULE}.{DEFAULT_API_HANDLER_CLASSNAME}"` will be used as the default api handler for the api server
For example
```env
DEFAULT_API_HANDLER_MODULE=some_broccoli_plugin.api_handlers
DEFAULT_API_HANDLER_CLASSNAME=SomeApiHandler
```
This will trigger the api server to use the Python class `some_broccoli_plugin.api_handlers.SomeApiHandler` as the api handler

## Run in development mode
```bash
./dev.sh
```
