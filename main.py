from Blockchain import Blockchain
from SmartContract import SmartContract, ExecMessage
from Transaction import Transaction
from rich import print

import utils

capybara_pk = utils.private_key_from_seed_phrase(
    "capybara"
)
capybara_vk = capybara_pk.get_verifying_key()
capybara_address = utils.generate_address(capybara_vk)

super_man_pk = utils.private_key_from_seed_phrase("superman")
super_man_vk = super_man_pk.get_verifying_key()
super_man_address = utils.generate_address(super_man_vk)

print(f"Capybara address: {capybara_address}")
print(f"Superman address: {super_man_address}")

blockchain = Blockchain.load()
# blockchain = Blockchain()
# print(blockchain)

print(utils.get_balance(blockchain, capybara_address))

# tx = utils.send(
#     id=blockchain.get_latest_tx_id_for_address(address=capybara_address)+1,
#     private_key=capybara_pk,
#     to=super_man_address,
#     amount=20,
#     message="Hello, World!"
# )

sc_code = open("test_sc.py", "r").read()
sc = SmartContract(sc_code)
# sc.execute(ExecMessage(capybara_address, "set~test=123"))

tx = Transaction(
    id=blockchain.get_latest_tx_id_for_address(address=capybara_address)+1,
    from_=capybara_vk,
    to="0xHzfdXfZLsyDWwCoDQuowLrdwoGuKReGdNxdE1p56Crxx",
    amount=0,
    gas=0,
    contract=sc,
    message="set~super=cool"
)
utils.sign(tx, capybara_pk)
print(tx.execute(blockchain=blockchain))

print(blockchain.validator.validate_tx(tx))

block = blockchain.create_new_block(tx_list=[tx], private_key=super_man_pk)
blockchain.blocks.append(block)

# print(block)

# blockchain.save()
