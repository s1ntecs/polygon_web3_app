from web3 import Web3
from web3.middleware import geth_poa_middleware
from backend.settings import CONTRACT_ADDRESS, POLYGON_RPC_URL
from eth_typing import ChecksumAddress
from data.abi import erc20_abi


class Web3Initializer:
    def __init__(self):
        self.web3 = None
        self.contract_address = None
        self.contract = None
        self.error = None
        self.initialize()

    def initialize(self):
        try:
            self.web3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))
            self.web3.middleware_onion.inject(
                geth_poa_middleware, layer=0)

            self.contract_address: ChecksumAddress = \
                self.web3.toChecksumAddress(CONTRACT_ADDRESS)
            self.contract = self.web3.eth.contract(
                address=self.contract_address, abi=erc20_abi)
        except Exception as e:
            self.error = str(e)
            print(f"Ошибка при инициализации Web3: {self.error}")


web3_initializer = Web3Initializer()
web3 = web3_initializer.web3
contract = web3_initializer.contract
initialization_error = web3_initializer.error
