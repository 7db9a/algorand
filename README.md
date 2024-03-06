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

