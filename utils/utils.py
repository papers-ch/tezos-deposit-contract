from pytezos.operation.result import OperationResult

def get_address(pytezos_client, operation_hash):
    get_addresses(pytezos_client, operation_hash)[0]

def get_addresses(pytezos_client, operation_hash):
    while True:
        try:
            opg = pytezos_client.shell.blocks[-20:].find_operation(operation_hash)
            originated_contracts = OperationResult.originated_contracts(opg)
            return originated_contracts
        except:
            pass