#!/usr/bin/env bash
set -e

docker build -t broccoli/web .
docker images broccoli/web
docker run \
    --env-file ./.env.development.local \
    --env-file ./.env.development \
    --publish 3000:5000 \
    broccoli/web
