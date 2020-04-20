#!/usr/bin/env bash
set -e

pushd ./web
yarn install
yarn build
popd

rm -rf ./broccoli_server/web
mv ./web/build ./broccoli_server/web
