#!/usr/bin/env bash
set -e

if [[ $# -eq 0 ]] ; then
    echo 'No argument'
    exit 1
fi

sudo rabbitmqctl add_user $1 $1
sudo rabbitmqctl add_vhost /$1
sudo rabbitmqctl set_permissions -p /$1 $1 ".*" ".*" ".*"
