import logging
from algosdk import transaction
from algosdk import account, mnemonic
from algosdk.v2client import algod

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def main():
    algod_address = "http://127.0.0.1:8080"
    algod_token = "1fa5aed7ec723da8ec9abfb6396adbbb607dd95316f8277456ec7b65afeb3893"
    mnemonic_phrase = "twin pumpkin plastic stage fortune shallow melt betray ribbon receive claim enrich price exile absent avoid woman toilet print settle shiver inform rookie absorb unaware"

    client = initialize_client(algod_token, algod_address)
    private_key = mnemonic.to_private_key(mnemonic_phrase)

    app_id = 1121   # Replace with your actual app ID

    delete_app(client, private_key, app_id)

if __name__ == "__main__":
    main()

