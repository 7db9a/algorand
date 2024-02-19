#!/bin/bash

# Create the new directory structure
mkdir -p algorand/configs
mkdir -p algorand/experiments/namespace_app
mkdir -p algorand/scripts
mkdir -p docs
mkdir -p util

# Move config files
mv algorand_configs/config.json algorand/configs/
mv my_network_template.json algorand/configs/

# Move Dockerfile
mv Dockerfile algorand/

# Move experiment scripts and namespace app files
mv experiments/check_api_sdk.py algorand/experiments/
mv experiments/create_account_multisig.py algorand/experiments/
mv experiments/create_account.py algorand/experiments/
mv experiments/create_asset.py algorand/experiments/
mv experiments/hello_world.teal algorand/experiments/
mv experiments/namespace_deploy_log.txt algorand/experiments/namespace_app/
mv experiments/namespace_deploy.py algorand/experiments/namespace_app/
mv experiments/namespace.py algorand/experiments/namespace_app/
mv experiments/namespace_read_global_state.py algorand/experiments/namespace_app/
mv experiments/simple_app_and_deploy.py algorand/experiments/
mv experiments/simple_app.py algorand/experiments/
mv experiments/status.py algorand/experiments/
mv experiments/test_api.py algorand/experiments/

# Move network initialization and scripts
mv initialize-network.sh algorand/
mv scripts/start-network.sh algorand/scripts/

# Move utility script
mv util.py util/

# Move documentation files
mv docs/intro.md docs/
mv docs/namespace-app.md docs/

# Remove old directories
rm -rf algorand_configs
rm -rf experiments
rm -rf scripts

# Print a completion message
echo "Files reorganized successfully."

