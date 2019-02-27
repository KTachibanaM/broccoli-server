#!/usr/bin/env bash
set -e

if [[ $# -eq 0 ]] ; then
    echo 'No argument'
    exit 1
fi

sudo rabbitmqadmin -V /$1 -f tsv -q list queues name | while read queue; do sudo rabbitmqadmin -V /$1 -q delete queue name=${queue}; done