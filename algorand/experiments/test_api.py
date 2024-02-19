import requests

def main():
    algod_address = "http://127.0.0.1:8080"
    algod_token = "d028d859385441d3ab510c88fb37ad294b9fa1b5c725c9920b4e24846d58072a"

    headers = {
        "X-Algo-API-Token": algod_token
    }

    try:
        response = requests.get(f"{algod_address}/v2/status", headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        print(response.json())
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

