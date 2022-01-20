# Depost Contracts

The deposit contract allows funds to be forwarded to a pool adress while still allowing an individual adress per user.

## Build/Basic Usage

### Dependencies

This project depends only on SmartPy (which depends on python and node), you can install SmartPy by doing a:

```
$ sh <(curl -s https://smartpy.io/releases/20210604-7f97dba13e914cb1915b7cea16b844208abf51e9/cli/install.sh)
```

You can read more about the installation here: https://smartpy.io/cli/

If you want to compile docs and deploy you also will need a sphinx and pytezos, these are the dependencies:

```
apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends python3-pip libsodium-dev libsecp256k1-dev
pip3 install sphinx pytezos
```

There is a ".devcontainer" which creates a dockerized environment and installs everything needed for you. You can checkout ".devcontainer/Dockerfile" to understand
the dependencies. I.e. VSCode will just ask you to open in container and within 5 minutes you are good to go.

Please note that in order to be able to "find" the Python modules you will have to export "PYTHONPATH" to include the main smartpy folder _and_ this very folder.

```
export PYTHONPATH=/home/node/smartpy-cli/:$(pwd)
```

The command above expects you to be on the root of this project and smartpy-cli to be installed in /home/node/smartpy-cli/. Also while you are at it, might aswell 
export the smartpy PATH.

```
export PATH=$PATH:/home/node/smartpy-cli/
```

## Testing

The tests are easiest to run using 

```
cd deposit
SmartPy.sh test deposit.py out --html
```

## Configuring

For deployment and CLI you will have to adapt settings.py the following way:

```
# settings.py example
POOL_ADDRESS = "tz1N5tn67kgiXRKSVmpmjzdvffwQ9Xu1bt7G" # this is where the money will be forwarded too.
DEPOSIT_MANAGER = "KT1GHBvGfhK211v5BdfFS1Rvkg4YGj3wrXEJ" # this is used for the CLI but will be blank if nothing is deployed yet.

SHELL = "https://hangzhounet.smartpy.io/" # use a tezos node RPC
ADMIN_KEY = "edsk..." # your account used for interaction and deployment of contracts

FORWARDERS = [
    "KT1WdUTQBgutLb1rXeZ4CQAwSfpJiB4bd1TC", # these come from the CLI output -c
    "KT1QYLGVNB2v4mYCPT5mq3YmNQGKLroAukMn", 
    "KT1WRXJGcPZVkqvq4kifBpGMRqEA12PkKfmR", 
    "KT1HytFzxcfJ2sxmUUh6uDuYjkNJCnE9cb8W"
]
```

## Deployment

Make sure you have specified `ADMIN_ADDRESS`, `POOL_ADDRESS`, `SHELL` and `ADMIN_KEY` in the settings.py

SmartPy.sh allows to easily deploy the contract using

```
SmartPy.sh compile compiler.py out
python3 deployments/deploy_deposit_manager.py 
```

The new contract address can then be used as `DEPOSIT_MANAGER`.

## Using the CLI

Make sure you have specified `ADMIN_ADDRESS`, `POOL_ADDRESS`, `DEPOSIT_MANAGER`, `SHELL` and `ADMIN_KEY` in the settings.py

You can then create new contracts using 

```
python3 forwarder-cli.py -c <number of forwarders>
```

You will then be able to configure `FORWARDERS` with the freshly created contracts shown in the cli output.

So if you want to create 3 new forwarding adresses do a:

```
python3 forwarder-cli.py -c <number of forwarders>
```

You can transfer all tokens of a specific fa1 contract with:

```
python3 forwarder-cli.py -fa1 <token contract address>
```

You can transfer all tokens of a specific fa2 contract with:

```
python3 forwarder-cli.py -fa2 <token contract address> <token id>
```
