import base64
import logging

from algosdk import transaction
from algosdk import account, mnemonic
from algosdk.v2client import algod
from pyteal import compileTeal, Mode
from namespace import approval_program, clear_state_program


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_client(algod_token, algod_address):
    return algod.AlgodClient(algod_token, algod_address)

def compile_program(client, source_code):
    try:
        compile_response = client.compile(source_code)
        return base64.b64decode(compile_response["result"])
    except Exception as e:
        logging.error(f"Error compiling program: {e}")
        raise

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

def compile_teal_programs(client):
    approval_teal = compileTeal(approval_program(), mode=Mode.Application, version=2)
    clear_teal = compileTeal(clear_state_program(), mode=Mode.Application, version=2)
    return compile_program(client, approval_teal), compile_program(client, clear_teal)

def create_app(client, private_key, approval_program, clear_program, app_args):
    try:
        # Define sender as creator
        sender = account.address_from_private_key(private_key)

        # Get node suggested parameters
        params = client.suggested_params()

        # Define the application schemas
        global_schema = transaction.StateSchema(num_uints=0, num_byte_slices=2)
        local_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)

        # Create unsigned transaction
        txn = transaction.ApplicationCreateTxn(
            sender,
            params,
            OnComplete.NoOpOC.real,
            approval_program,
            clear_program,
            global_schema,
            local_schema,
            app_args
        )

        # Sign and send the transaction
        signed_txn = txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()
        client.send_transactions([signed_txn])
        logging.info(f"Transaction sent, TxID: {tx_id}")

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

def update_app(client, private_key, app_id, approval_program, clear_program):
    # Define sender as creator
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

def delete_app(client, private_key, app_id):
    # Define sender as creator
    sender = account.address_from_private_key(private_key)

    # Get node suggested parameters
    params = client.suggested_params()

    # Create unsigned transaction
    txn = transaction.ApplicationDeleteTxn(sender, params, app_id)

    # Sign and send the transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    client.send_transactions([signed_txn])

    # Await confirmation
    wait_for_confirmation(client, tx_id)
    print("Deleted app-id:", app_id)

def read_global_state(client, app_id):
    response = client.application_info(app_id)
    state = {}
    for item in response['params']['global-state']:
        key = base64.b64decode(item['key']).decode('utf-8')
        value = item['value']
        if value['type'] == 1:  # byte string
            state[key] = base64.b64decode(value['bytes']).decode('utf-8')
        else:
            state[key] = value['uint']
    return state

def main():
    # Configuration and client initialization
    algod_address = "http://127.0.0.1:8080"
    algod_token = "d028d859385441d3ab510c88fb37ad294b9fa1b5c725c9920b4e24846d58072a"
    creator_mnemonic = "cost piano sample enough south bar diet garden nasty mystery mesh sadness convince bacon best patch surround protect drum actress entire vacuum begin abandon hair"

    client = initialize_client(algod_token, algod_address)
    creator_private_key = mnemonic.to_private_key(creator_mnemonic)

    # Load the pre-compiled programs
    approval_program = load_compiled_program("approval_program.teal")
    clear_state_program = load_compiled_program("clear_state_program.teal")

    # Create the application
    app_id = create_app(client, creator_private_key, approval_program_compiled, clear_state_program_compiled, [b"YourRepoName", b"https://github.com/YourRepoURL"])
    print("Created new app-id:", app_id)

    # Read the global state of the application
    global_state = read_global_state(client, app_id)
    print("Global State:", global_state)

    # Optional: Update the application and read the state again
    # update_app(client, creator_private_key, app_id, approval_program_compiled, clear_state_program_compiled)
    # global_state = read_global_state(client, app_id)
    # print("Updated Global State:", global_state)

    # Delete the application
    delete_app(client, creator_private_key, app_id)
    print("Application deleted.")

if __name__ == "__main__":
    main()

