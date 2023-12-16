import json
import ecdsa

from SmartContract import SmartContract, ExecMessage, ExecResult
import utils


class Transaction:
    def __init__(self, id: int, from_: ecdsa.VerifyingKey, to, amount, gas, message="", signature=None, contract=None):
        self.id = id
        self.from_ = from_  # stake, coinbase
        self.to = to  # stake
        self.amount = amount
        self.gas = gas
        self.message = message
        self.signature = signature
        self.contract = contract

    def get_sender_address(self):
        return utils.generate_address(self.from_)

    def serialize(self, strict=True):
        return {
            "id": self.id,
            "from_": utils.public_key_to_string(self.from_),
            "to": self.to,
            "amount": self.amount,
            "gas": self.gas,
            "message": self.message,
            "contract": self.contract.serialize(),
            "signature": self.signature if strict else None
        }

    def __str__(self):
        return json.dumps(self.serialize())

    @classmethod
    def from_dict(cls, source: dict):
        return cls(
            id=source.get("id"),
            from_=utils.public_key_from_string(source.get("from_")),
            to=source.get("to"),
            amount=source.get("amount"),
            gas=source.get("gas"),
            message=source.get("message"),
            contract=SmartContract.from_dict(source.get("contract")),
            signature=source.get("signature")
        )

    def execute(self, blockchain):
        call_stack = [self]
        results: list[ExecResult] = []

        def do_exec(the_call):
            sc: SmartContract = blockchain.get_sc_by_address(the_call.to)
            if sc is not None:
                message = ExecMessage(sender=the_call.get_sender_address(),
                                      data=the_call.message,
                                      amount=the_call.amount,
                                      storage=blockchain.get_sc_storage(the_call.to))
                result = sc.execute(message)
                results.append(result)

                for sc_call in result.other_sc_calls:
                    call_stack.append(sc_call)

        while len(call_stack) > 0:
            call = call_stack.pop()
            do_exec(call)

        return results


# these can be only created by smart contracts
class ScToEOA:
    def __init__(self, from_, to, amount, message=""):
        self.from_ = from_
        self.to = to
        self.amount = amount
        self.message = message

    def serialize(self, strict=True):
        return {
            "from_": utils.public_key_to_string(self.from_),
            "to": self.to,
            "amount": self.amount,
            "message": self.message,
        }

    def __str__(self):
        return json.dumps(self.serialize())

    @classmethod
    def from_dict(cls, source: dict):
        return cls(
            from_=utils.public_key_from_string(source.get("from_")),
            to=source.get("to"),
            amount=source.get("amount"),
            message=source.get("message"),
        )

    def get_sender_address(self):
        return self.from_


class SCToSC(ScToEOA):
    pass
