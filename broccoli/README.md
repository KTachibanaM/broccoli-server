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
* `Minio`, for `herr-ashi`
    * Have a Minio server running at `localhost:9000`
        * macOS
        ```bash
        brew install minio
        brew services start minio
        ```
        * Debian and Ubuntu: Follow [this guide](https://www.digitalocean.com/community/tutorials/how-to-set-up-an-object-storage-server-using-minio-on-ubuntu-16-04). You only need to complete Steps 1, 2 and 3
    * Obtain the pre-generated access key and secret key
        * macOS:
            * The access key can be obtained by running
            ```bash
            cat /usr/local/var/minio/.minio.sys/config/config.json | jq ".credential.accessKey"
            ```
            * The secret key can be obtained by running
            ```bash
            cat /usr/local/var/minio/.minio.sys/config/config.json | jq ".credential.secretKey"
            ```
        * Debian and Ubuntu
            * The access key can be obtained by running
            ```bash
            cat /usr/local/share/minio/.minio.sys/config/config.json | jq ".credential.accessKey"
            ```
            * The secret key can be obtained by running
            ```bash
            cat /usr/local/share/minio/.minio.sys/config/config.json | jq ".credential.secretKey"
            ```
    * Make sure you configure and install [`mc`](https://github.com/minio/mc), the CLI for Minio
        * Modify the `~/.mc/config.json` so that `local` host is populated with the pre-generated` access key and secret key. For example:
        ```json
        {
            "version": "9",
            "hosts": {
                "local": {
                    "url": "http://localhost:9000",
                    "accessKey": "YOUR ACCESS KEY HERE",
                    "secretKey": "YOUR SECRET KEY HERE",
                    "api": "S3v4",
                    "lookup": "auto"
                }
            }
        }
        ```

## Install Python dependencies
```bash
pipenv install
```

## Configure environment for the services
```bash
cp api.sample.env api.env
cp server.sample.env server.env
cp worker_manager.sample.env worker_manager.env
```

## Configure environment for `herr-ashi` workers
```bash
cp worker_globals.sample.env worker_globals.env
```
* Edit `worker_globals.env` so that
    * `S3_ACCESS_KEY` is populated with the Minio's pre-generated access key
    * `S3_SECRET_KEY` is populated with the Minio's pre-generated secret key
* Register a Twitter app [here](https://developer.twitter.com/en/apps/create)
    * Obtain the Twitter app's consumer key, consumer secret, access token key and access token secret
    * Populate `worker_globals.env` accordingly

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

## Configure as `herr-ashi`
```bash
dev/configure.sh
```

## Development
* Reset all stateful components
```bash
dev/reset_state.sh
```
* Reset RabbitMQ
```bash
dev/reset_rabbit_mq.sh
```
* Reset MongoDB
```bash
dev/reset_mongo.sh
```
* Reset Minio
```bash
dev/reset_minio.sh
```
