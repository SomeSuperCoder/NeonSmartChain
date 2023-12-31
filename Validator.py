from copy import copy

import loguru

from Transaction import Transaction
from Block import Block

import utils
import config


class Validator:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def validate(self):
        from Blockchain import Blockchain
        partial_blockchain = Blockchain()
        for block in self.blockchain.blocks:
            if not partial_blockchain.validator.validate_tx(block):
                return False

            partial_blockchain.blocks.append(block)

        return True

    def validate_tx(self, tx: Transaction):
        # check if the user has enough money
        if tx.amount + tx.gas > utils.get_balance(blockchain=self.blockchain, address=tx.get_sender_address()):
            print("TX Validation failed: not enough money ;(")
            return False

        # signature check
        if not utils.verify(tx, tx.from_):
            print("TX Validation failed: signature verification failed")
            return False

        if tx.to != "stake":
            # do the non-negative check
            if tx.amount < 0 or tx.gas < 0:
                print("TX Validation failed: negative numbers are forbidden")
                return False

        # check decimals
        if str(round(tx.amount, config.native_coin_decimals)) != str(tx.amount) or\
                str(round(tx.gas, config.native_coin_decimals)) != str(tx.gas):
            print("TX Validation failed: invalid amount of decimals")
            return False

        # check tx id
        if tx.id != self.blockchain.get_latest_tx_id_for_address(address=tx.get_sender_address())+1:
            print("TX Validation failed: TX id does not match the required one")
            return False

        if tx.to == "stake" and tx.amount < 0:
            # check stake release amount
            try:
                amount = self.blockchain.pos.get_stake_info().get(tx.get_sender_address()).amount
            except:
                amount = 0
            if amount < abs(tx.amount):
                print(f"He has: {amount}")
                print("TX Validation failed: user is trying to release more stake than he has")
                return False

        return True

    def validate_block(self, block: Block):
        a_copy = copy(block)
        a_copy.do_hash()

        if block.hash != a_copy.hash:
            print("Block Validation failed: wrong hash")
            return False

        if block.prev_hash != self.blockchain.get_latest_block_hash():
            print("Block Validation failed: prev_hash does not match blockchain latest hash")
            return False

        if block.id != self.blockchain.get_latest_block_id()+1:
            print("Block Validation failed: block id does not match the required one")
            return False

        if not utils.verify(block, block.creator):
            print("Block Validation failed: signature verification failed")
            return False

        # old code
        # if not all([self.validate_tx(tx) for tx in block.tx_list]):
        #     print("Block Validation failed: block contains a fraudulent TX!")
        #     return False

        valid_tx_list = []
        from Blockchain import Blockchain

        for tx in block.tx_list:
            tmp_blockchain: Blockchain = copy(self.blockchain)
            tmp_block = tmp_blockchain.create_new_block(valid_tx_list)
            tmp_blockchain.blocks.append(tmp_block)

            if tmp_blockchain.validator.validate_tx(tx):
                valid_tx_list.append(tx)
            else:
                print("Block Validation failed: block contains a fraudulent TX!")
                return False

        # in the new update tx results will be stored in the tx itself
        if block.results != block.execute(self.blockchain.get_slice(block.id)):
            print("Block Validation failed: block code execution results do not match the ones sent by the miner")
            return False

        return True

    def filter_fraudulent_transaction_from_list(self, tx_list):
        valid_tx_list = []
        from Blockchain import Blockchain

        for tx in tx_list:
            tmp_blockchain: Blockchain = copy(self.blockchain)
            tmp_block = tmp_blockchain.create_new_block(valid_tx_list)
            tmp_blockchain.blocks.append(tmp_block)

            if tmp_blockchain.validator.validate_tx(tx):
                valid_tx_list.append(tx)
            else:
                loguru.logger.debug("Found a fraudulent tx!")

        return valid_tx_list
