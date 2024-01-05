import copy
import json
import math
import os
import platform
import random
import subprocess
import threading
import time

import requests

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
random_num = None
vote = None
voted_block = None
latest_slot_to_be_filled = None

# ========================================================
# App routes
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
    global latest_slot_to_be_filled
    global voted_block

    """
    check that the block creator is the current validator,
    validate the block using the method of the Validator class and
    vote fot it you think it's valid
    """
    print("[bold green]New block")

    if slot % 2 != 0:
        return "Wrong slot! Try again later!"
    if latest_slot_to_be_filled == slot:
        return "This slot is already filled on this node. Try again later!"

    data = request.json

    if data is not None:
        try:
            block = Block.from_dict(data)
            block_is_valid = blockchain.validator.validate_block(block)

            if not block_is_valid:
                print("[bold red]Block is invalid")
                return "Block is invalid"
            if block.get_creator_address() != current_validator:
                print("[bold red]Wrong block validator!")
                return "Wrong block validator"
            latest_slot_to_be_filled = slot
            # Old code. For tests only!
            # blockchain.blocks.append(block)
            # blockchain.save()
            voted_block = block

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
        # print(f"THE ADDRESS: {tx.get_sender_address()} {address} {tx.get_sender_address() == address} THE ID: {tx.id} ({tx_id}) {int(tx.id) == int(tx_id)}")
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


@app.route("/add_to_node_list")
def add_to_node_list():
    args = request.args
    ip = args.get("ip")
    try:
        if not ip:
            return "Error: client did not specify node ip"

        if check_if_ip_is_me(ip):
            return "Error: can't add my self"

        if ping(ip):
            known_node_list.append(ip)
    except requests.exceptions.ConnectionError:
        return "Connection error"
    
    return "Done!"


@app.route("/i_am")
def i_am():
    global random_num
    return str(random_num)


@app.route("/get_known_node_list")
def get_known_node_list():
    return known_node_list

@app.route("/get_vote")
def get_vote():
    global vote
    return str(vote)

# ========================================================
# Bg stuff

def bg_miner():
    global tx_pool

    while True:
        if slot % 2 != 0:
            continue
        global latest_used_slot
        if latest_used_slot == slot:
            continue
        latest_used_slot = slot
        print("[bold sky_blue3]Scanning for new transactions...")
        validator = blockchain.pos.select_random_validator(based_on=str(slot))
        print(f"Validator: {validator}")

        if utils.generate_address(miner_private_key.get_verifying_key()) == validator:
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


def bg_voter():
    while True:
        if slot % 2 != 1:
            continue
        global latest_used_slot
        if latest_used_slot == slot:
            continue
        latest_used_slot = slot
        start_time = time.time()

        while time.time() - start_time > config.slot_length:
            vote_status = final_vote()
            if vote_status:
                if blockchain.validator.validate_block(voted_block):
                    blockchain.blocks.append(voted_block)
                else:
                    # TODO: sync blockchain
                    pass


# ========================================================
# Utils

def ping(host):
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0


def check_if_ip_is_me(ip):
    global random_num
    results = []
    for i in range(5):
        random_num = random.randint(-int(math.pow(10, 308)), int(math.pow(10, 308)))
        if net_utils.get_data_from_path("/i_am", ip) == str(random_num):
            results.append(True)
        else:
            results.append(False)

    return all(results)

def sync_blockchain():
    """
    Run only if the current slot is the block create slot
    Get every node oppinion on what the current blockchain state is. Take the most stake popularaty * length one!
    Load it.
    (Ask AI how to do this, ok!)
    """
    pass

# ========================================================
# Vore related stuff

def final_vote(block_id, block_hash) -> bool:
    total_votes = 0

    for vote in gather_votes():
        vote: Vote
        if vote.id == block_id and vote.hash == block_hash:
            total_votes += 1

    return total_votes > len(known_node_list) / 2

def gather_votes():
    result = []
    for node in known_node_list:
        data = net_utils.get_data_from_path("/get_vote", node, json=True)
        try:
            vote_obj = Vote.from_dict(vote)
        except:
            print("[bold yellow]Error loading vote. Skipping!")
            continue

        try:
            if not utils.verify(vote_obj, vote_obj.public_key):
                print("[bold red]Vote verification error! Skipping!")
        except:
            print("[bold yellow]Error verifying vote. Skipping!")
            continue

            
        result.append(voteobj)
            

    return result

class Vote:
    def __init__(self, hash, id, public_key, signature=None):
        self.hash = hash
        self.id = id
        self.public_key = public_key
        self.signature = signature

    def serialize(self):
        return {
            "hash": self.hash,
            "id": self.id,
            "public_key": self.public_key,
            "signature": self.signature
        }

    @classmethod
    def from_dict(cls, source):
        return cls(
            hash=source.get("hash"),
            id=source.get("id"),
            public_key=source.get("public_key"),
            signature=source.get("signature")
        )

    def __str__(self):
        return json.dumps(self.serialize())
# ========================================================

# Start miner
try:
    thread2 = threading.Thread(target=bg_slot_counter)
    thread2.start()
    thread = threading.Thread(target=bg_miner)
    thread.start()
    thread3 = threading.Thread(target=bg_voter)
    thread3.start()
    app.run(debug=False, port=config.node_port)
except KeyboardInterrupt:
    blockchain.save()
