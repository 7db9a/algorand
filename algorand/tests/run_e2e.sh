#!/bin/bash

# Compile vote contract app.
python contracts/vote_app/vote.py

# Bunde teal vote contract code for deployment
goal clerk compile vote_clear_state.teal -d /algod/data/net1/Primary
goal clerk compile vote_approval.teal -d /algod/data/net1/Primary
python -m tests.e2e.test_create_app
