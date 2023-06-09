from eth_account.messages import encode_defunct
from brownie import accounts, web3 as w3

def main():
    # Generate the message
    acc = accounts.load('sepolia_deploy')
    msg = "helloworld"
    message = encode_defunct(text=msg)
    signed_message = w3.eth.account.sign_message(message, private_key=acc.private_key)
    print(acc)
    print(msg)
    print(w3.toHex((signed_message['signature'])))
