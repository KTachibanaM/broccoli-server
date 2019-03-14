#!/usr/bin/env bash
set -e

echo "Checking required environment"
[ -z "$SERVER_PLUGIN" ] && echo "Need to set \$SERVER_PLUGIN" && exit 1;

echo "Installing $SERVER_PLUGIN"
pip install pip==18.1
pip install $SERVER_PLUGIN --process-dependency-links
