#!/usr/bin/env bash
set -e

if [[ $# -eq 0 ]] ; then
    echo 'No argument'
    exit 1
fi

mongo $1 -u $1 -p $1 --eval "db.getCollectionNames().forEach(function(c) { if (c.indexOf("\""system."\"") == -1) db[c].drop(); })"