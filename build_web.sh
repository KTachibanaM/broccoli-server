#!/usr/bin/env bash
set -e

echo "Checking and exporting required environment"
[ -z "$PUBLIC_URL" ] && echo "Need to set \$PUBLIC_URL" && exit 1;
[ -z "$REACT_APP_SERVER_URL" ] && echo "Need to set \$REACT_APP_SERVER_URL" && exit 1;
export PUBLIC_URL=$PUBLIC_URL
export REACT_APP_SERVER_URL=$REACT_APP_SERVER_URL

echo "Building web"
cd web
npm run build
cd ..

echo "Moving ./web/build to ./server/web_static"
rm -rf ./server/web_static
cp -r ./web/build ./server/web_static
