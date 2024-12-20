import json
import logging

import web3 as lol
from eth_account import Account
from web3 import Web3
logging.basicConfig(level=logging.INFO)

class Connector:
    def __init__(self):
        self.node_url = "https://sepolia.infura.io/v3/de887b634e97405693e522e0dec6d999"
        self.bot_address = Web3.to_checksum_address("0xFdB3587451Bf34A01eA0F1C68A35c5848c14F7A1")
        self.bot_pk = "dc3505a37fbf76047e5c80f6d4db5f4c849146c1cb41fc25a6a6c7292ba73fe5"  # To sign the transaction
        self.contract_address = Web3.to_checksum_address("0x9a87C708F5Ca7992d7f3cdeb500EEb9b60930320")

        # Create the node connection
        self.web3 = Web3(Web3.HTTPProvider(self.node_url))

        if self.web3.is_connected():
            logging.info("Connection Successful")
        else:
            logging.info("Connection Failed")

        # Initialize contract ABI and address
        artifacts = json.load(open("contract/artifacts.json"))
        abi = artifacts['abi']
        logging.info(f"ABI: {json.dumps(abi, indent=4)}")
        # Create smart contract instance
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=abi)

        all_functions = self.contract.all_functions()
        logging.info(f"Available funcs:\n{all_functions}")

    def makeBet(self, user_id: int, bet_id: int, option: int, wager: int):
        dict_transaction = {
            'chainId': self.web3.eth.chain_id,
            'gas': 210000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(self.bot_address),
        }
        tx = self.contract.functions.layBet(bet_id, user_id, wager, option).build_transaction(dict_transaction)
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.bot_pk)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logging.info(f"TX hash:\n{tx_hash}")
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        logging.info(f"TX receipt:\n{tx_receipt}")

    def register(self, user_id: int, address: str):
        dict_transaction = {
            'chainId': self.web3.eth.chain_id,
            'from': self.bot_address,
            'gas': 210000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(self.bot_address),
        }
        tx = self.contract.functions.register(user_id, Web3.to_checksum_address(address)).build_transaction(dict_transaction)
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.bot_pk)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logging.info(f"TX hash:\n{tx_hash}")
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        logging.info(f"TX receipt:\n{tx_receipt}")


connector = Connector()
connector.register(1782620428, "0xe9f46b6da8EF47EBf99EE9EDCEb8264d24317042")
# connector.makeBet(12, 0, 0, 1)


