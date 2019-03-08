#!/usr/bin/env bash
set -e

docker build -t broccoli/web .
docker images broccoli/web
docker run \
    --env-file ./.env.development.local \
    --env-file ./.env.development \
    --env REACT_APP_SERVER_HOSTNAME=host.docker.internal \
    --env REACT_APP_API_HOSTNAME=host.docker.internal \
    --env REACT_APP_WORKER_MANAGER_HOSTNAME=host.docker.internal \
    --env REACT_APP_S3_HOSTNAME=host.docker.internal \
    --publish 3000:5000 \
    broccoli/web
