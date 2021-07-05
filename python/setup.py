import time, sys

from web3 import Web3, HTTPProvider
from solcx import compile_files, link_code , compile_standard
from solcx import get_installed_solc_versions, set_solc_version

from lib.util.env import getbase_dir
from deploy import createInstaceContract

if __name__ == "__main__":
    
    #print("Anonnymizing entities..")
    #encrypted_entities = encrypt_data('bikes', 'candset.csv', 96)
    #print("Setup BC-Connection")


    # w3 = Web3(HTTPProvider("https://ropsten.infura.io/v3/ae955aa167d1467b94a59729f7b5770d"))
    w3 = Web3(HTTPProvider("https://rinkeby.infura.io/v3/ae955aa167d1467b94a59729f7b5770d"))

    account = '0xfCBb70E6983e2a24c7Ee392D598A3060bAE95096'


    ######################################################
    ## Oracle contract
    ######################################################
    cFile = 'oracles/simpleOracle2.sol'
    cName = 'ExampleContract'
    print("Compiling SmartContracts")
    compiledContract = createInstaceContract(w3,cFile,cName)

    print("Deploying SmartContracts")
    from deploy import deployContractInfura
    smc = deployContractInfura(w3,compiledContract,cFile,cName)

    ######################################################
    ## CCC contract
    ######################################################
    cFile = '/v2/ccc.sol'
    cName = 'ComparasionClassification'
    print("Compiling SmartContracts")
    compiledContract = createInstaceContract(w3, cFile, cName)
    deployedSC = deployContractInfura(w3, compiledContract, cFile, cName)



##0x1d4797ed41e1c0bcdcd076cde30ea09a5878fc0c
##0xfCBb70E6983e2a24c7Ee392D598A3060bAE95096