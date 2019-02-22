# local-pypi
Run a PyPi server locally to host broccoli plugins

## Prerequisites
* `docker`

## Run once
```bash
mkdir -p ~/.local/share/broccoli-local-pypi/srv/pypi
touch ~/.local/share/broccoli-local-pypi/srv/pypi/.htpasswd
```

## Run the server
```bash
./run.sh
```
The server is now blocking
