from brownie import accounts, factory as Factory, web3 as w3
from vyper import compiler

SEPOLIA_BLUEPRINT = '0x2228283f5682AeE138a566C80fC8911de6BC91c2'

def main():
    acc = accounts.load('sepolia_deploy')
    print("Account address:", acc.address)

    code = ""
    with open("contracts/factory.vy", encoding="utf8") as f:
        code = f.read()

    out = compiler.compile_code(code, ["abi", "bytecode"])

    abi = out['abi']

    deploy_tx = w3.eth.contract(
        abi=abi, bytecode=out['bytecode']
    ).constructor(SEPOLIA_BLUEPRINT).buildTransaction({
        "chainId": 11155111,
        "nonce": w3.eth.get_transaction_count(acc.address),
        "from": acc.address,
    })

    tx_create = w3.eth.account.sign_transaction(deploy_tx, acc.private_key)

    tx_hash = w3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print("Factory created", tx_receipt["contractAddress"])
