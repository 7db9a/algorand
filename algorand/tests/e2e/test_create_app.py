from lib.blockchain import Vote

def test_create_app(vote_app):
    (txid, app_id) = vote_app.create_app()
    assert app_id is not None and app_id > 0, "Failed to create application"
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
        'Creator': 'a82fe67e59c7badbc9802c5b4c1c60cab7bd79147e4aa77b70c800c43ea057c8',
        'TotalSupply': 1000000,
        'Winner': 'choiceZ',
        'OriginalVoter_choiceA': 'bb46ae84347088d6c61b2cf92848446942d9636163a9bb689933567fe47dcc80',
        '566f74655fbb46ae84347088d6c61b2cf92848446942d9636163a9bb689933567fe47dcc80': 'choiceA',
        'choiceA': 50000,
        'choiceA_child': 'child-oid_a1',
        '566f74655f22da946c854e0dd9fd7b2df24b01f4ad09ae529753a9002f30b5f1415a8cea78': 'choiceB',
        'OriginalVoter_choiceB': '22da946c854e0dd9fd7b2df24b01f4ad09ae529753a9002f30b5f1415a8cea78',
        'choiceB': 2500,
        'choiceB_child': 'child-oid_b1',
        'OriginalVoter_choiceZ': 'a82fe67e59c7badbc9802c5b4c1c60cab7bd79147e4aa77b70c800c43ea057c8',
        '566f74655fa82fe67e59c7badbc9802c5b4c1c60cab7bd79147e4aa77b70c800c43ea057c8': 'choiceZ',
        'choiceZ': 947500,
        'choiceZ_child': 'child_oid_z1',
    }
    assert global_state == expected_state

if __name__ == "__main__":
    algod_address = "http://127.0.0.1:8080"
    algod_token = "1fa5aed7ec723da8ec9abfb6396adbbb607dd95316f8277456ec7b65afeb3893"
    asset_id = 1653

    # Creator Info
    creator_mnemonic = "twin pumpkin plastic stage fortune shallow melt betray ribbon receive claim enrich price exile absent avoid woman toilet print settle shiver inform rookie absorb unaware"

    # User1 Info
    user1_mnemonic = "brain rough jazz defy absent ability jeans much hire retire metal tragic fury culture stem beach farm upset relief stove sound comic bunker able exist"

    # User2 Info
    user2_mnemonic = "mass slide nature lady river smart dismiss item cave topple place remember oxygen title travel mixture team focus live human burger knock achieve about giggle"

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

