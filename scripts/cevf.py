from brownie import accounts, factory as Factory, web3 as w3
from vyper import compiler

SEPOLIA_FACTORY = "0x5147c6333888F079D831f84691fa9c72c25441C9"


ABI = '[{"name": "EscrowCreated", "inputs": [{"name": "contract", "type": "address", "indexed": false}, {"name": "seller", "type": "address", "indexed": true}, {"name": "buyer", "type": "address", "indexed": true}, {"name": "value", "type": "uint256", "indexed": false}, {"name": "expiration_time", "type": "uint256", "indexed": false}], "anonymous": false, "type": "event"}, {"stateMutability": "nonpayable", "type": "constructor", "inputs": [{"name": "_blueprint", "type": "address"}], "outputs": []}, {"stateMutability": "nonpayable", "type": "function", "name": "create_escrow", "inputs": [{"name": "_seller", "type": "address"}, {"name": "_buyer", "type": "address"}, {"name": "_arbiter", "type": "address"}, {"name": "_value", "type": "uint256"}, {"name": "_expiration_seconds", "type": "uint256"}], "outputs": [{"name": "", "type": "address"}]}, {"stateMutability": "view", "type": "function", "name": "owner", "inputs": [], "outputs": [{"name": "", "type": "address"}]}, {"stateMutability": "view", "type": "function", "name": "blueprint", "inputs": [], "outputs": [{"name": "", "type": "address"}]}]'


def main():
    acc = accounts.load('sepolia_deploy')

    print(acc.address)

    f = w3.eth.contract(address=SEPOLIA_FACTORY, abi=ABI)

    deploy_transaction = f.functions.create_escrow(
        "0xBa2EE64811De3fB0bceF1fB1d18aCC7CA91f8950",
        "0xf443077E564Bd46156D1CAfc9c89227aD8E023b1",
        "0xf443077E564Bd46156D1CAfc9c89227aD8E023b1",
        0,
        0
    ).buildTransaction({
        "chainId": 11155111,
        "nonce": w3.eth.get_transaction_count(acc.address),
        "from": acc.address,
    })

    tx_create = w3.eth.account.sign_transaction(
        deploy_transaction, acc.private_key)

    tx_hash = w3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f'Contract deployed at address: { tx_receipt["transactionHash"] }')
