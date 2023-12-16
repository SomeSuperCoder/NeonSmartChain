
import Block, Blockchain, config, SmartContract, Validator, utils
from json import loads, dumps

message = SmartContract.ExecMessage.from_dict(loads(open("/code/message.json").read()))
result = SmartContract.ExecResult({}, [], [], message.storage)

command_and_args = message.data.split("~")
if command_and_args[0] == "set":
    for i in command_and_args[1].split(";"):
        result.new_storage[i.split("=")[0]] = i.split("=")[1]


with open("/result/result.json", "w") as file:
    file.write(result.serialize())

