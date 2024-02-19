from algosdk.v2client import algod

# Initialize Algod client
algod_address = "http://localhost:8080"  # Use the appropriate address
# data/net1/Primary/algod.token
algod_token = "d028d859385441d3ab510c88fb37ad294b9fa1b5c725c9920b4e24846d58072a"
algod_client = algod.AlgodClient(algod_token, algod_address)

# Get node status
try:
    status = algod_client.status()
    print("Node status: ", status)
except Exception as e:
    print("Error: ", e)
