from algosdk import util
#from util import get_account, get_algod_client
from algosdk import account, mnemonic
from algosdk import transaction
from algosdk.v2client import algod

import json

# Local testnet
algod_address = "http://localhost:8080"
algod_token = "d028d859385441d3ab510c88fb37ad294b9fa1b5c725c9920b4e24846d58072a"

# example: ACCOUNT_GENERATE
private_key, address = account.generate_account()
print(f"address: {address}")
print(f"private key: {private_key}")
print(f"mnemonic: {mnemonic.from_private_key(private_key)}")
# example: ACCOUNT_GENERATE

# example: ACCOUNT_RECOVER_MNEMONIC
mn = "cost piano sample enough south bar diet garden nasty mystery mesh sadness convince bacon best patch surround protect drum actress entire vacuum begin abandon hair"
pk = mnemonic.to_private_key(mn)
print(f"Base64 encoded private key: {pk}")
addr = account.address_from_private_key(pk)
print(f"Address: {addr}")
# example: ACCOUNT_RECOVER_MNEMONIC

algod_client = algod.AlgodClient(algod_token, algod_address)
account_info = algod_client.account_info(addr)
print(json.dumps(account_info, indent=4))
