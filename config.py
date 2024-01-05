tx_gas_units = 21_000
gas_units_per_sc_exec_second = 21_000
tx_gas_price = 0.01  # TODO: this should be removed
native_coin_decimals = 18
stake_amount_weight = 2.5
stake_time_weight = 1.2
slot_length = 3  # seconds
node_port = 3152
stake_minimum = 100  # neon #TODO: actually use this!
vote_expire_time = 10  # slots
miner_earn = 10  # roots
super_address = "7Cmg3rA1FSvho4acs6fFeZrPXhEHo2h99T1xMnodwn6o"

# SmartContract code stuff
python_sc_code_prefix = """
import Block, Blockchain, config, SmartContract, Validator, utils
from json import loads, dumps

message = SmartContract.ExecMessage.from_dict(loads(open("message.json", "r").read()))
result = SmartContract.ExecResult({}, [], [], message.storage)

class _ImportError(Exception):
    pass

def __import__(*args, **kwargs):
    raise _ImportError("Importing is not allowed.")

# Override the built-in __import__ function
# __builtins__.__import__ = __import__
"""
python_sc_code_postfix = """

with open("result.json", "w") as file:
    file.write(result.serialize())

"""
