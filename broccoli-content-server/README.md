# broccoli-content-server
The service that host the content and exposed RPC methods to query and manipulate them

## Prerequisites
* `Python 3.7`
* [`pipenv`](https://pipenv.readthedocs.io/en/latest/)

## Install dependencies
```bash
pipenv install
```

## Configure environment
```bash
cp content_server.sample.env content_server.env
# edit content_server.env  # TODO
```

## Run in development mode
```bash
./dev.sh
```
