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

def test_vote(vote_app, app_args):
    global_state = vote_app.vote(app_args)
    print(global_state)

    return global_state

def assert_final_state(global_state):
    expected_state = {
        'Creator': 'VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M',
        'TotalSupply': 1000000,
        'Winner': 'choiceZ',
        'OriginalVoter_choiceA': 'XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM',
        'OriginalVoter_choiceB': 'ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A',
        'OriginalVoter_choiceZ': 'VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M',
        'Vote_XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM': 'choiceA',
        'Vote_ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A': 'choiceB',
        'Vote_VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M': 'choiceZ',
        'choiceA': 50000,
        'choiceB': 2500,
        'choiceZ': 947500,
        'choiceA_child': 'child-oid_a1',
        'choiceB_child': 'child-oid_b1',
        'choiceZ_child': 'child_oid_z1'
    }

    assert global_state == expected_state

if __name__ == "__main__":
    # Load the configuration file
    with open('tests/e2e/test-config.json', 'r') as file:
        config = json.load(file)

    # Accessing specific configuration data
    creator_mnemonic = config['creatorInfo']['mnemonic']
    user1_mnemonic = config['user1Info']['mnemonic']
    user2_mnemonic = config['user2Info']['mnemonic']
    algod_address = config['algodAddress']
    algod_token = config['algodToken']
    asset_id = config['assetId']

    vote_app_creator = Vote(algod_address, algod_token, asset_id, creator_mnemonic, creator_mnemonic)

    app_id = test_create_app(vote_app_creator)

    # Initialize so user1 can opt in to asset
    vote_app_user1 = Vote(algod_address, algod_token, asset_id, user1_mnemonic, user1_mnemonic, app_id)

    # Initialize so user1 can opt in to asset
    vote_app_user2 = Vote(algod_address, algod_token, asset_id, user2_mnemonic, user2_mnemonic, app_id)

    vote_app_user1.optin()
    vote_app_user2.optin()

    test_vote(vote_app_user1, [b"vote", b"choiceA", b"child-oid_a1"])
    test_vote(vote_app_user2, [b"vote", b"choiceB", b"child-oid_b1"])
    final_state = test_vote(vote_app_creator, [b"vote", b"choiceZ", b"child_oid_z1"])

    assert_final_state(final_state)

