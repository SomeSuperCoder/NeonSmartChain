from Transaction import Transaction
from Block import Block

import utils
import config


class Validator:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def validate_tx(self, tx: Transaction):
        if tx.amount + tx.gas > utils.get_balance(blockchain=self.blockchain, address=tx.get_sender_address()):
            print("TX Validation failed: not enough money ;(")
            return False

        if not utils.verify(tx, tx.from_):
            print("TX Validation failed: signature verification failed")
            return False

        # check decimals
        if str(round(tx.amount, config.native_coin_decimals)) != str(tx.amount) or\
                str(round(tx.gas, config.native_coin_decimals)) != str(tx.gas):
            print("TX Validation failed: invalid amount of decimals")
            return False

        # do the non-negative check
        if tx.amount < 0 or tx.gas < 0:
            print("TX Validation failed: negative numbers are forbidden")
            return False

        # check tx id
        if tx.id != self.blockchain.get_latest_tx_id_for_address(address=tx.get_sender_address())+1:
            print("TX Validation failed: TX id does not match the required one")
            return

        return True

    def validate_block(self, block: Block):
        if block.prev_hash != self.blockchain.get_latest_block_hash():
            print("Block Validation failed: prev_hash does not match blockchain latest hash")
            return False

        if block.id != self.blockchain.get_latest_block_id()+1:
            print("Block Validation failed: block id does not match the required one")
            return False

        if utils.verify(block, block.creator):
            print("Block Validation failed: signature verification failed")
            return False

        if not all([self.validate_tx(tx) for tx in block.tx_list]):
            print("Block Validation failed: block contains a fraudulent TX!")
            return False

    def validate_sc_to_eoa_tx(self):
        pass

    def validate_sc_to_sc_tx(self):
        pass
