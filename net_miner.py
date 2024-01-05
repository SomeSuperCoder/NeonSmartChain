# TODO: asc user to login
# TODO: parse other nodes form config file

import os
import sys
import time
import threading

from flask import Flask
from loguru import logger

import utils
from Blockchain import Blockchain
import config

miner_pk = utils.private_key_from_seed_phrase(
    "diamond draft index outer mix frost teach master ritual round junk gloom"
)
miner_vk = miner_pk.get_verifying_key()
miner_address = utils.generate_address(miner_vk)

logger.info(f"Mining as: {miner_address}")

app = Flask(__name__)

if os.path.isfile("blockchain.json"):
    blockchain = Blockchain().load()
else:
    blockchain = Blockchain()

slot = None
prev_slot = None
current_validator = None
latest_checked_slot = None

tx_pool = []

# ================================================
# bg tasks


def bg_slot_counter():
    global slot
    global prev_slot
    global current_validator

    while True:
        prev_slot = slot
        slot = divmod(time.time(), config.slot_length)[0]
        if slot != prev_slot:
            logger.info(f"Slot: {slot}")
            current_validator = blockchain.pos.select_random_validator(f"{slot}")


def bg_miner():
    global latest_checked_slot

    while True:
        if latest_checked_slot == slot:
            continue

        latest_checked_slot = slot
        logger.info(f"Current leader: {current_validator}")
        if miner_address == current_validator:
            logger.info("Selected!")

# ================================================


def main():
    try:
        slot_counter = threading.Thread(target=bg_slot_counter)
        slot_counter.start()
        miner = threading.Thread(target=bg_miner)
        miner.start()

        slot_counter.join()
        miner.join()

    except KeyboardInterrupt:
        logger.info("Saving blockchain...")
        blockchain.save()
        logger.info("Exiting!")


if __name__ == "__main__":
    main()
