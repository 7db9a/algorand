import json
import unittest
from lib.blockchain import Vote

# don't trigger exclusive vote

class TestVoteApp(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        # Load the configuration file once for all tests
        with open('tests/e2e/test-config.json', 'r') as file:
            config = json.load(file)

        creator_mnemonic = config['creatorInfo']['mnemonic']
        user1_mnemonic = config['user1Info']['mnemonic']
        user2_mnemonic = config['user2Info']['mnemonic']
        user3_mnemonic = config['user3Info']['mnemonic']
        algod_address = config['algodAddress']
        algod_token = config['algodToken']
        asset_id = config['assetId']

        cls.vote_app_creator = Vote(algod_address, algod_token, asset_id, creator_mnemonic, creator_mnemonic)
        cls.vote_app_user1 = Vote(algod_address, algod_token, asset_id, user1_mnemonic, user1_mnemonic)
        cls.vote_app_user2 = Vote(algod_address, algod_token, asset_id, user2_mnemonic, user2_mnemonic)
        cls.vote_app_user3 = Vote(algod_address, algod_token, asset_id, user3_mnemonic, user3_mnemonic)

        app_id = cls.create_app(cls.vote_app_creator)
        cls.vote_app_user1.app_id = app_id
        cls.vote_app_user2.app_id = app_id
        cls.vote_app_user3.app_id = app_id

        cls.vote_app_user1.optin()
        cls.vote_app_user2.optin()
        cls.vote_app_user3.optin()

    @staticmethod
    def create_app(vote_app):
        (txid, app_id) = vote_app.create_app()
        assert app_id is not None and app_id > 0 and app_id < 3000000, "App ID should be positive and less than 3000000"
        print("Tx ID:", txid)
        print("Created new app-id:", app_id)
        return app_id

    def test_vote_multiple_users(self):
        """
        Test to prove that a choice can be incremented by multiple voters.
        This test involves three voting transactions by different users
        and verifies the final state of the voting application.
        """
        #self.vote_app_user1.vote([b"vote", b"choiceA", b"child-oid_a1"])
        self.vote_app_user2.vote([b"vote", b"choiceA", b"child-oid_a1"])
        final_state = self.vote_app_user3.vote([b"vote", b"choiceA", b"child-oid_a1"])

        expected_state = {
            'Creator': 'VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M',
            'TotalSupply': 1000000,
            'OriginalVoter_choiceA': 'ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A',
            'Vote_choiceA_ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A': 1,
            'Vote_choiceA_CSNFGTZI47Q52ZUI6SHTTCYO2YX7VHWUSYRXJYSPIHXST5E5KLZQNNHVLY': 1,
            'choiceA': 72500,
            'choiceA_child': 'child-oid_a1',
        }

        self.assertDictEqual(final_state, expected_state)

if __name__ == "__main__":
    unittest.main()

