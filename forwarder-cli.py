from pytezos import pytezos
from settings import settings
from utils.utils import get_addresses
import sys

pytezos_admin_client = pytezos.using(key=settings.ADMIN_KEY, shell=settings.SHELL)

def create_forwarders(number_of_adresses):
    deposit_manager = pytezos_admin_client.contract(settings.DEPOSIT_MANAGER)
    operation_group = deposit_manager.create_forwarders(callback=None, number_of_adresses=number_of_adresses).send()
    print("+----------------+")
    print(f"|    created {number_of_adresses} forwarders:   |")
    print("+----------------+")
    for address in get_addresses(pytezos_admin_client, operation_group.hash()):
        print(address)

def fa2_transfer(token_address, token_id):
    deposit_manager = pytezos_admin_client.contract(settings.DEPOSIT_MANAGER)
    token = pytezos_admin_client.contract(token_address)
    execution_payload = {}
    for forwarder in settings.FORWARDERS:
        balance = token.balance_of(requests=[{'owner':forwarder, "token_id": token_id}], callback=None).callback_view()[0]['balance']
        if balance > 0:
            execution_payload[forwarder] = f'{{ DROP; NIL operation; PUSH address "{token_address}"; CONTRACT %transfer (list (pair address (list (pair address (pair nat nat))))); IF_NONE {{ PUSH int 33; FAILWITH }} {{}}; PUSH mutez 0; NIL (pair address (list (pair address (pair nat nat)))); NIL (pair address (pair nat nat)); PUSH nat {balance}; PUSH nat {token_id}; PUSH address "{settings.POOL_ADDRESS}"; PAIR 3; CONS; SELF_ADDRESS; PAIR; CONS; TRANSFER_TOKENS; CONS }}'          
    deposit_manager.bulk_execute(execution_payload).send()
  

def fa1_transfer(token_address):
    deposit_manager = pytezos_admin_client.contract(settings.DEPOSIT_MANAGER)
    token = pytezos_admin_client.contract(token_address)
    execution_payload = {}
    for forwarder in settings.FORWARDERS:
        try:
            balance = token.getBalance((forwarder, None)).callback_view()
            if balance > 0:
                execution_payload[forwarder] = f'{{ DROP; NIL operation; PUSH address "{token_address}"; CONTRACT %transfer (pair address (pair address nat)); IF_NONE {{ PUSH int 19; FAILWITH }} {{}}; PUSH mutez 0; PUSH nat {balance}; PUSH address "{settings.POOL_ADDRESS}"; SELF_ADDRESS; PAIR 3; TRANSFER_TOKENS; CONS }}'
        except:
            pass
    deposit_manager.bulk_execute(execution_payload).send()

if __name__ == '__main__':
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    if "-c" in opts:
        create_forwarders(int(args[0]))
    if "-fa1" in opts:
        fa1_transfer(args[0])
    if "-fa2" in opts:
        fa2_transfer(args[0], args[1])