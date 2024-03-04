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
    #assert global_state["Winner"] == "choiceA"

if __name__ == "__main__":
    algod_address = "http://127.0.0.1:8080"
    algod_token = "1fa5aed7ec723da8ec9abfb6396adbbb607dd95316f8277456ec7b65afeb3893"
    asset_id = 1653

    # Creator info
    creator_mnemonic = "twin pumpkin plastic stage fortune shallow melt betray ribbon receive claim enrich price exile absent avoid woman toilet print settle shiver inform rookie absorb unaware"

    # User1 Info
    user1_mnemonic = "brain rough jazz defy absent ability jeans much hire retire metal tragic fury culture stem beach farm upset relief stove sound comic bunker able exist"
    vote_app_creator = Vote(algod_address, algod_token, asset_id, creator_mnemonic, creator_mnemonic)
    app_id = test_create_app(vote_app_creator)

    # Initialize so user1 can opt in to asset
    vote_app_user1 = Vote(algod_address, algod_token, asset_id, user1_mnemonic, user1_mnemonic, app_id)

    vote_app_creator = Vote(algod_address, algod_token, asset_id, creator_mnemonic, creator_mnemonic, app_id)
    test_vote(vote_app_user1, [b"vote", b"choiceA", b"child-oid_a1"])
    test_vote(vote_app_creator, [b"vote", b"choiceB", b"child_oid_b1"])

