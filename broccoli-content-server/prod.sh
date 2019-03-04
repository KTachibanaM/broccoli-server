#!/usr/bin/env bash
set -e

cd ..
docker build -t broccoli/content-server -f content-server.Dockerfile .
cd ./broccoli-content-server
docker images broccoli/content-server
docker run \
    --env-file ./content_server.env \
    --env RPC_AMQP_HOSTNAME=host.docker.internal \
    --env CONTENT_SERVER_MONGODB_HOSTNAME=host.docker.internal \
    --publish 5000:5000 \
    broccoli/content-server
