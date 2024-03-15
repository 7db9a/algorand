import subprocess
from lib.utilities.wallet_utility import (
    WalletUtility
)

def main():
    print("Starting account info retrieval...")

    # Set the data directory for the goal commands
    datadir = "/algod/data/net1/Node"  # Replace with the actual data directory path
    print(f"Using data directory: {datadir}")

    # Create an instance of WalletUtility
    wallet_utility = WalletUtility()

    # Get the account address of the newly created account
    account_address = "RS35Q7QY3CHWOSHH73BVGPCP3XHCFYXIKRKFKCKCP7W3IHMFF4QOA5SMOA"  # Replace with the actual account address
    print(f"Account address: {account_address}")

    # Get account info
    try:
        print(f"Getting account info for '{account_address}'...")
        account_info = wallet_utility.get_account_info_by_address(account_address, datadir)
        print(f"Account info for '{account_address}':")
        for key, value in account_info.items():
            if value:
                print(f"{key}: {value}")
            else:
                print(f"{key}: <none>")
    except Exception as e:
        print(f"Error getting account info: {str(e)}")
        return

    print("Account info retrieval completed.")

if __name__ == "__main__":
    main()
