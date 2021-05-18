#!/bin/bash

# This script builds and installs the
# Web API Manager browser extension.

set -e

# Make conda available to shell script
eval "$(conda shell.bash hook)"
conda activate openwpm

pushd openwpm/Extension/web-api-manager
npm install
npm run bundle
popd

echo "Success: Web API Manager has been built"
