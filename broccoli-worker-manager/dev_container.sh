#!/usr/bin/env bash
set -e

cd ..
docker build -t broccoli/worker-manager -f worker-manager.Dockerfile .
cd ./broccoli-worker-manager
docker images broccoli/worker-manager
docker run \
    --env-file ./worker_manager.env \
    --env-file ./workers.env \
    --env-file ./workers.container.env \
    --env-file ./dev_container.env \
    --env RPC_AMQP_HOSTNAME=host.docker.internal \
    --env WORKER_MANAGER_MONGODB_HOSTNAME=host.docker.internal \
    --publish 5002:5002 \
    broccoli/worker-manager
