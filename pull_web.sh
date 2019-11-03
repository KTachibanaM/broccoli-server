#!/usr/bin/env bash
set -e

rm -f web.tar.gz
curl -O -L https://github.com/broccoli-platform/broccoli-web/releases/download/"$(cat WEB_VERSION.txt)"/web.tar.gz

rm -rf broccoli_server/web
mkdir -p broccoli_server/web
tar xzf web.tar.gz -C broccoli_server/web
