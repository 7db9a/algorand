# Algorand Private Network Setup Guide

## Launching the Network

1. **Build Docker Image**:
   `docker build -t algorand .`

2. **Run Algorand Node**:
   `docker run -d -p 4190:8080 -p 4191:7833 --name my-algorand algorand-node`

However, if you're run this via the docker-compose in `../`,

`docker-compose build algorand`

and

`docker-compose up -d algorand`

## Find your algod token instance

   `cat /algod/data/net1/Primary/algod.token`

## Compiling "Hello World" Smart Contract

Enter the algorand container.

## Commands, algorand

Note: Replace `<Primary or Node>` with either `Primary` or `Node` based on your Algorand node configuration.

**Create TEAL Script**:
Save the following script as `hello_world.teal`:

``
#pragma version 2
int 1
``

**Compile TEAL Script**:
```
goal clerk compile hello_world.teal -d /algod/data/net1/<Primary or Node>
```

Note you can choose to interact with `Primary` or `Node` instance algod.

## Deploying the Smart Contract

**List Accounts**:
```
goal account list -d /algod/data/net1/Primary
```

**Get Account Info**:
```
goal account info --address [Account Address] -d [data directory]
```

**Get Account Mnemonic**:
``
goal account export -a <account_address> -d /algod/data/net1/<Primary or Node>
``

**Identify Sender Account**:
Choose an account with a positive balance from the list.

**Send Transaction**:
``
goal clerk send -a 0 -f [SenderAccount] -t [ContractAddress] -d /algod/data/net1/<Primary or Node>
``
Replace `[SenderAccount]` with the sender account address and `[ContractAddress]` with the address of the compiled smart contract.

**Check Transaction**:
``
goal node status -d /algod/data/net1/<Primary or Node>
``
Compare the current round with the transaction round to ensure it's processed.

**Compile Teal File**:
``
goal clerk compile app_example.teal
``

**OptIn ASA**

Accounts must opt-in to asa's to be able to accept transfer.

```
goal asset send -a 0 --assetid [Asset ID] --from [Receiver's Address] --to [Receiver's Address]
```

**Unfreeze ASA**

The freeze address must unfreeze any asa of an account for a transfer to work.

```
goal asset freeze --assetid [Asset ID] --freezer [Freeze Account Address] --account [Target Account Address] --freeze=false -d /algod/data/net1/<Primary or Node>
```

Note: `--freeze=true` freezes the account's asa.

**Transfer an Asa**

```
goal asset send -a [Amount] --assetid [Asset ID] --from [Sender's Address] --to [Receiver's Address] -d /algod/data/net1/<Primary or Node>
```
If the sender's account is protected by a passphrase, you will need to enter it to sign the transaction.

**OptIn Contract**

Accounts must opt-in to contracts to interact with it.

```
goal app optin --app-id [App ID] --from [Account Address]
```
