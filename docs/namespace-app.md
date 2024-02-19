# Namespace App

The Namespace app is a smart contract for the Algorand blockchain. It's designed to store and manage information about a repository, such as its name and URL. This documentation guides you through compiling, deploying, and interacting with this smart contract.

## Summary of Components

1. **namespace.py**: This Python script uses PyTeal to define the smart contract's logic. It includes two main parts:
   - **Approval Program**: Sets the rules for transactions that the contract will allow. It's used to initialize the contract with repository details and to update these details.
   - **Clear State Program**: Defines what happens when a user decides to opt-out of the contract.

2. **namespace_deploy.py**: A Python script for deploying the smart contract on the Algorand network. It handles creating, updating, and deleting the contract, as well as reading its global state (the stored information).

## Deploy App

### Compile PyTeal to TEAL

Convert the PyTeal code (a Python-based language for Algorand smart contracts) into TEAL (Transaction Execution Approval Language), which is the low-level language that Algorand's blockchain understands.

```
docker-compose exec -it algorand \
python \
/algod/experiments/namespace_app/namespace.py
```

### Send Contract TEAL Code to Algorand

This step involves "compiling" the TEAL code. It prepares the TEAL scripts (created in the previous step) to be deployed to the Algorand blockchain. This is akin to packaging the contract before it's launched.

```
docker-compose exec -it algorand \
goal clerk compile \
/algod/experiments/namespace_app/namespace_approval_program.teal

docker-compose exec -it algorand \
goal clerk compile \
/algod/experiments/namespace_app/namespace_clear_state_program.teal
```

### Deploy and Run Contract

Deploy the smart contract to the Algorand network. This step officially puts your contract on the blockchain, allowing it to start processing transactions according to its defined rules.

```
docker-compose exec -it algorand \
python \
/algod/experiments/namespace_app/namespace_deploy.py
```

### Read the State of the Contract

After deploying the contract, you can query its state. This lets you verify that the contract was deployed correctly and is functioning as expected.

```
docker-compose exec -it algorand \
python \
/algod/experiments/namespace_app/namespace_read_global_state.py
```

