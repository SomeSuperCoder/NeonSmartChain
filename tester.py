import time

from SmartContract import SmartContract, ExecMessage
from Transaction import Transaction
from Blockchain import Blockchain
import utils

import os

pk = utils.private_key_from_seed_phrase(utils.generate_seed_phrase())
blockchain = Blockchain()
tx = Transaction(1, pk.get_verifying_key(), "", 0, 0)
utils.sign(tx, pk)
sc = SmartContract("print(\"Hello, World!\")", 0, "")
start_time = time.time()
# print(blockchain.validator.validate_tx(tx))
sc.execute(ExecMessage("", "", 0, {}))
print(f"Time: {time.time()-start_time}")
