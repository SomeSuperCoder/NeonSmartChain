command_and_args = message.data.split("~")
if command_and_args[0] == "set":
    for i in command_and_args[1].split(";"):
        result.new_storage[i.split("=")[0]] = i.split("=")[1]
