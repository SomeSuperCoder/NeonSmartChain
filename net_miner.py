# import json
# import threading
# import time

import utils
from Blockchain import Blockchain
from Transaction import Transaction
from Block import Block
from flask import Flask, request
from rich import print

# import config
import net_utils

print("[bold green] Miner started")

miner_private_key = utils.private_key_from_seed_phrase("capybara")


app = Flask(__name__)

blockchain = Blockchain()
blockchain.load()
tx_pool = []
known_node_list = []
current_validator = blockchain.pos.select_random_validator()


@app.route("/")
def index():
    return "Hello! This is a NeonSmartChain cryptocurrency network node!"


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    data = request.json

    if data is not None:
        try:
            tx = Transaction.from_dict(data)
        except:
            print("[bold red]Error loading transaction. Skipping")
            return "Error"

        try:
            is_valid = not blockchain.validator.transaction_is_fraudulent(blockchain=blockchain,
                                                                          transaction=tx)
            if not is_valid:
                print("[bold red]Transaction is fraudulent")
                return "Fraudulent transaction"

            tx_pool.append(tx)
            print("[bold green]Successfully added transaction too pool!")
            broadcast_status = net_utils.broadcast_json_to_url(tx.serialize(), "/new_transaction", known_node_list)
            if broadcast_status:
                print("[bold green]Successfully broadcasted transaction!")
            else:
                print("[bold red]TX broadcast error")
        except:
            print("[bold red]Error while validating transaction!")
            return "Error"
    else:
        return "Client sent do data"


@app.route('/new_block', methods=['POST'])
def new_block():
    data = request.json

    if data is not None:
        # check that the block creator is the current validator, validate the block using the method of the Validator class and add it if you think it's valid remember abount the PoW phase
        try:
            block = Block.from_dict(data)
            block_is_valid = not blockchain.validator.block_is_fraudulent(blockchain, block)
            if not block_is_valid:
                print("[bold red]Block is invalid")
        except:
            print("[bold red]Error loading block. Skipping")
            return "Error"
    else:
        return "Client sent do data"


# def bg_miner():
#     while True:
#         time.sleep(config.node_tx_scan_delay)
#         print("[bold sky_blue3]Scanning for new transactions...")
#         print(f"Validator: {blockchain.select_random_validator()}")
#         if utils.generate_address(miner_private_key.get_verifying_key()) == blockchain.select_random_validator():
#             reward_tx = Transaction(miner_private_key.get_verifying_key(),
#                                  outputs=[
#                                      Output("",
#                                             utils.generate_address(miner_private_key.get_verifying_key()),
#                                             amount=100000000000000,
#                                             token_address="",
#                                             type="reward")
#                                           ],
#                                  )
#             tx_pool.append(reward_tx)
#             new_block = NewBlock(
#                 blockchain.get_latest_block_id()+1,
#                 tx_pool,
#                 blockchain.get_latest_hash()
#             )
#             utils.random_mine(new_block)
#             net_utils.broadcast_json_to_url(json.loads(new_block.serialize()), "/new_block", known_node_list)
#             # execute all scs ;(

# thread = threading.Thread(target=bg_miner)
# thread.start()
# app.run(debug=True, port=config.node_port)
