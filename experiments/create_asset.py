from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn

# Replace these values with your node's address and token
algod_address = "http://localhost:4190"
algod_token = "your_algod_token"

# Initialize Algod client
algod_client = algod.AlgodClient(algod_token, algod_address)

# Recover accounts (replace with actual mnemonics)
mnemonic1 = "alley permit pair cabin high width brown census thrive scan million time music submit matter bunker model color time someone eyebrow wait finger ability knife"
creator_private_key = mnemonic.to_private_key(mnemonic1)
creator_address = mnemonic.to_public_key(mnemonic1)

# Define asset parameters
params = algod_client.suggested_params()
asset_name = "hello"
unit_name = "HELLO"
total_supply = 1000000
decimals = 0
default_frozen = False
manager_address = creator_address
reserve_address = creator_address
freeze_address = creator_address
clawback_address = creator_address

# Create the asset creation transaction
txn = AssetConfigTxn(
    sender=creator_address,
    sp=params,
    total=total_supply,
    decimals=decimals,
    default_frozen=default_frozen,
    unit_name=unit_name,
    asset_name=asset_name,
    manager=manager_address,
    reserve=reserve_address,
    freeze=freeze_address,
    clawback=clawback_address
)

# Sign the transaction
signed_txn = txn.sign(creator_private_key)

# Send the transaction
txid = algod_client.send_transaction(signed_txn)
print("Transaction ID: {}".format(txid))

# Wait for confirmation
confirmed_txn = wait_for_confirmation(algod_client, txid, 4)
print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))
