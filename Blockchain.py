import json

import SmartContract
import utils
import ecdsa

from Block import Block
from Transaction import Transaction
from Validator import Validator
from pos import ProofOfStake


class Blockchain:
    def __init__(self, blocks=None):
        if blocks is None:
            self.blocks = [self.create_genesis_block()]
        else:
            self.blocks = blocks

        self.stakers = {}
        self.pos = ProofOfStake(self)
        self.poh = None
        self.validator = Validator(self)

    def get_tx_list(self) -> list[Transaction]:
        result = []
        for block in self.blocks:
            for tx in block.tx_list:
                result.append(tx)

        return result

    def create_new_block(self, tx_list, private_key: ecdsa.SigningKey):
        new_block = Block(
            id=self.get_latest_block_id()+1,
            tx_list=tx_list,
            prev_hash=self.get_latest_block_hash(),
            creator=private_key.get_verifying_key()
        )
        utils.sign(new_block, private_key)

        return new_block

    @staticmethod
    def create_genesis_block():
        creator_pk = utils.private_key_from_seed_phrase("genesis")
        creator_vk = creator_pk.get_verifying_key()
        new_block = Block(
            id=0,
            tx_list=[],
            prev_hash="0"*64,
            creator=creator_vk
        )
        utils.sign(new_block, creator_pk)
        return new_block

    def get_latest_block_id(self):
        return self.blocks[-1].id

    def get_latest_block_hash(self):
        return self.blocks[-1].hash

    def serialize(self):
        return {
            "blocks": [i.serialize() for i in self.blocks]
        }

    @classmethod
    def from_dict(cls, source):
        return cls(
            blocks=[Block.from_dict(i) for i in source.get("blocks")]
        )

    def __str__(self):
        return json.dumps(self.serialize(), indent=4)

    def get_latest_tx_id_for_address(self, address):
        tx_list = self.get_tx_list()
        tx_list.reverse()
        for tx in tx_list:
            tx: Transaction = tx
            if tx.get_sender_address() == address:
                return tx.id

        return 0

    def get_sc_storage(self, address):
        for block in self.blocks.__reversed__():
            storage = None
            for result in block.results:
                result: SmartContract.ExecResult
                if result.creator == address:
                    storage = result.new_storage
            if storage:
                return storage

        return {}

    def get_sc_by_address(self, address):
        for tx in self.get_tx_list():
            if tx.contract is not None:
                if tx.contract.address == address:
                    return tx.contract

    @classmethod
    def load_from_string(cls, string):
        return cls.from_dict(json.loads(string))

    def save(self, filename="blockchain.json"):
        open(filename, "w").write(str(self))

    @classmethod
    def load(cls, filename="blockchain.json"):
        return cls.load_from_string(open(filename, "r").read())
