import json
import unittest
from lib.blockchain import Vote

# Voter 1 and 2 vote on seperate choices. Creator votes on choice Z and wins.

class TestVoteApp(unittest.TestCase):
    maxDiff = None

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
        """
        Test the voting mechanism with multiple user participation and voting on different choices.

        This test demonstrates and verifies the following:
        1. Multiple users (in this case, user1 and user2) participating in the voting process.
        2. Each user voting for a different choice. For instance:
           - User1 votes for 'choiceA' with additional arguments.
           - User2 votes for 'choiceB' with their respective arguments.
           - The creator of the vote app also participates in voting, choosing 'choiceZ'.
        3. After each vote, the method captures the final global state of the voting application.
        4. The test then asserts whether the final global state matches the expected state, ensuring 
           that votes are correctly tallied and reflected in the application's state.

        This test is critical for ensuring the application correctly handles multiple votes from different 
        users and accurately updates the global state according to these votes. It validates the application's 
        ability to manage diverse inputs and maintain a consistent and accurate state, which is fundamental 
        for the integrity of the voting process.
        """
        user1_mnemonic = self.config['user1Info']['mnemonic']
        user2_mnemonic = self.config['user2Info']['mnemonic']
        user3_mnemonic = self.config['user3Info']['mnemonic']
        app_id = self.vote_app_creator.create_app()[1]

        vote_app_user1 = Vote(self.config['algodAddress'], self.config['algodToken'], self.config['assetId'], user1_mnemonic, user1_mnemonic, app_id)
        vote_app_user2 = Vote(self.config['algodAddress'], self.config['algodToken'], self.config['assetId'], user2_mnemonic, user2_mnemonic, app_id)
        vote_app_user3 = Vote(self.config['algodAddress'], self.config['algodToken'], self.config['assetId'], user3_mnemonic, user3_mnemonic, app_id)

        vote_app_user1.optin()
        vote_app_user2.optin()
        vote_app_user3.optin()

        vote_app_user1.vote([b"vote", b"choiceA", b"child-oid_a1"])
        vote_app_user2.vote([b"vote", b"choiceB", b"child-oid_b1"])
        final_state = self.vote_app_creator.vote([b"vote", b"choiceZ", b"child-oid_z1"])

        self.assert_final_state(final_state)

    def assert_final_state(self, global_state):
        """
        Assert the final state of the application. This test compares the actual global state
        with the expected state to ensure correctness of the voting process.
        """
        expected_state = {
            'Creator': 'VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M',
            'TotalSupply': 1000000,
            'Winner': 'choiceZ',
            'WinnerRef': 'child-oid_z1',
            'OriginalVoter_choiceA': 'XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM',
            'OriginalVoter_choiceB': 'ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A',
            'OriginalVoter_choiceZ': 'VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M',
            'Vote_choiceA_XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM': 1,
            'Vote_choiceB_ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A': 1,
            'Vote_choiceZ_VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M': 1,
            'choiceA': 50000,
            'choiceB': 2500,
            'choiceZ': 877500,
            'choiceA_child': 'child-oid_a1',
            'choiceB_child': 'child-oid_b1',
            'choiceZ_child': 'child-oid_z1'
        }

        self.assertDictEqual(global_state, expected_state)

if __name__ == "__main__":
    unittest.main()

