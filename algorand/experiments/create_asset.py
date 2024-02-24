from algosdk import account, transaction, mnemonic
from algosdk.v2client import algod


def create_asa(algod_address, algod_token, creator_private_key, total_units, asset_name, unit_name, url=None, decimals=0):
    creator_address = account.address_from_private_key(creator_private_key)

    # Initialize the algod client
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # Get network parameters for transactions
    params = algod_client.suggested_params()

    # Asset creation transaction
    txn = transaction.AssetConfigTxn(
        sender=creator_address,
        sp=params,
        total=total_units,
        decimals=decimals,
        default_frozen=creator_address,
        unit_name=unit_name,
        asset_name=asset_name,
        manager=creator_address,
        reserve=creator_address,
        freeze=creator_address,
        clawback=creator_address,
        url=url
    )

    # Sign the transaction
    signed_txn = txn.sign(creator_private_key)

    # Send the transaction
    txid = algod_client.send_transaction(signed_txn)

    # Wait for confirmation
    try:
        confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)
        print("Asset ID: {}".format(confirmed_txn["asset-index"]))
        return confirmed_txn["asset-index"]
    except Exception as e:
        print(e)
        return None

# Function to query the ASA balance of an account
def get_asa_balance(algod_address, algod_token, address, asset_id):
    algod_client = algod.AlgodClient(algod_token, algod_address)
    account_info = algod_client.account_info(address)
    assets = account_info.get('assets', [])
    for asset in assets:
        if asset['asset-id'] == asset_id:
            return asset['amount']
    return 0


# Example usage
# Replace these with your actual details
algod_address = "http://127.0.0.1:8080"
algod_token = "1fa5aed7ec723da8ec9abfb6396adbbb607dd95316f8277456ec7b65afeb3893"
mnemonic_phrase = "twin pumpkin plastic stage fortune shallow melt betray ribbon receive claim enrich price exile absent avoid woman toilet print settle shiver inform rookie absorb unaware"
creator_private_key = mnemonic.to_private_key(mnemonic_phrase)
total_units = 1000000
asset_name = "TurboSrc"
unit_name = "TSRC"

asset_id = create_asa(algod_address, algod_token, creator_private_key, total_units, asset_name, unit_name)

if asset_id is not None:
    print(f"Successfully created asset with ID: {asset_id}")
else:
    print("Failed to create asset")

if asset_id is not None:
    print(f"Successfully created asset with ID: {asset_id}")
    # Query and print the ASA balance of the creator
    creator_address = account.address_from_private_key(creator_private_key)
    balance = get_asa_balance(algod_address, algod_token, creator_address, asset_id)
    print(f"Creator's balance of asset {asset_id}: {balance}")
else:
    print("Failed to create asset")
