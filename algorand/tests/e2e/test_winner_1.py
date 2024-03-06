import json
import unittest
from lib.blockchain import Vote

class TestVoteApp(unittest.TestCase):

    def setUp(self):
        # Load the configuration file and initialize common resources
        with open('tests/e2e/test-config.json', 'r') as file:
            self.config = json.load(file)

        algod_address = self.config['algodAddress']
        algod_token = self.config['algodToken']
        asset_id = self.config['assetId']
        creator_mnemonic = self.config['creatorInfo']['mnemonic']

        self.vote_app_creator = Vote(algod_address, algod_token, asset_id, creator_mnemonic, creator_mnemonic)

    def test_create_app(self):
        (txid, app_id) = self.vote_app_creator.create_app()
        self.assertIsNotNone(app_id)
        self.assertGreater(app_id, 0)
        self.assertLess(app_id, 3000000)

    def test_vote(self):
        user1_mnemonic = self.config['user1Info']['mnemonic']
        user2_mnemonic = self.config['user2Info']['mnemonic']
        app_id = self.vote_app_creator.create_app()[1]

        vote_app_user1 = Vote(self.config['algodAddress'], self.config['algodToken'], self.config['assetId'], user1_mnemonic, user1_mnemonic, app_id)
        vote_app_user2 = Vote(self.config['algodAddress'], self.config['algodToken'], self.config['assetId'], user2_mnemonic, user2_mnemonic, app_id)

        vote_app_user1.optin()
        vote_app_user2.optin()

        vote_app_user1.vote([b"vote", b"choiceA", b"child-oid_a1"])
        vote_app_user2.vote([b"vote", b"choiceB", b"child-oid_b1"])
        final_state = self.vote_app_creator.vote([b"vote", b"choiceZ", b"child_oid_z1"])

        self.assert_final_state(final_state)

    def assert_final_state(self, global_state):
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
        self.assertDictEqual(global_state, expected_state)

if __name__ == "__main__":
    unittest.main()

