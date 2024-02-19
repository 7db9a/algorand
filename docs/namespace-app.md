# Namespace app

## Deploy app

Compile pyteal app to teal.
```
docker-compose exec -it algorand \
python \
/algod/experiments/namespace.py

docker-compose exec -it algorand \
python \
/algod/experiments/namespace_namespace.py
```

Send contract teal code to algorand.
```
docker-compose exec -it algorand \
goal clerk compile \
namespace_approval_program.teal

docker-compose exec -it algorand \
goal clerk compile \
goal clerk compile namespace_clear_state_program.teal
```
Deploy and run contract basic write and read example.
```
docker-compose exec -it algorand \
python \
/algod/experiments/namespace_deploy.py
```

To read the state of the contract.

```
docker-compose exec -it algorand \
python \
/algod/experiments/namespace_read_global_state.py
```
