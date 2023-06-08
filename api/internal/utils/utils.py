import random
import string

NONCE_LEN = 10


def generate_random_nonce() -> str:
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(NONCE_LEN))
