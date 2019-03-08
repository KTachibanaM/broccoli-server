#!/usr/bin/env bash
set -e

cd ..
docker build -t broccoli/api -f api.Dockerfile .
cd ./broccoli-api
docker images broccoli/api
docker run \
    --env-file ./api.env \
    --env-file ./api.container.env \
    --env API_MONGODB_HOSTNAME=host.docker.internal \
    --env CONTENT_SERVER_HOSTNAME=host.docker.internal \
    --publish 5001:5001 \
    broccoli/api
