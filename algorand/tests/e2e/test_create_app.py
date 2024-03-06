import json
from lib.blockchain import Vote

def test_create_app(vote_app):
    (txid, app_id) = vote_app.create_app()
    # After 3 million blocks, according to algorand docs, a private blockchain node will begin to stall.
    assert app_id is not None and app_id > 0 and app_id < 3000000, "App ID should be positive and less than 3000000"
    print("Tx ID:", txid)
    print("Created new app-id:", app_id)
    return app_id
    # Add calls to other test methods here

if __name__ == "__main__":
    # Load the configuration file
    with open('tests/e2e/test-config.json', 'r') as file:
        config = json.load(file)

    # Accessing specific configuration data
    creator_mnemonic = config['creatorInfo']['mnemonic']
    algod_token = config['algodToken']
    algod_address = config['algodAddress']
    asset_id = config['assetId']

    vote_app_creator = Vote(algod_address, algod_token, asset_id, creator_mnemonic, creator_mnemonic)

    test_create_app(vote_app_creator)
