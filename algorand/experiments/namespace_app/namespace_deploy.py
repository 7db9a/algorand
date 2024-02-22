import base64
import logging

from algosdk import transaction
from algosdk import account, mnemonic
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
        global_schema = transaction.StateSchema(num_uints=0, num_byte_slices=3)
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

def add_repo(client, private_key, app_id, repo_name, repo_url):
    try:
        # Define sender
        sender = account.address_from_private_key(private_key)

        # Get node suggested parameters
        params = client.suggested_params()

        # Create unsigned transaction
        app_args = [b"add_repo", bytes(repo_name, "utf-8"), bytes(repo_url, "utf-8")]
        txn = transaction.ApplicationCallTxn(
            sender,
            params,
            app_id,
            transaction.OnComplete.NoOpOC,
            app_args=app_args
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
        formatted_key = base64.b64decode(key).decode("utf-8")
        if value["type"] == 1:  # byte string
            try:
                # Try to decode as UTF-8 string
                formatted_value = base64.b64decode(value["bytes"]).decode("utf-8")
            except UnicodeDecodeError:
                # If decode fails, keep as base64 encoded string
                formatted_value = value["bytes"]
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
    app_id = create_app(client, private_key)
    print("Created new app-id:", app_id)

    # User 1 adds a repository
    add_repo(client, private_key, app_id, "User1Repo", "https://github.com/User1Repo")

    # User 2 adds a repository (using the same private key)
    add_repo(client, private_key, app_id, "User2Repo", "https://github.com/User2Repo")

    # Read the global state of the application
    global_state = read_global_state(client, creator_address, app_id)
    print("Global State:", global_state)

    # Optional: Delete the application
    delete_app(client, private_key, app_id)
    print("Application deleted.")

if __name__ == "__main__":
    main()

