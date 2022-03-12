# Deposit Contract Entrypoints

This document contains a description of all the entrypoints in the Deposit System Smart Contract.

## Admin only entrypoints
These entrypoints can only be called by an admin of the contract.

- set_administrator
- remove_administrator
- create_forwarders
- bulk_execute

The forwarder is the actual user account that gets an individual address, but is only controllable by the Deposit Contract. The relation is 1-n. 

### Set Administrator
- **entrypoint**: def set_administrator(self, administrator_to_set)
- **arguments**: administrator_to_set: sp.TAddress
- **description**: entrypoint used to set a new administrator, the parameter address is the new admin to set. Only an existing admin can call this.

### Remove Administrator
- **entrypoint**: def remove_administrator(self, administrator_to_remove)
- **arguments**: administrator_to_remove: sp.TAddress
- **description**: entrypoint used to remove an existing administrator, the parameter address is the admin to remove. Only an existing admin can call this. Warning: as an admin you can remove yourself.


### Bulk Execute
- **entrypoint**:  def bulk_execute(self, execution_payloads)
- **arguments**:
    - execution_payloads:  sp.TMap(sp.TAddress, sp.TLambda(sp.TUnit, sp.TList(sp.TOperation)))
- **description**: entrypoint used to execute in the name of the contract the lambda stored in the execution payload map on the given adresses. The admin calls this method and this metho is executed on the forwarders.

### Create Forwarders
- **entrypoint**:  def create_forwarders(self, number_of_adresses, callback)
- **arguments**: 
    - number_of_adresses: sp.TNat
    - callback: sp.TOption(sp.TContract(sp.TList(sp.TAddress)))
- **description**: entrypoint used to generate/create new forwarders. The number_of_addresses parameter decides on the count of contracts to create. If set the callback will return a list of adresses that were created in this invocation. Only an existing admin can call this. Only admin can do this.