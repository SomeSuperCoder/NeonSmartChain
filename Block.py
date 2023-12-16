import hashlib
import json
import utils

from Transaction import Transaction
from SmartContract import ExecMessage, ExecResult


class Block:
    def __init__(self, id, tx_list, prev_hash, creator, signature=None, hash=None, results=None):
        if results is None:
            self.results: list[ExecResult] = []
        else:
            self.results: list[ExecResult] = results

        self.id = id
        self.tx_list: list[Transaction] = tx_list
        self.prev_hash = prev_hash
        self.creator = creator
        self.signature = signature
        self.hash = None

        if hash is None:
            self.hash = hashlib.sha256(str(self).encode()).hexdigest()
        else:
            self.hash = hash

    def serialize(self, strict=True):
        return {
            "id": self.id,
            "tx_list": [i.serialize() for i in self.tx_list],
            "prev_hash": self.prev_hash,
            "creator": utils.public_key_to_string(self.creator),
            "signature": self.signature if strict else None,
            "hash": self.hash if strict else None,
            "results": self.results
        }

    def __str__(self):
        return json.dumps(self.serialize(), indent=4)

    def get_creator_address(self):
        return utils.generate_address(self.creator)

    @classmethod
    def from_dict(cls, source: dict):
        return cls(
            id=source.get("id"),
            tx_list=[Transaction.from_dict(i) for i in source.get("tx_list")],
            prev_hash=source.get("prev_hash"),
            creator=utils.public_key_from_string(source.get("creator")),
            signature=source.get("signature"),
            results=source.get("results")
        )

    def execute(self, blockchain, set=False):
        results = []
        for tx in self.tx_list:
            for result in tx.execute(blockchain):
                results.append(result)

        if set:
            self.results = results
        return results
