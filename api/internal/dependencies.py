import os
from web3 import Web3, HTTPProvider
from dotenv import load_dotenv

load_dotenv()

web3 = Web3(HTTPProvider(os.getenv("WEB3_PROVIDER")))
