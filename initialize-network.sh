#!/bin/sh

# Create the network
goal network create -r /algod/data/net1 -n private -t my_network_template.json

# Start the network
goal network start -r /algod/data/net1

# Keep the container running
tail -f /dev/null
