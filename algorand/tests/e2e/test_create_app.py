import json
import unittest
from lib.blockchain import Vote

class TestVoteApp(unittest.TestCase):

    def setUp(self):
        # Load the configuration file
        with open('tests/e2e/test-config.json', 'r') as file:
            config = json.load(file)

        # Accessing specific configuration data
        creator_mnemonic = config['creatorInfo']['mnemonic']
        algod_token = config['algodToken']
        algod_address = config['algodAddress']
        asset_id = config['assetId']

        # Initialize the Vote instance
        self.vote_app = Vote(algod_address, algod_token, asset_id, creator_mnemonic, creator_mnemonic)

    def test_create_app(self):
        # Use the initialized vote_app in the test
        (txid, app_id) = self.vote_app.create_app()
        self.assertIsNotNone(app_id, "App ID should not be None")
        self.assertGreater(app_id, 0, "App ID should be greater than 0")
        self.assertLess(app_id, 3000000, "App ID should be less than 3000000")
        print("Tx ID:", txid)
        print("Created new app-id:", app_id)

if __name__ == "__main__":
    unittest.main()

