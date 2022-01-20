from settings import settings
from utils.utils import get_address
from pytezos import pytezos, ContractInterface



def deploy_deposit_manager(pool_address, baker):
    pytezos_admin_client = pytezos.using(key=settings.ADMIN_KEY, shell=settings.SHELL)
    administrator = pytezos_admin_client.key.public_key_hash()
    
    print("Starting DepositManager deployment...")
    deposit_manager_code = ContractInterface.from_file('out/DepositManager/step_000_cont_0_contract.tz')
    storage = deposit_manager_code.storage.dummy()

    storage['administrators'] = {administrator:None}
    storage['baker'] = baker
    storage['pool_address'] = pool_address

    operation_group = pytezos_admin_client.origination(script=deposit_manager_code.script(initial_storage=storage)).send()
    deposit_manager_address = get_address(pytezos_admin_client, operation_group.hash())
    print("done: '{}'".format(deposit_manager_address))

if __name__ == '__main__':
    deploy_deposit_manager(settings.POOL_ADDRESS, None)
