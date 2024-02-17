import base64
from algosdk import account, mnemonic, algod
from algosdk.future.transaction import ApplicationCreateTxn, OnComplete, ApplicationUpdateTxn, ApplicationDeleteTxn
from pyteal import compileTeal, Mode
from namespace import approval_program, clear_state_program

# Declare constants for the algod connection and account mnemonics
algod_address = "http://localhost:8080"
algod_token = "d028d859385441d3ab510c88fb37ad294b9fa1b5c725c9920b4e24846d58072a"
creator_mnemonic = "cost piano sample enough south bar diet garden nasty mystery mesh sadness convince bacon best patch surround protect drum actress entire vacuum begin abandon hair"

def initialize_client():
    return algod.AlgodClient(algod_token, algod_address)

def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])

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
    approval_teal = compileTeal(approval_program(), mode=Mode.Application, version=3)
    clear_teal = compileTeal(clear_state_program(), mode=Mode.Application, version=3)
    return compile_program(client, approval_teal), compile_program(client, clear_teal)

from algosdk.future.transaction import ApplicationCreateTxn, ApplicationUpdateTxn, ApplicationDeleteTxn, StateSchema

def create_app(client, private_key, approval_program, clear_program, app_args):
    # Define sender as creator
    sender = account.address_from_private_key(private_key)

    # Get node suggested parameters
    params = client.suggested_params()

    # Define the application schemas
    global_schema = StateSchema(num_uints=0, num_byte_slices=2)
    local_schema = StateSchema(num_uints=0, num_byte_slices=0)

    # Create unsigned transaction
    txn = ApplicationCreateTxn(
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

    # Await confirmation
    wait_for_confirmation(client, tx_id)

    # Fetch and return the application ID
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id:", app_id)
    return app_id

def update_app(client, private_key, app_id, approval_program, clear_program):
    # Define sender as creator
    sender = account.address_from_private_key(private_key)

    # Get node suggested parameters
    params = client.suggested_params()

    # Create unsigned transaction
    txn = ApplicationUpdateTxn(
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
    txn = ApplicationDeleteTxn(sender, params, app_id)

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
    client = initialize_client()
    creator_private_key = mnemonic.to_private_key(creator_mnemonic)
    approval_program_compiled, clear_program_compiled = compile_teal_programs(client)

    app_id = create_app(client, creator_private_key, approval_program_compiled, clear_program_compiled, [b"YourRepoName", b"https://github.com/YourRepoURL"])

    global_state = read_global_state(algod_client, app_id)
    print("Global State:", global_state)

    #update_app(client, creator_private_key, app_id, approval_program_compiled, clear_program_compiled)

    delete_app(client, creator_private_key, app_id)

if __name__ == "__main__":
    main()

