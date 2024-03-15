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
    print("Starting account balance retrieval...")

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

    # Get account balance
    account_address = "YOUR_ACCOUNT_ADDRESS"  # Replace with the actual account address
    try:
        print(f"Getting account balance for '{account_address}'...")
        account_balance = wallet_utility.get_account_balance(account_address, datadir)
        print(f"Account balance for '{account_address}': {account_balance}")
    except Exception as e:
        print(f"Error getting account balance: {str(e)}")
        return

    print("Account balance retrieval completed.")

if __name__ == "__main__":
    main()
