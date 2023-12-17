import json
import base58
import config
import utils
import os
import Transaction


class SmartContract:
    def __init__(self, code, language="python", nonce=0, docs=""):
        self.nonce = nonce
        self.raw_code = code

        if language == "python":
            if "eval" in code or "exec" in code or "import" in code:
                self.code = ""
            else:
                self.code = config.sc_code_prefix + self.raw_code + config.sc_code_postfix

        else:
            self.code = ""

        self.docs = docs
        self.language = language
        self.address = utils.generate_serializable_address(self)

        print("The code is:")
        print(self.code)
        print("==========================================")

    def execute(self, message):
        with open("sc_code.py", "w") as file:
            file.write(self.code)
        with open("message.json", "w") as file:
            file.write(message.serialize())
        with open("message.json", "w") as file:
            file.write(message.serialize())

        if self.language == "python":
            os.system("docker run --rm --name sc_run -v \"$(pwd)/result:/result\" -v \"$(pwd):/code:ro\" neon_vm")

        with open("result/result.json", "r") as file:
            return ExecResult.from_dict(json.loads(file.read()))

    def serialize(self, strict=True):
        return {
                "address": self.address if strict else None,
                "nonce": self.nonce,
                "language": self.language,
                "code": base58.b58encode(self.raw_code.encode()).decode(),
                "docs": self.docs
            }

    @staticmethod
    def from_dict(source):
        return SmartContract(
                code=base58.b58decode(source.get("code")).decode(),
                docs=source.get("docs"),
                nonce=source.get("nonce"),
                language=source.get("language")
        )

    def __str__(self):
        return json.dumps(
            self.serialize()
        )


class ExecMessage:
    def __init__(self, sender: str, data, amount=None, storage=None):
        if storage is None:
            storage = {}
        if amount is None:
            amount = {}

        self.sender = sender
        self.amount = amount
        self.data = data
        self.storage = storage

    def serialize(self):
        return json.dumps({
            "sender": self.sender,
            "amount": self.amount,
            "data": self.data,
            "storage": self.storage
        })

    @staticmethod
    def from_dict(source):
        return ExecMessage(
            sender=source["sender"],
            amount=source["amount"],
            data=source["data"],
            storage=source["storage"]
        )


class ExecResult:
    def __init__(self, return_data, eoa_transfers, other_sc_calls, new_storage: dict, creator=None):
        self.return_data = return_data
        self.eoa_transfers = eoa_transfers
        self.other_sc_calls = other_sc_calls
        self.new_storage = new_storage
        self.creator = creator

    def serialize(self):
        return json.dumps(
            {
                "return_data": self.return_data,
                "new_transactions": self.eoa_transfers,
                "other_sc_calls": self.other_sc_calls,
                "new_storage": self.new_storage,
                "creator": self.creator
            }
        )

    @staticmethod
    def from_dict(source):
        return ExecResult(
            return_data=source.get("return_data"),
            eoa_transfers=source.get("eoa_transfers"),
            other_sc_calls=source.get("other_sc_calls"),
            new_storage=source.get("new_storage"),
            creator=source.get("creator")
        )
