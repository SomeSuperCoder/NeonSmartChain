tx_gas_units = 10
gas_units_per_sc_exec_second = 20
tx_gas_price = 0.01
native_coin_decimals = 2
stake_amount_weight = 2.5
stake_time_weight = 1.2
slot_length = 5  # seconds
node_port = 3152


# SmartContract code stuff
sc_code_prefix = """
import Block, Blockchain, config, SmartContract, Validator, utils
from json import loads, dumps

message = SmartContract.ExecMessage.from_dict(loads(open("/code/message.json").read()))
result = SmartContract.ExecResult({}, [], [], message.storage)

"""
sc_code_postfix = """

with open("/result/result.json", "w") as file:
    file.write(result.serialize())

"""

