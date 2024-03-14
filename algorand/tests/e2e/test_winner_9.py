import json
import base64
from algosdk.encoding import decode_address
import unittest
from lib.blockchain import Vote

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
        This test involves voting transactions by different users,
        verifies the final state of the voting application, and tests
        the deletion of keys associated with the winning choice.
        """
        self.vote_app_user1.vote([b"vote", b"choiceA", b"child-oid_a1"])
        self.vote_app_user2.vote([b"vote", b"choiceB", b"child-oid_b1"])
        self.vote_app_user2.vote([b"vote", b"choiceA", b"child-oid_b1"])
        self.vote_app_creator.vote([b"vote", b"choiceZ", b"child_oid_z1"])
        winner_state = self.vote_app_creator.read_global_state()

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

        self.assertDictEqual(winner_state, expected_winner_state)

        # Delete keys associated with the winning choice 'choiceZ'
        self.vote_app_creator.delete_keys_associated_with_choice('choiceZ')

        intermediate_state = self.vote_app_creator.read_global_state()

        expected_intermediate_state = {
            'Creator': 'VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M',
            'TotalSupply': 1000000,
            'OriginalVoter_choiceA': 'XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM',
            'OriginalVoter_choiceB': 'ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A',
            'Vote_choiceA_XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM': 1,
            'Vote_choiceB_ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A': 1,
            'Vote_choiceA_ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A': 1,
            'choiceA': 52500,
            'choiceB': 2500,
            'choiceA_child': 'child-oid_a1',
            'choiceB_child': 'child-oid_b1'
        }

        self.assertDictEqual(intermediate_state, expected_intermediate_state)

        # User1 votes on 'choiceB', but doesn't change successfully change its 'ref' as
        # the user isn't the original voter.
        self.vote_app_user1.vote([b"vote", b"choiceB", b"child-oid_a1"])

        # Assert the intermediate state before the creator votes on 'choiceB'
        intermediate_state_before_creator_vote = self.vote_app_creator.read_global_state()
        expected_intermediate_state_before_creator_vote = {
            'Creator': 'VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M',
            'TotalSupply': 1000000,
            'OriginalVoter_choiceA': 'XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM',
            'OriginalVoter_choiceB': 'ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A',
            'Vote_choiceA_XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM': 1,
            'Vote_choiceB_ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A': 1,
            'Vote_choiceA_ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A': 1,
            'Vote_choiceB_XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM': 1,
            'choiceA': 52500,
            'choiceB': 52500,
            'Exclusive': 'choiceB',
            'choiceA_child': 'child-oid_a1',
            'choiceB_child': 'child-oid_b1'
        }
        self.assertDictEqual(intermediate_state_before_creator_vote, expected_intermediate_state_before_creator_vote)

        # Creator votes on 'choiceB'
        self.vote_app_creator.vote([b"vote", b"choiceB", b"child_oid_z1"])
        final_state = self.vote_app_creator.read_global_state()

        expected_final_state = {
            'Creator': 'VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M',
            'TotalSupply': 1000000,
            'OriginalVoter_choiceA': 'XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM',
            'OriginalVoter_choiceB': 'ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A',
            'Vote_choiceA_XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM': 1,
            'Vote_choiceB_ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A': 1,
            'Vote_choiceA_ELNJI3EFJYG5T7L3FXZEWAPUVUE24UUXKOUQALZQWXYUCWUM5J4DHLNU2A': 1,
            'Vote_choiceB_VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M': 1,
            'Vote_choiceB_XNDK5BBUOCENNRQ3FT4SQSCENFBNSY3BMOU3W2EZGNLH7ZD5ZSANKIRJZM': 1,
            'choiceA': 52500,
            'choiceB': 930000,
            'Winner': 'choiceB',
            'choiceA_child': 'child-oid_a1',
            'choiceB_child': 'child_oid_z1'
        }

        self.assertDictEqual(final_state, expected_final_state)

if __name__ == "__main__":
    unittest.main()
