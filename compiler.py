import smartpy as sp

import deposit.constants as Constants
from deposit.deposit import DepositManager

def main():
    """
    This file is used for compiling all contract such that the :obj:`deployments` module can then be used to deploy and wire everything.
    """
    sp.add_compilation_target("DepositManager", DepositManager({}, Constants.DEFAULT_ADDRESS, sp.none))
    

if __name__ == '__main__':
    main()
