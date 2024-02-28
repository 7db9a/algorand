import base64
from algosdk import transaction, account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetTransferTxn, StateSchema
#from pyteal import compileTeal, Mode

from lib.utilities.utility import (
    wait_for_confirmation,
    get_private_key_from_mnemonic,
    intToBytes,
    opt_in_app,
    call_app,
    read_global_state
)

class Vote:
    def __init__(self, algod_address, algod_token, creator_mnemonic, user_mnemonic):
        self.client = algod.AlgodClient(algod_token, algod_address)
        self.creator_private_key = get_private_key_from_mnemonic(creator_mnemonic)
        self.user_private_key = get_private_key_from_mnemonic(user_mnemonic)
        self.asset_id = 1653  # Replace with the actual asset ID
        self.global_ints = 24  # Adjust as needed
        self.global_bytes = 2  # Adjust as needed
        self.local_ints = 0
        self.local_bytes = 0
        self.app_id = None
        self.status = self.client.status()
        self.regBegin = self.status["last-round"] + 10
        self.regEnd = self.regBegin + 10
        self.voteBegin = self.regEnd + 1
        self.voteEnd = self.voteBegin + 10

        with open('vote_approval.teal.tok', 'rb') as f:
            self.approval_program = f.read()

        with open('vote_clear_state.teal.tok', 'rb') as f:
            self.clear_program = f.read()

    def create_app(self, app_args=None):
        sender = account.address_from_private_key(self.creator_private_key)
        params = self.client.suggested_params()
        params.flat_fee = True
        params.fee = 1000
        global_schema = StateSchema(self.global_ints, self.global_bytes)
        local_schema = StateSchema(self.local_ints, self.local_bytes)

        print(f"Registration rounds: {self.regBegin} to {self.regEnd}")
        print(f"Vote rounds: {self.voteBegin} to {self.voteEnd}")

        # create list of bytes for app args
        app_args = [
            intToBytes(self.regBegin),
            intToBytes(self.regEnd),
            intToBytes(self.voteBegin),
            intToBytes(self.voteEnd),
        ]

        if app_args is None:
            app_args = []
        app_args.append(intToBytes(1000000))  # Append TotalSupply to app_args

        txn = transaction.ApplicationCreateTxn(
            sender,
            params,
            transaction.OnComplete.NoOpOC.real,
            self.approval_program,
            self.clear_program,
            global_schema,
            local_schema,
            app_args,
            foreign_assets=[self.asset_id]
        )

        signed_txn = txn.sign(self.creator_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.client.send_transactions([signed_txn])
        wait_for_confirmation(self.client, tx_id)
        response = self.client.pending_transaction_info(tx_id)
        self.app_id = response['application-index']

        return self.app_id

def vote(self, app_args=None):
    sender = account.address_from_private_key(self.creator_private_key)

    # opt-in to application
    opt_in_app(self.client, self.user_private_key, self.app_id)

    wait_for_round(self.client, voteBegin)

    # call application without arguments
    call_app(self.client, self.user_private_key, self.app_id, app_args)

    # read local state of application from user account
    #print(
    #    "Local state:",
    #    read_local_state(
    #        self.client, account.address_from_private_key(self.user_private_key), self.app_id
    #    ),
    #)

    # wait for registration period to start
    wait_for_round(self.client, voteEnd)

    # read global state of application
    global_state = read_global_state(
        self.client, sender, self.app_id
    )
    print("Global state:", global_state)

    # Find the choice with the maximum votes
    max_votes = 0
    max_votes_choice = None
    for key, value in global_state.items():
        if key not in (
            "RegBegin",
            "RegEnd",
            "VoteBegin",
            "VoteEnd",
            "Creator",
            "TotalSupply"  # Exclude TotalSupply from the winner calculation
        ) and isinstance(value, int):
            if value > max_votes:
                max_votes = value
                max_votes_choice = key

    print("The winner is:", max_votes_choice if max_votes_choice is not None else "No votes cast")

