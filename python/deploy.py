import time

from web3 import Web3, HTTPProvider
from solcx import compile_files, link_code , compile_standard
from solcx import get_installed_solc_versions, set_solc_version

from lib.util.env import getbase_dir

def get_input_json(file_path,file,lib,ldlib):
    # https://solidity.readthedocs.io/en/v0.5.3/using-the-compiler.html
    if lib == None:
        input_json =  {
                    "language": "Solidity",
                    "sources": {
                                    str(file): {
                                    "urls": [
                                        str(file_path+file)
                                    ]
                                    }
                                },
                    "settings": {
                                    "optimizer": {
                                        "enabled": True,
                                        "runs": 200
                                    },
                                    "outputSelection": {
                                                str(file) : {
                                                            "*": [
                                                            "metadata",
                                                            "abi",
                                                            "evm.bytecode",
                                                            "evm.sourceMap"]
                                                            }
                                    }
                                }

        }
    else:
        input_json =  {
                    "language": "Solidity",
                    "sources": {
                                    str(file): {
                                    "urls": [
                                        str(file_path+file)
                                    ]
                                    },
                                    str(lib): {
                                    "urls": [
                                        str(file_path+lib)
                                    ]
                                    }
                                },
                    "settings": {
                                    "optimizer": {
                                        "enabled": True,
                                        "runs": 200
                                    },
                                    "metadata": {
                                        "useLiteralContent": True
                                    },
                                    "libraries": {
                                        str(file): {
                                        str(list(ldlib.keys())[0]):str(ldlib[list(ldlib.keys())[0]])
                                        }
                                    },
                                    "outputSelection": {
                                                str(file) : {
                                                            "*": [
                                                            "metadata",
                                                            "abi",
                                                            "evm.bytecode",
                                                            "evm.sourceMap"]
                                                            }
                                    }
                                }

        }
    return input_json


def compileContract(file,lib=None,ldlib=None,file_path="Contracts"):
    file_path = getbase_dir(file_path)

    input_json = get_input_json(file_path,file,lib,ldlib)
    set_solc_version('v0.5.4')
    # return compile_files([file_path+file])
    return compile_standard(input_json, allow_paths=file_path)

def createInstaceContract(w3,file,contract_name):
    compiled_contract = compileContract(file)
    cbytecode = compiled_contract['contracts'][file][contract_name]['evm']['bytecode']['object']
    cabi = compiled_contract['contracts'][file][contract_name]['abi']
    return w3.eth.contract(abi=cabi,bytecode=cbytecode)

def deployContract(account,file,contract,contract_name,web3,library_address=None):
    # unlocck account
    web3.personal.unlockAccount(account,'', 0)

    cbytecode = contract['contracts'][file][contract_name]['evm']['bytecode']['object']
    cabi = contract['contracts'][file][contract_name]['abi']

    # Link Contract with code
    if library_address != None:
        cbytecode = link_code(cbytecode, library_address)

    instanceContract = web3.eth.contract(abi=cabi,
                                        bytecode=cbytecode)

    # caso seja necessario utilizar o compilado
    # instanceContract = readCompiledContractData(contract_name,web3)

    #deploy contract
    tx_hash = instanceContract.constructor().transact({'from': account, 'gas': 1000000})
    # tx_hash = instanceContract.constructor().transact({'from': account})

    tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
    iter_count = 1

    while tx_receipt == None or iter_count < 30:
        print("Trying.. " + str(iter_count) + "/30 ..." )
        time.sleep(2)
        tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
        iter_count+=1

    if tx_receipt == None:
        import sys
        print("Aborting!!!")
        sys.exit()

    contract_address = tx_receipt['contractAddress']
    # contract_address

    cc = web3.eth.contract(
        address=contract_address,
        abi=instanceContract.abi,
    )

    return cc


def deployContractInfura(w3,mycontract,file,contract_name,privateKey='A0AC3B5859D53'):

    acct = w3.eth.account.privateKeyToAccount(privateKey)

    construct_txn = mycontract.constructor().buildTransaction({
        'from': acct.address,
        'nonce': w3.eth.getTransactionCount(acct.address),
        'gas': 6612388,
        'gasPrice': w3.eth.gasPrice})
    # 10000000000
    # 'gasPrice': w3.toWei('21', 'gwei')})

    signed = acct.signTransaction(construct_txn)
    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
    print(tx_hash)

    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    iter_count = 1

    while tx_receipt == None or iter_count < 30:
        print("Trying.. " + str(iter_count) + "/30 ...")
        time.sleep(2)
        tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
        iter_count += 1

    contract_address = tx_receipt['contractAddress']

    return w3.eth.contract(address=contract_address,abi=mycontract.abi)


if __name__ == "__main__":
    import sys

    # web3=Web3(HTTPProvider('http://localhost:8545'))
    # remote
    # web3 = Web3(HTTPProvider('http://192.168.0.100:8545'))
    account = web3.eth.accounts[1]



    print("Start deploying lib")
    sfile = 'pprl_lib.sol'
    compC = compileContract(sfile)
    
    libName = 'ComparisonTool'

    cc = deployContract(account,sfile,compC,libName,web3)
    print(cc)

    library_address = {
        str(libName): str(cc.address)
    }

    # library_address = {
    #     "stringUtils.sol:StringUtils": deploy_contract(library_link)
    # }

    sfile = 'cc3.sol'
    compC = compileContract(sfile,lib='pprl_lib.sol',ldlib=library_address)
    cName = 'ComparasionClassification'
    

    
    # cbytecode = compC['contracts'][sfile][cName]['evm']['bytecode']['object']
    # cbytecode = link_code(cbytecode, library_address)
    # cn = deployContract(account,'cc2.sol',compC,cName,web3,library_address=library_address)
    
    cn = deployContract(account,'cc3.sol',compC,cName,web3)

    #transaction
    web3.personal.unlockAccount(account,'', 0)
    transaction={'from': account, 'gas': 1000000, 'to': cn.address}
    cn.functions.compareEntities(bytes([1]),bytes([3])).call(transaction)
    cn.functions.compareEntities(bytes([1]),bytes([3])).transact(transaction)
    sys.exit(10)
