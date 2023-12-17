import copy
import json
import threading
import time

import utils
from Blockchain import Blockchain
from Transaction import Transaction
from Block import Block
from flask import Flask, request
from rich import print

import config
import net_utils

print("[bold green] Miner started")

miner_private_key = utils.private_key_from_seed_phrase("capybara")


app = Flask(__name__)

blockchain = Blockchain()
blockchain.load()
tx_pool = []
known_node_list = []
current_validator = None
slot = None


@app.route("/")
def index():
    return "<h1>Hello! This is a NeonSmartChain cryptocurrency network node!</h1>"


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
        return "Client sent no data"


@app.route('/new_block', methods=['POST'])
def new_block():
    """
    check that the block creator is the current validator,
    validate the block using the method of the Validator class and
    vote fot it you think it's valid
    """

    data = request.json

    if data is not None:
        try:
            block = Block.from_dict(data)
            block_is_valid = blockchain.validator.validate_block(blockchain, block)
            if not block_is_valid:
                print("[bold red]Block is invalid")
                blockchain.blocks.append(block)
        except:
            print("[bold red]Error loading block. Skipping")
            return "Error"
    else:
        return "Client sent no data"


def bg_miner():
    while True:
        time.sleep(1)
        print("[bold sky_blue3]Scanning for new transactions...")
        validator = blockchain.pos.select_random_validator(based_on=str(slot))
        print(f"Validator: {validator}")

        if utils.generate_address(miner_private_key.get_verifying_key()) == validator:
            # TODO: add double spending protection
            result_pool = []
            tmp_blockchain = copy.copy(blockchain)
            empty_block = tmp_blockchain.create_new_block([], miner_private_key)
            tmp_blockchain.blocks.append(empty_block)
            for tx in tx_pool:
                tmp_block = blockchain.blocks.pop()
                tmp_block.tx_list.append(tx)
                if blockchain.

            # create the new block it self
            some_new_block = blockchain.create_new_block(tx_list=tx_pool,
                                                         private_key=miner_private_key)
            some_new_block.execute()
            net_utils.broadcast_json_to_url(json.loads(new_block.serialize()), "/new_block", some_new_block)


def bg_slot_counter():
    global slot
    global prev_slot
    prev_slot = None
    while True:
        prev_slot = slot
        slot = divmod(time.time(), config.slot_length)[0]
        if slot != prev_slot:
            print(f"Slot: {slot}")


thread2 = threading.Thread(target=bg_slot_counter)
thread2.start()
thread = threading.Thread(target=bg_miner)
thread.start()
app.run(debug=False, port=config.node_port)
