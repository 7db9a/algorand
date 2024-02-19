from algosdk.v2client import algod

# Initialize the client
algod_address = "http://127.0.0.1:8080"
algod_token = "d028d859385441d3ab510c88fb37ad294b9fa1b5c725c9920b4e24846d58072a"
client = algod.AlgodClient(algod_token, algod_address)

# Fetch and print the status of the node
try:
    status = client.status()
    print("Node status:", status)
except Exception as e:
    print("Error querying node status:", e)

