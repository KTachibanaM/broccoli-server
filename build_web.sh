#!/usr/bin/env bash
set -e

echo "Checking and exporting required environment"
[ -z "$PUBLIC_URL" ] && echo "Need to set \$PUBLIC_URL" && exit 1;
[ -z "$REACT_APP_SERVER_URL" ] && echo "Need to set \$REACT_APP_SERVER_URL" && exit 1;
[ -z "$WEBLET_GIT" ] && echo "Need to set \$WEBLET_GIT" && exit 1;
[ -z "$WEBLET_SUBDIR" ] && echo "Need to set \$WEBLET_SUBDIR" && exit 1;
export PUBLIC_URL=$PUBLIC_URL
export REACT_APP_SERVER_URL=$REACT_APP_SERVER_URL

echo "Installing weblet"
pushd ./web
rm -rf weblet
git clone $WEBLET_GIT weblet
pushd ./weblet
rm -rf .git
pushd $WEBLET_SUBDIR
npm link
PACKAGE_NAME=$(jq '.name' -r package.json)
popd
popd

echo "Building web"
npm install --no-save ./weblet/$WEBLET_SUBDIR
REACT_APP_WEBLET_MODULE=$PACKAGE_NAME npm run build
popd

echo "Moving ./web/build to ./server/web_static"
rm -rf ./server/web_static
cp -r ./web/build ./server/web_static
