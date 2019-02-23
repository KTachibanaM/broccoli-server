# herr-ashi
Herr あし, 大腿先生, 大腿君

The broccoli plugin for herr-ashi

## Prerequisites
* `Minio`
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

## Configure plugin installation
Append `-e ./../herr-ashi` to `PIP_INSTALLS` for worker manager and api server. See `Configure plugin installation` section in `README.md` in `broccoli` codebase for detail.

## Configure worker manager environment
* `cp herr_ashi/environment.sample.py herr_ashi/environment.py `
* Edit `herr_ashi/environment.py` so that
    * `S3_ACCESS_KEY` is populated with the Minio's pre-generated access key
    * `S3_SECRET_KEY` is populated with the Minio's pre-generated secret key
* Register a Twitter app [here](https://developer.twitter.com/en/apps/create)
    * Obtain the Twitter app's consumer key, consumer secret, access token key and access token secret
    * Populate `herr_ashi/environment.py` accordingly

## Configure worker manager environment injection
Append `herr_ashi` to `PIP_ENVIRONMENT_MODULES` for worker manager. See `Configure worker manager environment injection` section in `README.md` in `broccoli` codebase for detail.

## Configure api server
Set `DEFAULT_API_HANDLER_MODULE` as `herr_ashi.api_handlers.default_handler` and `DEFAULT_API_HANDLER_CLASSNAME` as `DefaultHandler`. See `Configure api server` section in `README.md` in `broccoli` codebase for detail.

## Configure broccoli
After you are running both the server, worker manager and api server, run
```bash
./configure.sh
```

## Development
* Reset Minio
```bash
dev/reset_minio.sh
```
