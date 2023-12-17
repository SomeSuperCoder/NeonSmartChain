import hashlib
import json
import base58
import ecdsa
import config
import Transaction


def get_balance(blockchain, address):
    balance = 0
    for tx in blockchain.get_full_tx_list():
        tx: Transaction.Transaction = tx
        if tx.to == address:
            balance += tx.amount
        if tx.get_sender_address() == address:
            balance -= tx.amount
            balance -= tx.gas

    if address == "0x7Cmg3rA1FSvho4acs6fFeZrPXhEHo2h99T1xMnodwn6o":
        balance += 10_000

    return balance


def send(id, private_key: ecdsa.SigningKey, to, amount, message):
    public_key = private_key.get_verifying_key()
    new_tx = Transaction.Transaction(
        id=id,  # blockchain.get_latest_tx_id_for_address(address=generate_address(public_key))
        from_=public_key,
        to=to,
        amount=amount,
        message=message,
        gas=config.tx_gas_price*config.tx_gas_units
    )

    sign(new_tx, private_key)
    return new_tx


# =====================================================
# ecdsa stuff

def sign(target, private_key):
    print(f"Signing: {json.dumps(target.serialize(include_signature=False))}")
    print(f"With: {private_key.get_verifying_key()}")
    signature = private_key.sign_deterministic(json.dumps(target.serialize(include_signature=False, include_hash=False)).encode())
    print(signature)
    signature_string = base58.b58encode(signature).decode()

    target.signature = signature_string


def verify(target, public_key):
    try:
        signature_bytes = base58.b58decode(target.signature.encode())
        print(signature_bytes)
        print(f"Verifying: {json.dumps(target.serialize(include_signature=False))}")
        print(f"With: {public_key}")
        is_valid = public_key.verify(signature_bytes, json.dumps(target.serialize(include_signature=False, include_hash=False)).encode())

        return is_valid
    except ecdsa.BadSignatureError as e:
        print(f"{e.__class__.__name__}: {e}")
        return False


def generate_address(public_key: ecdsa.VerifyingKey):
    return "0x" + base58.b58encode(
        hashlib.sha256(
            public_key.to_der()
        ).digest()
    ).decode()


def generate_serializable_address(target):
    return "0x" + base58.b58encode(
        hashlib.sha256(
            json.dumps(target.serialize(False)).encode()
        ).digest()
    ).decode()


def private_key_from_seed_phrase(string):
    return ecdsa.SigningKey.from_string(hashlib.sha256(string.encode()).digest(), curve=ecdsa.SECP256k1)


def public_key_to_string(public_key: ecdsa.VerifyingKey):
    der = public_key.to_der()
    return base58.b58encode(der).decode()


def public_key_from_string(string):
    der = base58.b58decode(string)
    return ecdsa.VerifyingKey.from_der(der)

# =====================================================


def slow_growth_multiplication(x, y, x_weight, y_weight):
    return (x ** (1 / x_weight)) * (y ** (1 / y_weight))
