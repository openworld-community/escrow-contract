from brownie import Escrow, accounts

def main() -> None:
    Escrow.deploy({'from': accounts[0], 'value': 100})
