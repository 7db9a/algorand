from algosdk.v2client import algod
from algosdk import account, mnemonic
import base64

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

# Initialize Algod Client
algod_address = "http://127.0.0.1:8080"
algod_token = "1fa5aed7ec723da8ec9abfb6396adbbb607dd95316f8277456ec7b65afeb3893"
client = algod.AlgodClient(algod_token, algod_address)

# Your mnemonic
mnemonic_phrase = "twin pumpkin plastic stage fortune shallow melt betray ribbon receive claim enrich price exile absent avoid woman toilet print settle shiver inform rookie absorb unaware"
private_key = mnemonic.to_private_key(mnemonic_phrase)
sender_address = account.address_from_private_key(private_key)
print("Sender address:", sender_address)

# Replace with appropriate app ID
app_id = 1121  # Replace with your application ID

# Fetch and print the global state of the application
global_state = read_global_state(client, sender_address, app_id)
print("Global State:", global_state)

