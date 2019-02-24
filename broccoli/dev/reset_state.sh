#!/usr/bin/env bash
set -e

if [[ $# -eq 0 ]] ; then
    echo 'No argument'
    exit 1
fi

echo "Resetting MongoDB for $1"
dev/reset_mongo.sh $1

echo "Resetting RabbitMQ for $1"
dev/reset_rabbitmq.sh $1
