# Algorand Private Network Testing Guide

## Introduction
This guide provides detailed steps to set up and test a voting application on Algorand's private network, including smart contract interaction and ASA management.

## Setting Up the Environment

### Startup the Algorand Private Blockchain
1. Start the Algorand private blockchain using Docker:
   ```
   docker-compose build algorand
   docker-compose up -d algorand
   ```
   Note: Initial setup may take some time.

### Configure Test Users
2. After the blockchain is running, create a `test/e2e/tests/test-config.json` by using the default users information:
   - **Get Algod Token**:
     ```
     docker-compose exec algorand cat /algod/data/net1/Primary/algod.token
     ```
   - **List Accounts**:
     ```
     docker-compose exec algorand goal account list -d /algod/data/net1/Primary
     docker-compose exec algorand goal account list -d /algod/data/net1/Node
     ```
   - **Export Account Mnemonics**:
     For each account (regardless if its 'online' or 'offline'), retrieve the mnemonic (replace `<account_address>`):
     ```
     docker-compose exec algorand goal account export -a <account_address> -d /algod/data/net1/Primary
     docker-compose exec algorand goal account export -a <account_address> -d /algod/data/net1/Primary
     ```
     You'll have to use the above one or the other, depending where the account is found (Primary or Node).

   Populate the above info into `algorand/tests/e2e/test-config.json`.

   ```
   {
     "creatorInfo": {"mnemonic": "[creator mnemonic]"},
     "user1Info": {"mnemonic": "[user1 mnemonic]"},
     "user2Info": {"mnemonic": "[user2 mnemonic]"},
     "algodAddress": "http://127.0.0.1:8080",
     "algodToken": "[Your Algod Token]",
     "assetId": "[Your Asset ID]"
   }
   ```

### Testing Pre-requisites
3. Before testing, ensure:
   - Algorand private blockchain is running.
   - `test-config.json` is correctly configured.
   - Create an ASA (e.g., 1 million units named `tsrc`) and note the Asset ID.

## Running Tests

Execute tests with the following script:
```bash
#!/bin/bash

cd ~/projects/turbo-src
docker-compose stop algorand
docker-compose build algorand
docker-compose up -d algorand
sleep 1
docker-compose exec -it algorand ./tests/run_e2e.sh
```

## Account Address Lookup Script

The `name_to_address.py` script is a utility that allows you to retrieve the account address associated with a given account name and execute `goal` commands using that address.

### Usage

To use the `name_to_address.py` script, run the following command:

```
docker-compose exec -it algorand \
./name_to_address.py "<command>" <name> -d <datadir>
```

- `<command>`: The `goal` command you want to run (e.g., `"goal account balance"`).
- `<name>`: The name of the account you want to retrieve the address for.
- `-d <datadir>`: The data directory for the node (e.g., `/algod/data/net1/Node`).

### Example

To check the balance of an account with the name "user3" using the `name_to_address.py` script, run the following command:

```
docker-compose exec -it algorand \
./name_to_address.py "goal account balance" user3 -d /algod/data/net1/Node
```

The script will retrieve the account address associated with the name "user3" and execute the `goal account balance` command with the retrieved address and the specified data directory.

Note: Make sure to have the `name_to_address.py` script file in the same directory where you are running the command, or provide the full path to the script file if it is located elsewhere.

## Key Developments and Features
- **Automatic ASA Opt-in**
- **Vote Threshold Function**
- **Human-readable Addresses**
- **Original Voter Tracking**
- **Extensive Tests**
- **Dynamic Asset and App ID Management**

## Guide to Algorand Commands

- **Compile TEAL Scripts**: Use `goal clerk compile` with TEAL files.
- **Send Transactions**: Use `goal clerk send` specifying sender and receiver addresses.
- **Opt-in to ASA**: Mandatory for accounts to accept asset transfers.
- **Unfreeze ASA**: Necessary for transfers if the ASA is frozen.
- **Transfer ASA**: Use `goal asset send` with the asset ID and participant addresses.
- **Opt-in to Smart Contracts**: Required for accounts to interact with a contract.

## Documentation and Commit History
Explore the project's commits for detailed insights and development stages.

## Conclusion
This guide provides an in-depth look at setting up and testing on Algorand's private network, demonstrating the application's capabilities in a controlled blockchain environment.

## Note
For more detailed instructions and command references, see the provided `intro.md` file and the project's commit logs.

