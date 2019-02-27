# broccoli-worker-manager
The services that schedules workers that query and manipulate content on content server

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

## Run in development mode
```bash
./dev.sh
```
