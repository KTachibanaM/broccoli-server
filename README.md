# broccoli-platform
🥦, a web content crawling and sorting platform

## Problem Statement
* I want to
    * Crawl content, such as images and texts, from "feeds" on the Internet, such as RSS, Twitter, some random webpage
    * Archive those content into a centralized repository
    * Process the content and attach extra attributes, such as extracting hash, width, height of an image, or translating a piece of text
    * Manage the content repository using a dashboard, such as viewing images and duplicates, or viewing texts and changing their translation
    * Expose the content repository to the world with certain attributes, such as "moderation is true"
* While I do not want to
    * Re-implement crawling resiliency and failure observability for different use cases
    * Specify different programming language object models for content in different use cases
    * Re-implement common elements in a management dashboard for different use cases

## Solution
This is a monolith web application that generalizes the crawling, processing, sorting and publishing of Internet content, while offer pluggability so that you customize it to fulfill individual use cases

## Pluggability
TBD

## Getting Started

### Prerequisites
* `Python 3.7`
* `pipenv`
* `Npde.js`
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

### Configure MongoDB
```bash
./scripts/init_mongo.sh my_first_broccoli
```
This script will create a database named `my_first_broccoli` with a user named `my_first_broccoli` with the password `my_first_broccoli` who has `readWrites` role to the database

### Run the service

#### Required environment
```env
ADMIN_USERNAME  # admin username used to authenticate API calls
ADMIN_PASSWORD  # admin password used to authenticate API calls
JWT_SECRET_KEY  # JWT secret key
MONGODB_CONNECTION_STRING  # MongoDB connection string
MONGODB_DB  # MongoDB database name
DEFAULT_API_HANDLER_MODULE  # module of the default API handler
DEFAULT_API_HANDLER_CLASSNAME  # class name of the default API handler
```
If you are running locally, you can copy `.env.sample` as `.env` and then edit `.env` in `server`

#### Optional environment for workers
You should also set additional environment variables for workers if the workers require

If you are running locally, you can copy `.workers.env.sample` as `.workers.env` and then edit `.workers.env` in `server`

#### Install dependencies
```bash
cd server
pipenv install
```

#### Install service plugin
* Configure your shell environment to include `BPI_DEP_LINK`
This is an environment variable that is needed in `setup.py` to find a local version of `broccoli-plugin-interface`, a Python package needed to develop broccoli plugins
In your `.zshrc` or `.bashrc`, add this line
`export BPB_DEP_LINK=git+file:///ABS_PATH_TO_BPB#egg=broccoli_plugin_interface-0.1`
Replace `ABS_PATH_TO_BPB` with the absolute path to the `broccoli-plugin-interface` directory in the `broccoli-platform` codebase
For example, on my development environment with `zsh`, the line looks like this in `.zshrc`
```bash
export BPI_DEP_LINK=git+file:///Users/username/Projects/broccoli-platform/broccoli-plugin-interface#egg=broccoli_plugin_interface-0.1
```
* Install the plugin
Assume the PyPI module name or Python module URL is `$PLUGIN`
```bash
cd server
pipenv run pip install pip==18.1
pipenv run pip install -e $PLUGIN --process-dependency-links
```
`$PLUGIN` might look something like `/Users/username/Projects/some-project/some-plugin`
* Uninstall the plugin
```bash
pipenv run pip freeze | grep -e
# figure about the Python module name of the plugin
pipenv run pip uninstall $THE_MODULE_NAME
```

#### Run
```bash
FLASK_ENV=development pipenv run python app.py
```

#### Run unit tests
```bash
pipenv run python -m unittest discover tests -v
```

### Run the web frontend

#### Optional environment
If you are running locally, you can create and edit `.env.development.local` in `web`

#### Install dependencies
```bash
cd web
npm install
```

#### Run
```bash
npm start
```

### Reset MongoDB
```bash
./scripts/reset_mongo.sh my_first_broccoli
```
