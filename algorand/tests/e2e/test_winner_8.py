import json
import unittest
from lib.blockchain import Vote

# Creator deletes Winner key.
# Voter 2 increments choice after Voter 1 initiates.

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
        algod_address = config['algodAddress']
        algod_token = config['algodToken']
        asset_id = config['assetId']

        cls.vote_app_creator = Vote(algod_address, algod_token, asset_id, creator_mnemonic, creator_mnemonic)
        cls.vote_app_user1 = Vote(algod_address, algod_token, asset_id, user1_mnemonic, user1_mnemonic)
        cls.vote_app_user2 = Vote(algod_address, algod_token, asset_id, user2_mnemonic, user2_mnemonic)

        app_id = cls.create_app(cls.vote_app_creator)
        cls.vote_app_user1.app_id = app_id
        cls.vote_app_user2.app_id = app_id

        cls.vote_app_user1.optin()
        cls.vote_app_user2.optin()

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
        self.vote_app_user1.vote([b"vote", b"choiceA", b"child-oid_a1"])
        self.vote_app_user2.vote([b"vote", b"choiceB", b"child-oid_b1"])
        self.vote_app_user2.vote([b"vote", b"choiceA", b"child-oid_b1"])
        winner_state = self.vote_app_creator.vote([b"vote", b"choiceZ", b"child_oid_z1"])

        # After the voting sequence
        final_state = self.vote_app_creator.delete_key([b"delete_key", b"Winner"])

        expected_winner_state = {
            'Creator': 'VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M',
            'TotalSupply': 1000000,
            'Winner': 'choiceZ',
            'OriginalVoter_choiceA': 'XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM',
            'OriginalVoter_choiceB': 'ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A',
            'OriginalVoter_choiceZ': 'VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M',
            'Vote_choiceA_XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM': 1,
            'Vote_choiceB_ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A': 1,
            'Vote_choiceA_ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A': 1,
            'Vote_choiceZ_VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M': 1,
            'choiceA': 52500,
            'choiceB': 2500,
            'choiceZ': 877500,
            'choiceA_child': 'child-oid_a1',
            'choiceB_child': 'child-oid_b1',
            'choiceZ_child': 'child_oid_z1'
        }

        expected_final_state = {
            'Creator': 'VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M',
            'TotalSupply': 1000000,
            'OriginalVoter_choiceA': 'XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM',
            'OriginalVoter_choiceB': 'ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A',
            'OriginalVoter_choiceZ': 'VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M',
            'Vote_choiceA_XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM': 1,
            'Vote_choiceB_ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A': 1,
            'Vote_choiceA_ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A': 1,
            'Vote_choiceZ_VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M': 1,
            'choiceA': 52500,
            'choiceB': 2500,
            'choiceZ': 877500,
            'choiceA_child': 'child-oid_a1',
            'choiceB_child': 'child-oid_b1',
            'choiceZ_child': 'child_oid_z1'
        }

        self.assertDictEqual(winner_state, expected_winner_state)
        self.assertDictEqual(final_state, expected_final_state)

if __name__ == "__main__":
    unittest.main()

