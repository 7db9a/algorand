#!/usr/bin/env python3

import subprocess
import sys
import re
import shlex

def get_account_address(name, datadir):
    # Run the goal account list command and capture the output
    output = subprocess.check_output(["goal", "account", "list", "-d", datadir]).decode("utf-8")

    # Split the output into lines
    lines = output.strip().split("\n")

    # Iterate over the lines and find the account with the specified name
    for line in lines:
        if name in line:
            # Extract the account address using a regular expression
            match = re.search(r"[A-Z2-7]{58}", line)
            if match:
                return match.group(0)

    return None

def main():
    if len(sys.argv) < 5 or sys.argv[3] != "-d":
        print("Usage: ./name_to_address.py <command> <name> -d <datadir>")
        sys.exit(1)

    command = shlex.split(sys.argv[1])
    name = sys.argv[2]
    datadir = sys.argv[4]

    # Get the account address for the specified name
    address = get_account_address(name, datadir)

    if address:
        # Run the specified command with the account address
        subprocess.run(command + ["-a", address, "-d", datadir] + sys.argv[5:])
    else:
        print(f"Account with name '{name}' not found.")

if __name__ == "__main__":
    main()
