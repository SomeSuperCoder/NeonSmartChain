import os
import random

import requests
from rich import print

import config
import data_encrypt
import net_utils
import utils

allowed_words = open("cli_wallet_stuff/words.txt", "r").read().strip().split("\n")
node = "127.0.0.1"


def is_seed_phrase(text: str):
    words = text.strip().split(" ")

    if len(words) != 12:
        return False

    for word in words:
        if word not in allowed_words:
            return False

    return True


def generate_random_seed():
    result = ""
    random.choice(allowed_words)
    for i in range(12):
        result = result + f"{random.choice(allowed_words)} "

    return result.strip()

# ===============================================
# app


print("[bold green]Welcome to the Neon official CLI wallet!")

if not os.path.isfile("cli_wallet_stuff/account.bin"):
    while True:
        print("Please, enter your seed phrase(leave empty to create a new account): ", end="")
        seed = input("")

        if seed.strip() != "":
            if not is_seed_phrase(seed):
                print("[bold red]Invalid seed phrase!")
                continue
        if seed.strip() == "":
            seed = generate_random_seed()

        print("Please, create a password for the next login: ", end="")
        password = input("")
        enc_data = data_encrypt.encrypt_text(text=seed, password=password)
        open("cli_wallet_stuff/account.bin", "w+b").write(enc_data)

        break

while True:
    global seed_phrase
    print("Enter your password: ", end="")
    password = input("")
    try:
        seed_phrase = data_encrypt.decrypt_text(open("cli_wallet_stuff/account.bin", "r+b").read(), password)
    except UnicodeDecodeError:
        print("[bold red]Wrong password!")
        continue
    if not is_seed_phrase(seed_phrase):
        print("[bold red]Wrong password!")
        continue

    break

private_key = utils.private_key_from_seed_phrase(seed_phrase)
public_key = private_key.get_verifying_key()
address = utils.generate_address(public_key)

while True:
    data = input(">> ")
    match data:
        case "seed":
            print(seed_phrase)
        case "address":
            print(address)
        case "logout":
            os.remove("cli_wallet_stuff/account.bin")
            exit()
        case "exit":
            exit()
        case "balance":
            try:
                balance = net_utils.get_data_from_path(f"/utils/balance_of?address={address}", node)
                print(f"Balance: {balance}")
            except requests.exceptions.ConnectionError as e:
                print(f"{e.__class__.__name__}: {e}")
                print("[bold red]Network connection error")
        case "send":
            to = input(f"Enter the receiver address: ")
            try:
                amount = round(float(input("Amount: ")), config.native_coin_decimals)
            except:
                print("[bold red]Error: that is not a number!")
                break

            index = int(net_utils.get_data_from_path(f"/utils/get_latest_tx_id_for_address?address={address}", node))

            message = input("Enter a message: ")
            send_tx = utils.send(
                id=index+1,
                private_key=private_key,
                to=to,
                amount=amount,
                message=message
            )
            net_utils.broadcast_json_to_url(send_tx.serialize(), url="/new_transaction", node_list=[node])
        case "stake info":
            try:
                balance = net_utils.get_data_from_path(f"/utils/stake_info?address={address}", node)
                print(f"Stake amount: {balance}")
            except requests.exceptions.ConnectionError as e:
                print(f"{e.__class__.__name__}: {e}")
                print("[bold red]Network connection error")
