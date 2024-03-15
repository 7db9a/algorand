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
    print("Starting account creation...")

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

    # Create a new account
    try:
        print("Creating a new account...")
        account_address = wallet_utility.create_account(datadir)
        print(f"Created new account with address: {account_address}")
    except Exception as e:
        print(f"Error creating account: {str(e)}")
        return

    print("Account creation completed.")

if __name__ == "__main__":
    main()
