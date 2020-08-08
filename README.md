# broccoli-server
[![Build Status](https://travis-ci.org/k-t-corp/broccoli-server.svg?branch=master)](https://travis-ci.org/k-t-corp/broccoli-server)
[![PyPI version](https://badge.fury.io/py/broccoli-server.svg)](https://badge.fury.io/py/broccoli-server)

A web content crawling and sorting library

## Problem Statement
* I want to
    * Crawl content (images, texts, etc) from feeds on the Internet (RSS, Twitter, or webpages that you define crawling methods with)
    * Process the contents and attach extra attributes, such as image hash, image width/height, or text translation
    * Manipulate the contents with dashboards, such as managing duplicate images, or adding texts translation
    * Expose the contents to the world with a certain attribute, such as only moderated images
* However, I don't want to, for different use cases
    * Re-implement resiliency and observability for content crawling and processing
    * Re-implement common frontend and backend elements in content manipulation dashboards

## Solution
This is a Python library that generalizes the crawling, processing, sorting and publishing of Internet content

It offers Python interfaces that you will plug in and register implementation that fulfills your individual use cases

An implementation should instantiate an `Application` object, plug in modules for the use cases, and run 3 processes

* The web server is responsible for serving a web UI, exposing contents, and manipulating the metadata for this implementation
* The clock process is responsible for triggering background work
* The worker process is responsible for executing background work

A demo implementation of the process architecture running on Heroku is WIP

## Concepts and Pluggability
* Content repository is a centralized place to store all of the contents in database rows
* Worker
    * A worker is a "cron" job object that runs periodically and probably reads/writes to content repository.
    * Worker modules are registered to your implementation at runtime.
    * Workers are instantiated using worker modules and run according to worker metadata which can changed at runtime through UI and API.
* Mod view
    * A mod view is an UI that allows end users to view and manipulate the content repository.
    * A mod view shows rows, each row corresponds to an entry in the content repository.
    * What rows to show, how many rows to show, in what order the rows are shown, are controlled by the metadata of each mod view which your implementation specifies.
    * A row have columns. What to show for each column is controlled by ModViewColumn classes ("class" as in OOP) which are registered to your implementation at runtime.
* API handler
    * An API handler is an object that handles public query traffic to the content repository in HTTP.
    * The API handler is registered to your implementation at runtime.
* Job
    * A job is the same as a worker except that it only runs once at user's discretion at runtime through UI and API

## Usage
In your implementation, do

```bash
pip install broccoli-server
```

## Prepare

### MongoDB
You need a MongoDB database with two users, one for regular data operations (e.g. reading/writing the content repository), another for database schema migrations

We will call the former `rw`, and the later `ddl`

You need to create a collection named `schema_version` in the database. The collection should have one document

```
{
    "v": <schema_version>
}
```

`<schema_version>` is the current database schema version for the version of this library you are using. It can be found using the following steps
1. Go to `./broccoli_server/utils/database_migration.py`
2. Find `self.upgrade_map`
3. Find the key with max value
4. Increment that max value by one, and the incremented value is `<schema_version>`

#### MongoDB for local development
You need to give your implementation a name. We will call it `foo_bar`

If you have an "OS-default" version of MongoDB installed, you likely will have an unauthenticated MongoDB running locally on `localhost:27017`

If that's the case, you can use a convenient dev script to create both the MongoDB database and users

Run `./scripts/bootstrap_mongodb.sh <foo_bar> <schema_version>` to create the appropriate MongoDB database and users for local development

### Redis
You need a Redis instance. For local development, if you have an "OS-default" version of Redis running on `localhost:6379` installed, it will suffice.

### Environment variables
The following environment variables are expected to be found for the application to run
* `ADMIN_USERNAME` is the username for the web application
* `ADMIN_PASSWORD` is the password for the web application
* `JWT_SECRET_KEY`
* `MONGODB_CONNECTION_STRING` is the connection string for MongoDB user `rw`
    * If you used `bootstrap_mongodb.sh`, the connection string will simply be `mongodb://foo_bar:foo_bar@localhost:27017/foo_bar`
* `MONGODB_ADMIN_CONNECTION_STRING` is the connection string for MongoDB user `ddl`
    * If you used `bootstrap_mongodb.sh`, the connection string will simply be `mongodb://foo_bar:foo_bar@localhost:27017/foo_bar`
* `MONGODB_DB` is the actual name of the MongoDB database (even if the connection string already contains the database, this variable is still expected)
* `REDIS_URL` is the URL to the Redis instance
* `REDIS_KEY_PREFIX` is a prefix for all Redis keys the library will need to use
* `INSTANCE_TITLE` is an optional string that indicates the identifier of the implementation. It cannot contain spaces. It will be displayed in the web UI.

## API
TODO

## Development
### Prerequisites
* `Python 3.7`

### Prepare virtualenv
```bash
python3 -m virtualenv venv
```

### Develop
```bash
source venv/bin/activate
python setup.py develop
```

### Test
```bash
source venv/bin/activate
python setup.py test
```
