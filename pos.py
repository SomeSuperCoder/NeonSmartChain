import random

import config
import utils

from Transaction import Transaction


class ProofOfStake:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def get_stake_info(self):
        stakers = {}
        for tx in self.blockchain.get_tx_list():
            tx: Transaction = tx
            if tx.to == "stake":
                address = tx.get_sender_address()
                staker = stakers.get(address) or Staker(amount=0, time=1)
                stakers[address] = Staker(amount=staker.amount+tx.amount, time=staker.time)
            if tx.from_ == "stake":
                address = tx.get_sender_address()
                staker = stakers.get(address) or Staker(amount=0, time=1)
                stakers[address] = Staker(amount=staker.amount + tx.amount, time=staker.time)

        return stakers

    def select_random_validator(self, based_on: str = ""):
        random.seed(int.from_bytes(f"{based_on}".encode()))

        nodes = self.get_stake_info()
        nodes["capybara"] = Staker(90, 7)
        nodes["superman"] = Staker(100, 5)
        weight_map = {}

        for address, staker in nodes.items():
            weight_map[address] = round(staker.calculate_weight())

        address_list = list(weight_map.keys())
        weight_list = list(weight_map.values())
        print("Lists")
        print(address_list)
        print(weight_list)

        try:
            return random.choices(population=address_list, weights=weight_list, k=1)[0]
        except IndexError:
            return "0x7Cmg3rA1FSvho4acs6fFeZrPXhEHo2h99T1xMnodwn6o"


class Staker:
    def __init__(self, amount, time):
        self.amount = amount
        self.time = time

    def calculate_weight(self):
        return utils.slow_growth_multiplication(self.amount,
                                                self.time,
                                                config.stake_amount_weight,
                                                config.stake_time_weight)
