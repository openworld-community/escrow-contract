import random
import string

from web3 import Web3
from eth_account.messages import encode_defunct

NONCE_LEN = 10


def generate_random_nonce() -> str:
    return ''.join(
        random.SystemRandom().choice(
            string.ascii_uppercase + string.digits
        ) for _ in range(NONCE_LEN)
    )

def verify_signature(addr: str, sig: str, msg: str) -> bool:
    w3 = Web3(Web3.HTTPProvider(""))
    message = encode_defunct(text=msg)
    signed_address = (w3.eth.account.recover_message(message, signature=sig)).lower()
    print(f"message: {message}")
    print(f"signed address: {signed_address}")
    return signed_address == addr.lower()
