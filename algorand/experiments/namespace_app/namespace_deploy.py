import base64
import logging

from algosdk import transaction, account, mnemonic, encoding
from algosdk.transaction import AssetTransferTxn
from algosdk.v2client import algod
from pyteal import compileTeal, Mode

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

with open('namespace_approval_program.teal.tok', 'rb') as f:
    approval_program = f.read()


with open('namespace_clear_state_program.teal.tok', 'rb') as f:
    clear_program = f.read()

# Debug: Print or inspect the contents of compiled_teal_bytes
print("Compiled TEAL Bytecode:", clear_program)

def initialize_client(algod_token, algod_address):
    return algod.AlgodClient(algod_token, algod_address)

def wait_for_confirmation(client, txid):
    last_round = client.status().get("last-round")
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get("confirmed-round") and txinfo.get("confirmed-round") > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get("confirmed-round")))
    return txinfo

def delete_repo(client, private_key, app_id, repo_name):
    try:
        sender = account.address_from_private_key(private_key)
        params = client.suggested_params()

        app_args = [b"delete_repo", bytes(repo_name, "utf-8")]
        txn = transaction.ApplicationCallTxn(sender, params, app_id, transaction.OnComplete.NoOpOC, app_args=app_args)

        signed_txn = txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()
        client.send_transactions([signed_txn])

        wait_for_confirmation(client, tx_id)
        logging.info(f"Repo {repo_name} deleted from app-id: {app_id}")

    except Exception as e:
        logging.error(f"Error deleting repo: {e}")
        raise

def create_app(client, private_key):
    try:
        # Define sender as creator
        sender = account.address_from_private_key(private_key)

        # Get node suggested parameters
        params = client.suggested_params()

        # Define the application schemas
        global_schema = transaction.StateSchema(num_uints=0, num_byte_slices=5)
        local_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)

        # Create unsigned transaction
        txn = transaction.ApplicationCreateTxn(
            sender,
            params,
            transaction.OnComplete.NoOpOC,
            approval_program,
            clear_program,
            global_schema,
            local_schema
        )

        # Sign and send the transaction
        signed_txn = txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()
        client.send_transactions([signed_txn])

        # Await confirmation
        wait_for_confirmation(client, tx_id)

        # Fetch and return the application ID
        transaction_response = client.pending_transaction_info(tx_id)
        app_id = transaction_response["application-index"]
        logging.info(f"Created new app-id: {app_id}")
        return app_id

    except Exception as e:
        logging.error(f"Error creating app: {e}")
        raise

def add_contributor(client, private_key, app_id, contributor_name):
    try:
        # Define sender
        sender = account.address_from_private_key(private_key)

        # Get node suggested parameters
        params = client.suggested_params()

        # Include Asset 1653 in the foreign assets for the transaction
        foreign_assets = [1653]  # Asset ID to be included

        # Create unsigned transaction
        app_args = [b"add_contributor", bytes(contributor_name, "utf-8")]
        txn = transaction.ApplicationCallTxn(
            sender,
            params,
            app_id,
            transaction.OnComplete.NoOpOC,
            app_args=app_args,
            foreign_assets=foreign_assets  # Add this line
        )

        # Sign and send the transaction
        signed_txn = txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()
        client.send_transactions([signed_txn])

        # Await confirmation
        wait_for_confirmation(client, tx_id)
        logging.info(f"Contributor {contributor_name} added to app-id: {app_id}")

    except Exception as e:
        logging.error(f"Error adding contributor: {e}")
        raise

def add_repo(client, private_key, app_id, repo_name, repo_url):
    try:
        # Define sender
        sender = account.address_from_private_key(private_key)

        # Get node suggested parameters
        params = client.suggested_params()

        # Include Asset 1653 in the foreign assets for the transaction
        foreign_assets = [1653]  # Asset ID to be included

        # Create unsigned transaction
        app_args = [b"add_repo", bytes(repo_name, "utf-8"), bytes(repo_url, "utf-8")]
        txn = transaction.ApplicationCallTxn(
            sender,
            params,
            app_id,
            transaction.OnComplete.NoOpOC,
            app_args=app_args,
            foreign_assets=foreign_assets  # Add this line
        )

        # Sign and send the transaction
        signed_txn = txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()
        client.send_transactions([signed_txn])

        # Await confirmation
        wait_for_confirmation(client, tx_id)
        logging.info(f"Repo {repo_name} added to app-id: {app_id}")

    except Exception as e:
        logging.error(f"Error adding repo: {e}")
        raise

def update_app(client, private_key, app_id) :
    sender = account.address_from_private_key(private_key)

    # Get node suggested parameters
    params = client.suggested_params()

    # Create unsigned transaction
    txn = transaction.ApplicationUpdateTxn(
        sender,
        params,
        app_id,
        approval_program,
        clear_program
    )

    # Sign and send the transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    client.send_transactions([signed_txn])

    # Await confirmation
    wait_for_confirmation(client, tx_id)
    print("Updated app-id:", app_id)

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
    #params.flat_fee = True
    #params.fee = 1000

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

def format_state(state):
    formatted = {}
    for item in state:
        key = item["key"]
        value = item["value"]

        # Decode the base64 key
        decoded_key = base64.b64decode(key)

        # Check if the key is an Algorand address (32 bytes length)
        if len(decoded_key) == 32:
            # Encode as Algorand address
            formatted_key = encoding.encode_address(decoded_key)
        else:
            # Try to decode as UTF-8
            try:
                formatted_key = decoded_key.decode("utf-8")
            except UnicodeDecodeError:
                formatted_key = decoded_key  # Fallback to raw bytes if not a valid UTF-8 string

        # Process value based on its type
        if value["type"] == 1:  # byte string
            # Decode the base64 value
            decoded_value = base64.b64decode(value["bytes"])

            # Try to decode the value as UTF-8, else keep it as base64 string
            try:
                formatted_value = decoded_value.decode("utf-8")
            except UnicodeDecodeError:
                formatted_value = base64.b64encode(decoded_value).decode("utf-8")
        else:  # integer
            formatted_value = value["uint"]

        formatted[formatted_key] = formatted_value
    return formatted

def read_global_state(client, addr, app_id):
    results = client.account_info(addr)
    apps_created = results.get("created-apps", [])
    for app in apps_created:
        if app["id"] == app_id:
            return format_state(app["params"]["global-state"])
    return {}

def main():
    # Configuration and client initialization
    algod_address = "http://127.0.0.1:8080"
    algod_token = "1fa5aed7ec723da8ec9abfb6396adbbb607dd95316f8277456ec7b65afeb3893"

    client = initialize_client(algod_token, algod_address)

    # Using the same mnemonic for both users
    mnemonic_phrase = "twin pumpkin plastic stage fortune shallow melt betray ribbon receive claim enrich price exile absent avoid woman toilet print settle shiver inform rookie absorb unaware"
    private_key = mnemonic.to_private_key(mnemonic_phrase)


    # Create the application
    app_id = create_app(client, private_key)

    # Get the creator's address
    creator_address = account.address_from_private_key(private_key)

    # Derive the account address from the private key
    account_address = account.address_from_private_key(private_key)

    # Assert that the account address is the expected one
    expected_address = "VAX6M7SZY65NXSMAFRNUYHDAZK3326IUPZFKO63QZAAMIPVAK7ECTS2F4M"
    assert creator_address == expected_address, f"Unexpected account address: {account_address}"
    print('asset address, success')

    ## optin to asa - only needs to be done once in ownership lifecycle.
    #asset_id = 1653  # Replace with the actual asset ID
    ## Create the asset opt-in transaction
    #params = client.suggested_params()
    #optin_txn = AssetTransferTxn(
    #    sender=creator_address,
    #    sp=params,
    #    receiver=creator_address,
    #    amt=0,
    #    index=asset_id
    #)
    ## Sign the transaction
    #signed_optin_txn = optin_txn.sign(private_key)
    ## Send the transaction
    #txid = client.send_transaction(signed_optin_txn)
    #wait_for_confirmation(client, txid)

    # User 1 adds themselves as a contributor
    add_contributor(client, private_key, app_id, "User1")

    # User 2 adds themselves as a contributor (using the same private key)
    add_contributor(client, private_key, app_id, "User2")

    # User 1 adds a repository
    add_repo(client, private_key, app_id, "User1Repo", "https://github.com/User1Repo")

    # User 2 adds a repository (using the same private key)
    add_repo(client, private_key, app_id, "User2Repo", "https://github.com/User2Repo")

    # Try and execute the contract as a non-asa holder (should fail)
    mnemonic_phrase_non_asa_holder = "brain rough jazz defy absent ability jeans much hire retire metal tragic fury culture stem beach farm upset relief stove sound comic bunker able exist"
    private_key_non_asa_holder = mnemonic.to_private_key(mnemonic_phrase_non_asa_holder)
    non_asa_holder_address = account.address_from_private_key(private_key_non_asa_holder)
    add_contributor(client, private_key, app_id, "User3")
    add_repo(client, private_key_non_asa_holder, app_id, "User3Repo", "https://github.com/User3Repo")

    # Read the global state of the application
    global_state = read_global_state(client, creator_address, app_id)
    print("Global State:", global_state)

    # Optional: Delete the application
    delete_app(client, private_key, app_id)
    print("Application deleted.")

if __name__ == "__main__":
    main()

