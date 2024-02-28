# based off https://github.com/algorand/docs/blob/cdf11d48a4b1168752e6ccaf77c8b9e8e599713a/examples/smart_contracts/v2/python/stateful_smart_contracts.py

import base64

from algosdk import transaction
from algosdk import account, mnemonic
from algosdk.transaction import AssetTransferTxn
from algosdk.v2client import algod
from pyteal import compileTeal, Mode

with open('vote_approval.teal.tok', 'rb') as f:
    approval_program = f.read()


with open('vote_clear_state.teal.tok', 'rb') as f:
    clear_program = f.read()

# Debug: Print or inspect the contents of compiled_teal_bytes
print("Compiled TEAL Bytecode:", clear_program)

TOTAL_SUPPLY = 1000000  # 1 million

# user declared account mnemonics
mnemonic_phrase = "twin pumpkin plastic stage fortune shallow melt betray ribbon receive claim enrich price exile absent avoid woman toilet print settle shiver inform rookie absorb unaware"

# user declared algod connection parameters. Node must have EnableDeveloperAPI set to true in its config
algod_address = "http://127.0.0.1:8080"
algod_token = "1fa5aed7ec723da8ec9abfb6396adbbb607dd95316f8277456ec7b65afeb3893"


# helper function to compile program source
def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])


# helper function that converts a mnemonic passphrase into a private signing key
def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key


# helper function that waits for a given txid to be confirmed by the network
def wait_for_confirmation(client, txid):
    last_round = client.status().get("last-round")
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get("confirmed-round") and txinfo.get("confirmed-round") > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print(
        "Transaction {} confirmed in round {}.".format(
            txid, txinfo.get("confirmed-round")
        )
    )
    return txinfo


def wait_for_round(client, round):
    last_round = client.status().get("last-round")
    print(f"Waiting for round {round}")
    while last_round < round:
        last_round += 1
        client.status_after_block(last_round)
        print(f"Round {last_round}")

def create_app(
    client,
    private_key,
    approval_program,
    clear_program,
    global_schema,
    local_schema,
    app_args=None,
):
    # Define sender as creator
    sender = account.address_from_private_key(private_key)

    # Declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # Get node suggested parameters
    params = client.suggested_params()
    # Comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # Include Asset 1653 in the foreign assets for the transaction
    foreign_assets = [1653]  # Asset ID to be included

    if app_args is None:
        app_args = []
    app_args.append(intToBytes(TOTAL_SUPPLY))  # Append TotalSupply to app_args

    # Create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        sender,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
        app_args,
        foreign_assets=foreign_assets
    )

    # Sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # Send transaction
    client.send_transactions([signed_txn])

    # Await confirmation
    wait_for_confirmation(client, tx_id)

    # Display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id:", app_id)

    return app_id

# opt-in to application
def opt_in_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)
    print("OptIn from account: ", sender)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationOptInTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("OptIn to app-id:", transaction_response["txn"]["txn"]["apid"])

# Modify the call_app function to include foreign_assets
def call_app(client, private_key, app_id, app_args):
    # declare sender
    sender = account.address_from_private_key(private_key)
    print("Call from account:", sender)

    # get node suggested parameters
    params = client.suggested_params()

    # Include Asset 1653 in the foreign assets for the transaction
    foreign_assets = [1653]  # Asset ID to be included

    # create unsigned transaction
    txn = transaction.ApplicationCallTxn(
        sender,
        params,
        app_id,
        transaction.OnComplete.NoOpOC,  # Specify the type of application call
        app_args=app_args,
        foreign_assets=foreign_assets  # Add this line
    )

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

def format_state(state):
    formatted = {}
    for item in state:
        key = item["key"]
        value = item["value"]
        try:
            # Try decoding as UTF-8. If it fails, handle as binary data
            formatted_key = base64.b64decode(key).decode("utf-8")
        except UnicodeDecodeError:
            # If it's not a UTF-8 string, it might be binary data like an address
            formatted_key = base64.b64decode(key).hex()  # Represent binary data in hex

        if value["type"] == 1:
            # byte string
            try:
                # Try decoding value as UTF-8
                formatted_value = base64.b64decode(value["bytes"]).decode("utf-8")
            except UnicodeDecodeError:
                # If it's not a UTF-8 string, handle as binary data
                formatted_value = base64.b64decode(value["bytes"]).hex()  # Represent binary data in hex
        else:
            # integer
            formatted_value = value["uint"]

        formatted[formatted_key] = formatted_value

    return formatted

# Function to opt-in to an ASA (commented out by default)
def optin_to_asa(client, private_key, asset_id):
    """
    Opt-in to an ASA for the account associated with the provided private key.

    Args:
        client (AlgodClient): An instance of the Algod client.
        private_key (str): The private key of the account opting in.
        asset_id (int): The ID of the ASA to opt-in.
    """
    # Define sender
    sender = account.address_from_private_key(private_key)

    # Get node suggested parameters
    params = client.suggested_params()

    # Create the asset opt-in transaction
    optin_txn = AssetTransferTxn(
        sender=sender,
        sp=params,
        receiver=sender,
        amt=0,
        index=asset_id
    )

    # Sign the transaction
    signed_optin_txn = optin_txn.sign(private_key)

    # Send the transaction
    txid = client.send_transaction(signed_optin_txn)

    # Await confirmation
    wait_for_confirmation(client, txid)
    print(f"Opted-in to asset {asset_id}.")

# read user local state
def read_local_state(client, addr, app_id):
    results = client.account_info(addr)
    for local_state in results["apps-local-state"]:
        if local_state["id"] == app_id:
            if "key-value" not in local_state:
                return {}
            return format_state(local_state["key-value"])
    return {}


# read app global state
def read_global_state(client, addr, app_id):
    results = client.account_info(addr)
    apps_created = results["created-apps"]
    for app in apps_created:
        if app["id"] == app_id:
            return format_state(app["params"]["global-state"])
    return {}


# delete application
def delete_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationDeleteTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Deleted app-id:", transaction_response["txn"]["txn"]["apid"])


# close out from application
def close_out_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationCloseOutTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Closed out from app-id: ", transaction_response["txn"]["txn"]["apid"])


# clear application
def clear_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationClearStateTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Cleared app-id:", transaction_response["txn"]["txn"]["apid"])


# convert 64 bit integer i to byte string
def intToBytes(i):
    return i.to_bytes(8, 'big')  # Convert integer to 8-byte big-endian

def main():
    # initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # define private keys
    creator_private_key = get_private_key_from_mnemonic(mnemonic_phrase)
    user_private_key = get_private_key_from_mnemonic(mnemonic_phrase)

    # Derive the account address from the private key
    account_address = account.address_from_private_key(creator_private_key)

    # Assert that the account address is the expected one
    expected_address = "VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M"
    assert account_address == expected_address, f"Unexpected account address: {account_address}"
    print('asset address, success')


    # Example usage of the optin_to_asa function (commented out)
    # Uncomment the lines below to perform ASA opt-in
    asset_id = 1653  # Replace with the actual asset ID
    optin_to_asa(algod_client, creator_private_key, asset_id)

    # declare application state storage (immutable)
    local_ints = 0
    local_bytes = 0
    global_ints = (
        24  # 4 for setup + 20 for choices. Use a larger number for more choices.
    )
    global_bytes = 2
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    # configure registration and voting period
    status = algod_client.status()
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

    # create new application
    app_id = create_app(
        algod_client,
        creator_private_key,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
        app_args,
    )

    # read global state of application
    print(
        "Global state:",
        read_global_state(
            algod_client, account.address_from_private_key(creator_private_key), app_id
        ),
    )

    # wait for registration period to start
    wait_for_round(algod_client, regBegin)

    # opt-in to application
    opt_in_app(algod_client, user_private_key, app_id)

    wait_for_round(algod_client, voteBegin)

    # call application without arguments
    call_app(algod_client, user_private_key, app_id, [b"vote", b"choiceA"])

    # read local state of application from user account
    #print(
    #    "Local state:",
    #    read_local_state(
    #        algod_client, account.address_from_private_key(user_private_key), app_id
    #    ),
    #)

    # wait for registration period to start
    wait_for_round(algod_client, voteEnd)

    # read global state of application
    global_state = read_global_state(
        algod_client, account.address_from_private_key(creator_private_key), app_id
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

    # delete application
    delete_app(algod_client, creator_private_key, app_id)

    # clear application from user account
    clear_app(algod_client, user_private_key, app_id)


if __name__ == "__main__":
    main()
