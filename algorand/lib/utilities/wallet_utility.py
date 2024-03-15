import subprocess
import json
import re

class WalletUtility:
    def create_account(self, datadir):
        try:
            # Create a new account using goal CLI
            command = ["goal", "account", "new", "-d", datadir]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                # Extract the account address from the output
                output_lines = result.stdout.strip().split("\n")
                print(f"Output lines: {output_lines}")  # Debugging print statement
                for line in output_lines:
                    if "Created new account with address" in line:
                        account_address = line.split(":")[-1].strip()
                        print(f"Extracted account address: {account_address}")  # Debugging print statement
                        return account_address
                raise Exception("Account address not found in the output")
            else:
                raise Exception(f"Error creating account: {result.stderr}")
        except Exception as e:
            raise Exception(f"Error creating account: {str(e)}")

    def get_account_info(self, account_name, datadir):
        try:
            # Get account information using goal CLI
            command = ["goal", "account", "list", "-d", datadir]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                # Split the output into lines
                lines = result.stdout.strip().split("\n")
                print(f"Account list output lines: {lines}")  # Debugging print statement
                # Iterate over the lines and find the account with the specified name
                for line in lines:
                    if account_name in line:
                        # Extract the account information using a regular expression
                        match = re.search(r"\{[^}]+}", line)
                        if match:
                            account_info = json.loads(match.group(0))
                            print(f"Extracted account info: {account_info}")  # Debugging print statement
                            return account_info
                raise Exception(f"Account with name '{account_name}' not found.")
            else:
                raise Exception(f"Error getting account info: {result.stderr}")
        except Exception as e:
            raise Exception(f"Error getting account info: {str(e)}")

    def get_account_info_by_address(self, account_address, datadir):
        try:
            # Get account information using goal CLI
            command = ["goal", "account", "info", "-a", account_address, "-d", datadir]
            result = subprocess.run(command, capture_output=True, text=True)
    
            if result.returncode == 0:
                # Split the output into lines
                lines = result.stdout.strip().split("\n")
                print(f"Account info output lines: {lines}")  # Debugging print statement
    
                # Create an empty dictionary to store the account info
                account_info = {}
    
                # Iterate over the lines and extract the relevant information
                for line in lines:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip()
                        account_info[key] = value
    
                print(f"Extracted account info: {account_info}")  # Debugging print statement
                return account_info
            else:
                raise Exception(f"Error getting account info: {result.stderr}")
        except Exception as e:
            raise Exception(f"Error getting account info: {str(e)}")

    def get_account_balance(self, account_address, datadir):
        try:
            # Get account balance using goal CLI
            command = ["goal", "account", "balance", "-a", account_address, "-d", datadir]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                balance = result.stdout.strip()
                print(f"Extracted account balance: {balance}")  # Debugging print statement
                return balance
            else:
                raise Exception(f"Error getting account balance: {result.stderr}")
        except Exception as e:
            raise Exception(f"Error getting account balance: {str(e)}")
