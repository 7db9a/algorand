from lib.blockchain import Vote

def test_vote(algorand):
    app_id = algorand.vote()
    assert app_id is not None and app_id > 0, "Failed to create application"
    print("Created new app-id:", app_id)
    # Add calls to other test methods here


def run_tests(algorand):
    test_create_app(algorand)

if __name__ == "__main__":
    algod_address = "http://127.0.0.1:8080"
    algod_token = "1fa5aed7ec723da8ec9abfb6396adbbb607dd95316f8277456ec7b65afeb3893"
    creator_mnemonic = "twin pumpkin plastic stage fortune shallow melt betray ribbon receive claim enrich price exile absent avoid woman toilet print settle shiver inform rookie absorb unaware"
    user_mnemonic = creator_mnemonic

    algorand = Vote(algod_address, algod_token, creator_mnemonic, user_mnemonic)
    run_tests(algorand)
