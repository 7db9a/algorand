import subprocess
import json
import re
import tempfile

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
                        # Extract the account address using a regular expression
                        match = re.search(r"\b[A-Z2-7]{58}\b", line)
                        if match:
                            account_address = match.group(0)
                            print(f"Extracted account address: {account_address}")  # Debugging print statement
                            # Get the account info by address
                            account_info = self.get_account_info_by_address(account_address, datadir)
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

    def sign_transaction(self, unsigned_txn_file, account_address, datadir):
        try:
            # Create a temporary file to store the signed transaction
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as signed_txn_file:
                signed_txn_filename = signed_txn_file.name

                # Sign the transaction using goal CLI
                command = [
                    "goal", "clerk", "sign",
                    "-i", unsigned_txn_file,
                    "-o", signed_txn_filename,
                    "-a", account_address,
                    "-d", datadir
                ]
                result = subprocess.run(command, capture_output=True, text=True)

                if result.returncode == 0:
                    print("Transaction signed successfully.")
                    # Read the signed transaction from the file
                    signed_txn_file.seek(0)
                    signed_txn = signed_txn_file.read()
                    return signed_txn
                else:
                    raise Exception(f"Error signing transaction: {result.stderr}")
        except Exception as e:
            raise Exception(f"Error signing transaction: {str(e)}")
