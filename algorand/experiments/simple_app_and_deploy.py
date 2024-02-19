from algosdk.v2client import algod
from algosdk import account, mnemonic
from algosdk import transaction
from pyteal import *

def approval_program():
    return Approve()

# Initialize Algod Client
algod_address = "http://127.0.0.1:8080"
algod_token = "d028d859385441d3ab510c88fb37ad294b9fa1b5c725c9920b4e24846d58072a"
client = algod.AlgodClient(algod_token, algod_address)

# Generate TEAL Code
approval_program_teal = compileTeal(approval_program(), mode=Mode.Application, version=2)

# Save TEAL Code to File
with open("approval_program.teal", "w") as f:
    f.write(approval_program_teal)

# Read TEAL Code from File and Compile
with open("approval_program.teal", "r") as f:
    approval_program_source = f.read()
    compile_response = client.compile(approval_program_source)
    program_bytes = base64.b64decode(compile_response['result'])

# Set up account using mnemonic
mnemonic_phrase = "cost piano sample enough south bar diet garden nasty mystery mesh sadness convince bacon best patch surround protect drum actress entire vacuum begin abandon hair"
private_key = mnemonic.to_private_key(mnemonic_phrase)
sender_address = account.address_from_private_key(private_key)

# Prepare transaction
params = client.suggested_params()
txn = transaction.ApplicationCreateTxn(
    sender=sender_address,
    sp=params,
    on_complete=OnComplete.NoOpOC,
    approval_program=program_bytes,
    clear_program=program_bytes,
    global_schema=StateSchema(num_uints=0, num_byte_slices=0),
    local_schema=StateSchema(num_uints=0, num_byte_slices=0)
)

# Sign and send transaction
signed_txn = txn.sign(private_key)
tx_id = client.send_transaction(signed_txn)
print(f"Submitted transaction {tx_id}")

# Wait for confirmation
confirmed_txn = wait_for_confirmation(client, tx_id, 4)
print("Transaction confirmed in round", confirmed_txn['confirmed-round'])

