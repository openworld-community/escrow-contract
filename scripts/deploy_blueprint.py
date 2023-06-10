import sys

from dotenv import load_dotenv
from brownie import accounts, escrow as Escrow, chain, factory as Factory, web3
from vyper import compiler

load_dotenv(dotenv_path='.env')

ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'


def blueprint_deployer_bytecode(initcode: bytes) -> bytes:
    blueprint_preamble = b"\xFE\x71\x00"  # ERC5202 preamble
    blueprint_bytecode = blueprint_preamble + initcode

    # the length of the deployed code in bytes
    len_bytes = len(blueprint_bytecode).to_bytes(2, "big")

    # copy <blueprint_bytecode> to memory and `RETURN` it per EVM creation semantics
    # PUSH2 <len> RETURNDATASIZE DUP2 PUSH1 10 RETURNDATASIZE CODECOPY RETURN
    deploy_bytecode = b"\x61" + len_bytes + b"\x3d\x81\x60\x0a\x3d\x39\xf3"

    return deploy_bytecode + blueprint_bytecode


def main():
    acc = accounts.load('sepolia_deploy')

    print(acc.address)

    code = ""
    with open("contracts/escrow.vy", encoding="utf8") as f:
        code = f.read()

    c_out = compiler.compile_code(
        code, ["abi", "bytecode", "blueprint_bytecode"])

    abi = c_out['abi']
    bytecode = c_out['blueprint_bytecode']

    c = web3.eth.contract(abi=abi, bytecode=bytecode)

    deploy_transaction = c.constructor(
        "0xBa2EE64811De3fB0bceF1fB1d18aCC7CA91f8950",
        "0xBa2EE64811De3fB0bceF1fB1d18aCC7CA91f8950",
        "0xBa2EE64811De3fB0bceF1fB1d18aCC7CA91f8950",
        1000000,
        86400
    ).buildTransaction({
        "chainId": 11155111,
        "nonce": web3.eth.get_transaction_count(acc.address),
        "from": acc.address,
    })

    tx_create = web3.eth.account.sign_transaction(
        deploy_transaction, acc.private_key)

    tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    print(f'Contract deployed at address: { tx_receipt.contractAddress }')
