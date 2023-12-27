# from Blockchain import Blockchain
# from SmartContract import SmartContract, ExecMessage
# from Transaction import Transaction
# from rich import print
#
# import utils
#
# capybara_pk = utils.private_key_from_seed_phrase(
#     "diamond draft index outer mix frost teach master ritual round junk gloom"
# )
# capybara_vk = capybara_pk.get_verifying_key()
# capybara_address = utils.generate_address(capybara_vk)
#
# super_man_pk = utils.private_key_from_seed_phrase("superman")
# super_man_vk = super_man_pk.get_verifying_key()
# super_man_address = utils.generate_address(super_man_vk)
#
# print(f"Capybara address: {capybara_address}")
# print(f"Superman address: {super_man_address}")
#
# blockchain = Blockchain.load()
# # blockchain = Blockchain()
# # print(blockchain)
#
# print(utils.get_balance(blockchain, capybara_address))
#
# # tx = utils.send(
# #     id=blockchain.get_latest_tx_id_for_address(address=capybara_address)+1,
# #     private_key=capybara_pk,
# #     to=super_man_address,
# #     amount=20,
# #     message="Hello, World!"
# # )
#
# sc_code = open("test_sc.py", "r").read()
# sc = SmartContract(sc_code)
# # sc.execute(ExecMessage(capybara_address, "set~test=123"))
#
# tx = Transaction(
#     id=blockchain.get_latest_tx_id_for_address(address=capybara_address)+1,
#     from_=super_man_vk,
#     to="stake",
#     amount=10,
#     gas=0,
#     message="set~super=cool"
# )
# utils.sign(tx, capybara_pk)
# # print(tx.execute(blockchain=blockchain))
#
# # print(blockchain.validator.validate_tx(tx))
#
# # block = blockchain.create_new_block(tx_list=[], private_key=super_man_pk)
# # blockchain.blocks.append(block)
# #
# # print(block.execute(blockchain=blockchain))
# #
# # info = blockchain.pos.get_stake_info()
# #
# # for address, staker in info.items():
# #     print(f"{address}: {staker.calculate_weight()} ({staker.amount} * {staker.time})")
# #
# # blockchain.save()
#
# print(blockchain.pos.get_stake_info())
import base58
import utils
import random

allowed_words = open("cli_wallet_stuff/words.txt", "r").read().strip().split("\n")


def generate_random_seed():
    result = ""
    random.choice(allowed_words)
    for i in range(12):
        result = result + f"{random.choice(allowed_words)} "

    return result.strip()


while True:
    seed_phrase = generate_random_seed()
    sk = utils.private_key_from_seed_phrase(seed_phrase)
    vk = sk.get_verifying_key()
    address = utils.generate_address(vk)

    print("Seed phrase: " + seed_phrase)
    print("Private key: " + base58.b58encode(sk.to_string()).decode())
    print("Public key: " + utils.public_key_to_string(vk))
    print("Address: " + address)
    print("="*150)
