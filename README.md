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
This is a set of services and webapps that generalize the crawling, processing, sorting and publishing of Internet content, while offer pluggability so that you customize it to fulfill individual use cases

## Components
* `server`: The backend server that serves the content repository. It exposes a set of RPC actions, via AMQP and HTTP, to query and manipulate the content repository
* `worker_manager`: The backend server that schedules and runs workers which query and manipulate the content repository. It exposes a declarative API for end users to schedule workers
* `api`: The backend server that hosts information about the content management dashboards. It additionally exposes a configurable selected portion of the content repository to the public Internet
* `broccoli-web`: The frontend webapp that mainly displays the content management dashboards and additionally offers the UI to schedule the workers

## Pluggability
TBD

## Getting Started

### Prerequisites
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

### Configure MongoDB
```bash
scripts/init_mongo.sh my_first_broccoli
```
This script will create a database named `my_first_broccoli` with a user named `my_first_broccoli` with the password `my_first_broccoli` who has `readWrites` role to the database

### Configure RabbitMQ
```bash
dev/init_rabbitmq.sh my_first_broccoli
```
This script will create a virtual host named `my_first_broccoli` with a user named `my_first_broccoli` with the password `my_first_broccoli` who has admin access to the virtual host

### Run the services
Follow `README.md`s in `broccoli-content-server`, `broccoli-worker-manager`, `broccoli-api` and `broccoli-web` **in order** to spawn up the services

### Reset MongoDB and RabbitMQ
* Reset RabbitMQ
```bash
dev/reset_rabbit_mq.sh my_first_broccoli
```
* Reset MongoDB
```bash
dev/reset_mongo.sh my_first_broccoli
```
* Reset both
```bash
dev/reset_state.sh my_first_broccoli
```
