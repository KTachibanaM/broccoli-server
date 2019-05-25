#!/usr/bin/env bash
set -e

echo "Checking and exporting required environment"
[ -z "$WEBLET_URL" ] && echo "Need to set \$WEBLET_URL" && exit 1;
[ -z "$PUBLIC_URL" ] && echo "Need to set \$PUBLIC_URL" && exit 1;
[ -z "$REACT_APP_SERVER_URL" ] && echo "Need to set \$REACT_APP_SERVER_URL" && exit 1;
[ -z "$REACT_APP_WEBLET_MODULE" ] && echo "Need to set \$REACT_APP_WEBLET_MODULE" && exit 1;
export PUBLIC_URL=$PUBLIC_URL
export REACT_APP_SERVER_URL=$REACT_APP_SERVER_URL
export REACT_APP_WEBLET_MODULE=$REACT_APP_WEBLET_MODULE

echo "Building web"
pushd ./web
yarn add $WEBLET_URL
npm run build
popd

echo "Moving ./web/build to ./server/web_static"
rm -rf ./server/web_static
cp -r ./web/build ./server/web_static
