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
        self.hash = hash

    def serialize(self, include_signature=True, include_hash=True):
        return {
            "id": self.id,
            "tx_list": [i.serialize() for i in self.tx_list],
            "prev_hash": self.prev_hash,
            "creator": utils.public_key_to_string(self.creator),
            "signature": self.signature if include_signature else None,
            "hash": self.hash if include_hash else None,
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
            results=source.get("results"),
            hash=source.get("hash")
        )

    def execute(self, blockchain, set=False):
        results = []
        for tx in self.tx_list:
            for result in tx.execute(blockchain):
                results.append(result)

        if set:
            self.results = results
        return results

    def get_full_tx_list(self):
        the_result = []
        for tx in self.tx_list:
            the_result.append(tx)
        for result in self.results:
            for eoa_transafer in result.eoa_transfers:
                the_result.append(eoa_transafer)
            for other_sc_call in result.other_sc_calls:
                the_result.append(other_sc_call)

        return the_result

    def do_hash(self):
        self.hash = hashlib.sha256(json.dumps(self.serialize(include_hash=False, include_signature=False)).encode()).hexdigest()
