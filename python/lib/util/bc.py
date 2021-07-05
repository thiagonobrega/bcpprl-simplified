from web3.middleware import geth_poa_middleware

def checkAllBalances(web3):
    accts = []
    for acc in web3.eth.accounts:
        acc_bal = web3.eth.getBalance(acc)
        accts.append((acc,int(web3.fromWei(acc_bal, "ether")),acc_bal))
    return accts


def transfer(web3,src,dst,amount_ether):
    # transfer(web3, web3.eth.accounts[1], web3.eth.accounts[2], 5)
    web3.personal.unlockAccount(src, '', 0)
    amount = web3.toWei(amount_ether, "ether")
    transction = {'to': dst, 'from': web3.eth.coinbase, 'value': amount}
    return web3.eth.sendTransaction(transction)


def configure_poa_env(web3):
    #https://web3py.readthedocs.io/en/stable/middleware.html#geth-style-proof-of-authority
    web3.middleware_stack.inject(geth_poa_middleware, layer=0)
    return web3

###
def getTranscationInfot(web3,tx_hash):
    return web3.eth.getTransaction(tx_hash)
###
def registration_onboarding(web3,account,unique_key):
    hash_op = web3.sha3('password')
    signature = web3.eth.sign(account,hash_op)
    return signature