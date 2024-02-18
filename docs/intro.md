# Algorand Private Network Setup Guide

## Launching the Network

1. **Build Docker Image**:
   `docker build -t algorand .`

2. **Run Algorand Node**:
   `docker run -d -p 4190:8080 -p 4191:7833 --name my-algorand algorand-node`

However, if you're run this via the docker-compose in `../`,

`docker-compose build algorand`

and

`docker-compose up algorand`

## Compiling "Hello World" Smart Contract

Enter the algorand container.

1. **Create TEAL Script**:
   Save the following script as `hello_world.teal`:
   `#pragma version 2
   int 1`

2. **Compile TEAL Script**:
   `goal clerk compile hello_world.teal -d /algod/data/net1/Node`

## Deploying the Smart Contract

1. **List Accounts**:
   `goal account list -d /algod/data/net1/Primary`

2. **Get Account Mnemonic**:

   `goal account export -a <account_address> -d /algod/data/net1/Primary`

3. **Identify Sender Account**:
   Choose an account with a positive balance from the list.

4. **Send Transaction**:
   `goal clerk send -a 0 -f [SenderAccount] -t [ContractAddress] -d /algod/data/net1/Node`
   Replace `[SenderAccount]` with the sender account address and `[ContractAddress]` with the address of the compiled smart contract.

5. **Check Transaction**:
   `goal node status -d /algod/data/net1/Node`
   Compare the current round with the transaction round to ensure it's processed.

6. **Compile Teal File**:
   `goal clerk compile app_example.teal`
