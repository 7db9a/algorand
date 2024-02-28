from lib.blockchain.blockchain import Algorand

def run_tests(algorand):
    algorand.create_app()
    # Add calls to other test methods here

if __name__ == "__main__":
    algod_address = "http://127.0.0.1:8080"
    algod_token = "1fa5aed7ec723da8ec9abfb6396adbbb607dd95316f8277456ec7b65afeb3893"
    creator_mnemonic = "twin pumpkin plastic stage fortune shallow melt betray ribbon receive claim enrich price exile absent avoid woman toilet print settle shiver inform rookie absorb unaware"
    user_mnemonic = creator_mnemonic

    algorand = Algorand(algod_address, algod_token, creator_mnemonic, user_mnemonic)
    run_tests(algorand)
