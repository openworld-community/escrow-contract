from dotenv import load_dotenv
from brownie import accounts, escrow as Escrow, chain, factory as Factory
from vyper import compiler

load_dotenv(dotenv_path='.env')

ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

SEPOLIA_BLUEPRINT = '0xece858af6f3719eae599c0bcef0b098fabfe9ff3'


def main():
    acc = accounts.load('sepolia_deploy')
    blueprint = Factory.deploy(SEPOLIA_BLUEPRINT, {'from': acc.address})
    print(blueprint.address)

