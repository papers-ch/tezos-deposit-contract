import smartpy as sp

class Errors:
    NOT_ADMIN = 401
    
class Forwarder(sp.Contract):
    def get_init_storage(self):
        return dict(
            administrator = sp.set_type_expr(self.administrator, sp.TAddress),
            recipient = sp.set_type_expr(self.recipient, sp.TAddress)
        )
    
    def __init__(self, administrator, recipient):
        self.administrator = administrator
        self.recipient = recipient
        self.init(**self.get_init_storage())
        
    @sp.entry_point
    def default(self):
        """default entrypoint will automatically forward the funds to the set recipient
        Post: send(sp.amount, storage.recipient)
        """
        sp.send(self.data.recipient, sp.balance)
    
    @sp.entry_point
    def execute(self, execution_payload):
        """Only an admin can call this entrypoint. It executes in the name of the contract the lambda stored in the execution payload.
        This is used for FA1.2 and FA2 deposist.
        Pre: storage.administrator == sp.sender
        Post: push execution_payload on execution stack

        Args:
            execution_payload (sp.TLambda(sp.TUnit, sp.TList(sp.TOperation))): the lambda to execute
        """
        sp.set_type(execution_payload, sp.TLambda(sp.TUnit, sp.TList(sp.TOperation)))
        sp.verify(self.data.administrator == sp.sender, message=Errors.NOT_ADMIN)
        sp.add_operations(execution_payload(sp.unit).rev())

class AdministrableMixin():
    """Mixin used to compose andministrable functionality of a contract. Still requires the inerhiting contract to define the apropiate storage.
    """

    @sp.sub_entry_point
    def verify_is_admin(self, unit):
        """Sub entrypoint which verifies if a sender is in the set of admins
        Pre: storage.administrators.contains(LedgerKey(sp.sender, token_id))

        """
        sp.set_type(unit, sp.TUnit)
        sp.verify(self.data.administrators.contains(sp.sender), message=Errors.NOT_ADMIN)

    @sp.entry_point
    def set_administrator(self, administrator_to_set):
        """Only an existing admin can call this entrypoint. If the sender is correct the new admin is set
        Pre: verify_is_admin()
        Post: storage.administrators[LedgerKey(administrator_to_set, token_id)] = sp.unit

        Args:
            administrator_to_set (sp.address): the administrator that should be set
        """
        sp.set_type(administrator_to_set, sp.TAddress)
        self.verify_is_admin(sp.unit)
        self.data.administrators[administrator_to_set] = sp.unit

    @sp.entry_point
    def remove_administrator(self, administrator_to_remove):
        """Only an existing admin can call this entrypoint. This removes a administrator entry entirely from the map (even the executing admin if requested)
        Pre: verify_is_admin()
        Post: del storage.administrators[administrator_to_remove]

        Args:
            administrator_to_remove (sp.address): the administrator that should be removed
        """
        sp.set_type(administrator_to_remove, sp.TAddress)
        self.verify_is_admin(sp.unit)
        del self.data.administrators[administrator_to_remove]

class DepositManager(sp.Contract, AdministrableMixin):
    def get_init_storage(self):
        return dict(
            administrators=sp.big_map(l=self.administrators, tkey=sp.TAddress, tvalue=sp.TUnit),
            baker= self.baker,
            pool_address = self.pool_address
        )
    
    def __init__(self, administrators, pool_address, baker):
        self.administrators = administrators
        self.pool_address = pool_address
        self.baker = baker
        self.init(**self.get_init_storage())

    @sp.entry_point
    def create_forwarders(self, number_of_adresses, callback):
        sp.set_type(number_of_adresses, sp.TNat)
        sp.set_type(callback, sp.TOption(sp.TContract(sp.TList(sp.TAddress))))

        self.verify_is_admin(sp.unit)
        adresses = sp.local("responses", sp.set_type_expr(sp.list([]), sp.TList(sp.TAddress)))
        with sp.for_('i', sp.range(0, number_of_adresses)) as i:
            adresses.value.push(sp.create_contract(Forwarder(sp.to_address(sp.self), self.data.pool_address), baker=self.data.baker))
        with sp.if_(callback.is_some()):
            sp.transfer(adresses.value, sp.mutez(0), callback.open_some())
        
    @sp.entry_point
    def bulk_execute(self, execution_payloads):
        sp.set_type(execution_payloads, sp.TMap(sp.TAddress, sp.TLambda(sp.TUnit, sp.TList(sp.TOperation))))

        self.verify_is_admin(sp.unit)
        with sp.for_('execution_payload', execution_payloads.items()) as execution_payload:
            forwarder_contract = sp.contract(sp.TLambda(sp.TUnit, sp.TList(sp.TOperation)), execution_payload.key, entry_point="execute").open_some()
            sp.transfer(execution_payload.value, sp.mutez(0), forwarder_contract)
        
@sp.add_test(name = "Lambdas")
def test():    
    class Viewer(sp.Contract):
        def __init__(self):
            self.init(
                addresses = sp.list([], t=sp.TAddress),
                nat = sp.nat(0)
            )
        
        @sp.entry_point
        def set_nat(self, nat):
            self.data.nat = nat
            
        @sp.entry_point
        def set_addresses(self, addresses):
            self.data.addresses = addresses
    
    def dummy_lambda(unit):
        sp.set_type(unit, sp.TUnit)
        sp.result(
            sp.list([])
        )

    chain_id=sp.chain_id_cst("0x9caecab9")
    scenario = sp.test_scenario()
    scenario.h1("Generic Multi Signature Executor")
    scenario.table_of_contents()
    
    admin = sp.test_account("Administrator")
    alice = sp.test_account("Alice")
    bob = sp.test_account("Robert")
    dan = sp.test_account("Dan")
    
    # Let's display the accounts:
    scenario.h2("Accounts")
    scenario.show([admin, alice, bob, dan])
    
    admin = sp.test_account("Administrator")    

    deposit_manager = DepositManager({admin.address:sp.unit}, alice.address, sp.none)
    scenario += deposit_manager

    viewer = Viewer()
    scenario += viewer

    forwarder = Forwarder(deposit_manager.address, alice.address)
    scenario += forwarder
    
    return_contract = sp.contract(sp.TList(sp.TAddress), viewer.address, entry_point="set_addresses").open_some()
    
    scenario.h2("Deposit Manager tests")
    scenario.p("Non Admin fails forwarder creation")
    scenario += deposit_manager.create_forwarders(number_of_adresses=10, callback=sp.some(return_contract)).run(valid=False, sender=bob)

    scenario.p("Admin creates forwarders")
    scenario += deposit_manager.create_forwarders(number_of_adresses=10, callback=sp.some(return_contract)).run(valid=True, sender=admin)

    scenario.p("Non Admin fails execution")
    scenario += deposit_manager.bulk_execute({forwarder.address:dummy_lambda}).run(valid=False, sender=bob)

    scenario.p("Admin succeeds with execution")
    scenario += deposit_manager.bulk_execute({forwarder.address:dummy_lambda}).run(valid=True, sender=admin)

    scenario.p("Non Admin tries set admin")
    scenario += deposit_manager.set_administrator(bob.address).run(valid=False, sender=bob)

    scenario.p("Admin tries set admin")
    scenario += deposit_manager.set_administrator(bob.address).run(valid=True, sender=admin)

    scenario.p("New Admin sets next admin")
    scenario += deposit_manager.set_administrator(alice.address).run(valid=True, sender=bob)

    scenario.p("New Admin removes set admin")
    scenario += deposit_manager.remove_administrator(alice.address).run(valid=True, sender=bob)

    scenario.p("New Admin removes himself")
    scenario += deposit_manager.remove_administrator(bob.address).run(valid=True, sender=bob)

    scenario.p("Removed admin cannot remove anymore")
    scenario += deposit_manager.remove_administrator(admin.address).run(valid=False, sender=bob)

    scenario.h2("Forwarder tests")
    scenario.p("Non admin cannot execute")
    scenario += forwarder.execute(dummy_lambda).run(valid=False, sender=admin)

    scenario.p("Admin can execute")
    scenario += forwarder.execute(dummy_lambda).run(valid=True, sender=deposit_manager.address)