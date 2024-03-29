import subprocess
from lib.utilities.wallet_utility import (
    WalletUtility
)

def check_goal_cli_exists():
    try:
        subprocess.run(["goal", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def main():
    print("Starting account info retrieval...")

    # Check if the goal CLI is accessible in the system's PATH
    if not check_goal_cli_exists():
        print("The 'goal' CLI is not found in the system's PATH.")
        print("Please make sure the 'goal' CLI is installed and accessible.")
        return

    print("Goal CLI found.")

    # Create an instance of WalletUtility
    wallet_utility = WalletUtility()

    # Set the data directory for the goal commands
    datadir = "/algod/data/net1/Node"  # Replace with the actual data directory path
    print(f"Using data directory: {datadir}")

    # Get account info by address
    account_address = "YOUR_ACCOUNT_ADDRESS"  # Replace with the actual account address
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
