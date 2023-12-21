import copy
import json
import os
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

miner_private_key = utils.private_key_from_seed_phrase(
    "diamond draft index outer mix frost teach master ritual round junk gloom"
)

app = Flask(__name__)

if os.path.isfile("blockchain.json"):
    blockchain = Blockchain().load()
else:
    blockchain = Blockchain()

tx_pool = []
known_node_list = ["127.0.0.1"]
current_validator = None
slot = None
prev_slot = None
latest_used_slot = None


@app.route("/")
def index():
    return "<h1>Hello! This is a NeonSmartChain cryptocurrency network node!</h1>"


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    print("[bold green]New transaction!")
    data = request.json

    if data is not None:
        try:
            tx = Transaction.from_dict(data)
        except:
            print("[bold red]Error loading transaction. Skipping")
            return "Error"

        try:
            is_valid = blockchain.validator.validate_tx(tx)
            if not is_valid:
                print("[bold red]Transaction is fraudulent")
                return "Fraudulent transaction"

            tx_pool.append(tx)
            print("[bold green]Successfully added transaction too pool!")
            filtered_known_node_list = [i for i in known_node_list if i != "127.0.0.1"]
            broadcast_status = net_utils.broadcast_json_to_url(tx.serialize(), "/new_transaction", filtered_known_node_list)
            if broadcast_status:
                print("[bold green]Successfully broadcasted transaction!")
            else:
                print("[bold red]TX broadcast error")
            return "Ok"
        except BaseException as e:
            print(f"{e.__class__.__name__}: {e}")
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
    print("[bold green]New block")
    data = request.json

    if data is not None:
        try:
            block = Block.from_dict(data)
            print(f"Hash: {block.hash}")
            block_is_valid = blockchain.validator.validate_block(block)
            if not block_is_valid:
                print("[bold red]Block is invalid")
            if block.get_creator_address() != current_validator:
                print("[bold red]Wrong block validator!")

            blockchain.blocks.append(block)
            blockchain.save()

            return "Ok"
        except BaseException as e:
            print(f"{e.__class__.__name__}: {e}")
            print("[bold red]Error loading block. Skipping")
            return "Error"
    else:
        return "Client sent no data"


@app.route("/utils/balance_of")
def balance_of():
    args = request.args
    address = args.get("address")
    if not address:
        return "Error: client did not specify account address. This is likely a problem with your wallet application"
    return str(utils.get_balance(blockchain, address))


@app.route("/utils/get_latest_tx_id_for_address")
def get_latest_tx_id_for_address():
    args = request.args
    address = args.get("address")
    if not address:
        return "Error: client did not specify account address. This is likely a problem with your wallet application"
    return str(blockchain.get_latest_tx_id_for_address(address=address))


@app.route("/utils/stake_info")
def stake_info():
    args = request.args
    address = args.get("address")
    if not address:
        return "Error: client did not specify account address. This is likely a problem with your wallet application"
    try:
        amount = blockchain.pos.get_stake_info().get(address).amount
        return str(amount)
    except AttributeError:
        return str(0)


@app.route("/utils/tx_info")
def tx_info():
    args = request.args
    address = args.get("address")
    tx_id = args.get("id")
    print(f"ARGS: {address}{tx_id}")

    if not address or not tx_id:
        return "Error: client did not specify account address or TX id. This is likely a problem with your wallet application"

    tx_list = blockchain.get_full_tx_list()
    the_tx = None
    for tx in tx_list:
        print(f"THE ADDRESS: {tx.get_sender_address()} {address} {tx.get_sender_address() == address} THE ID: {tx.id} ({tx_id}) {int(tx.id) == int(tx_id)}")
        if tx.get_sender_address() == address and int(tx.id) == int(tx_id):
            the_tx = tx

    if the_tx:
        return {
            "status": "confirmed"
        }
    else:
        return {
            "status": "unconfirmed"
        }


def bg_miner():
    global tx_pool
    while True:
        time.sleep(1)
        print("[bold sky_blue3]Scanning for new transactions...")
        validator = blockchain.pos.select_random_validator(based_on=str(slot))
        print(f"Validator: {validator}")

        if utils.generate_address(miner_private_key.get_verifying_key()) == validator:
            global latest_used_slot
            if latest_used_slot == slot:
                continue
            latest_used_slot = slot
            print("[bold green]Adding a block!")
            # double spending protection
            result_pool = []
            tmp_blockchain = copy.copy(blockchain)
            empty_block = tmp_blockchain.create_new_block([], miner_private_key)
            tmp_blockchain.blocks.append(empty_block)
            for tx in tx_pool:
                if tmp_blockchain.validator.validate_tx(tx):
                    tmp_blockchain.blocks[-1].tx_list.append(tx)
                    result_pool.append(tx)

            # create the new block it self
            some_new_block = blockchain.create_new_block(tx_list=[],
                                                         private_key=miner_private_key)
            some_new_block.execute(blockchain=blockchain)
            some_new_block.do_hash()
            net_utils.broadcast_json_to_url(some_new_block.serialize(), "/new_block", known_node_list)
            tx_pool = []


def bg_slot_counter():
    global slot
    global prev_slot
    global current_validator

    prev_slot = None
    while True:
        prev_slot = slot
        slot = divmod(time.time(), config.slot_length)[0]
        if slot != prev_slot:
            print(f"Slot: {slot}")
            current_validator = blockchain.pos.select_random_validator(f"{slot}")


try:
    thread2 = threading.Thread(target=bg_slot_counter)
    thread2.start()
    thread = threading.Thread(target=bg_miner)
    thread.start()
    app.run(debug=False, port=config.node_port)
except KeyboardInterrupt:
    blockchain.save()
