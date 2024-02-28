import base64
from algosdk import transaction, account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetTransferTxn, StateSchema
#from pyteal import compileTeal, Mode

from ...tests.test_util import (
    wait_for_confirmation,
    get_private_key_from_mnemonic,
    intToBytes,
)

class AlgorandVoteTestSuite:
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

        # configure registration and voting period
        status = self.client.status()
        regBegin = status["last-round"] + 10
        regEnd = regBegin + 10
        voteBegin = regEnd + 1
        voteEnd = voteBegin + 10

        print(f"Registration rounds: {regBegin} to {regEnd}")
        print(f"Vote rounds: {voteBegin} to {voteEnd}")

        # create list of bytes for app args
        app_args = [
            intToBytes(regBegin),
            intToBytes(regEnd),
            intToBytes(voteBegin),
            intToBytes(voteEnd),
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
        assert self.app_id is not None and self.app_id == 0, "Failed to create application"
        print("Created new app-id:", self.app_id)

    def run_tests(self):
        self.create_app()
        # Add calls to other test methods here

if __name__ == "__main__":
    algod_address = "http://127.0.0.1:8080"
    algod_token = "1fa5aed7ec723da8ec9abfb6396adbbb607dd95316f8277456ec7b65afeb3893"
    creator_mnemonic = "twin pumpkin plastic stage fortune shallow melt betray ribbon receive claim enrich price exile absent avoid woman toilet print settle shiver inform rookie absorb unaware"
    user_mnemonic = creator_mnemonic

    test_suite = AlgorandVoteTestSuite(algod_address, algod_token, creator_mnemonic, user_mnemonic)
    test_suite.run_tests()
