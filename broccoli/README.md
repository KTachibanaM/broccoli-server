# Broccoli

🥦, a web content crawling and sorting system

## Prerequisites
* `Python 3.7`
* `pipenv`
* `jq`
* `RabbitMQ`
    * Follow [this guide](https://www.rabbitmq.com/install-debian.html) to have an unauthenticated RabbitMQ running at `localhost:5672`
    * If you are not on Ubuntu, ensure to have an unauthenticated RabbitMQ running at `localhost:5672`
    * Create a admin user and enable web interface at `localhost:15672`

    ```bash
    dev/reset_rabbit_mq.sh
    ```

* `MongoDB`
    * Follow [this guide](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/) to have an unauthenticated MongoDB running at `localhost:27017`
    * If you are not on Ubuntu, ensure to have an unauthenticated MongoDB running at `localhost:27017`

* `Minio`
    * Follow [this guide](https://www.digitalocean.com/community/tutorials/how-to-set-up-an-object-storage-server-using-minio-on-ubuntu-16-04) to have a Minio server running at `localhost:9000`
        * You only need to complete Steps 1, 2 and 3
        * The access key can be obtained by running

        ```bash
        cat /usr/local/share/minio/.minio.sys/config/config.json | jq ".credential.accessKey"
        ```

        * The secret key can be obtained by running

        ```bash
        cat /usr/local/share/minio/.minio.sys/config/config.json | jq ".credential.secretKey"
        ```
    * If you are on macOS
        * The access key can be obtained by running

        ```bash
        cat /usr/local/var/minio/.minio.sys/config/config.json | jq ".credential.accessKey"
        ```

        * The secret key can be obtained by running

        ```bash
        cat /usr/local/var/minio/.minio.sys/config/config.json | jq ".credential.secretKey"
        ```
    * If you are not on Ubuntu, ensure to have a Minio server running at `localhost:9000` and you know its access key and secret key
    * Make sure you configure and install [`mc`](https://github.com/minio/mc), the CLI for Minio
        * Modify the `~/.mc/config.json` so that `local` host is filled with `accessKey` and `secretKey`

        ```json
        {
            "version": "9",
            "hosts": {
                    "local": {
                            "url": "http://localhost:9000",
                            "accessKey": "your access key here",
                            "secretKey": "your secret key here",
                            "api": "S3v4",
                            "lookup": "auto"
                    }
            }
        }
        ```

## Install dependencies
```bash
pipenv install
```

## Configure workers environment

Environment variables needed to run the workers are

* `S3_ENDPOINT_URL`: url to your S3 instance, Amazon, Google, Minio, etc
* `S3_REGION`: S3 region
* `S3_ACCESS_KEY`: S3 access key
* `S3_SECRET_KEY`: S3 secret key

### Either use `workers.env` file to inject the environment variables

```bash
cp workers.sample.env workers.env
vi workers.env  # edit this to fill the environment variables
```

### Or inject the environment variables at runtime

## Run server
```bash
dev/server.sh
```

## Run workers
```bash
dev/workers.sh
```

## Add some example workers
```bash
dev/add_example_workers.sh
```

## Development
* Reset everything

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