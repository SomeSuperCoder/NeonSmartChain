import hashlib
from Crypto.Cipher import AES
from Crypto import Random


def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)


def undo_pad(s):
    return s[:-ord(s[len(s) - 1:])]


def encrypt_text(text, password):
    """
    :param text:
    данные которые надо зашифоровать(это будет сид фраза)
    :param password:
    пароль пользователя
    :return:
    зашифрованый текст
    """
    key = hashlib.sha256(password.encode('utf-8')).digest()
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_text = iv + cipher.encrypt(pad(text).encode('utf-8'))
    return encrypted_text


def decrypt_text(encrypted_text, password):
    """

    :param encrypted_text:
    зашифорованый текст
    :param password:
    пароль
    :return:
    расшифрованый текст(это будет сид фраза)
    """
    key = hashlib.sha256(password.encode('utf-8')).digest()
    iv = encrypted_text[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_text = undo_pad(cipher.decrypt(encrypted_text[AES.block_size:]))
    return decrypted_text.decode('utf-8')


def main():
    while True:
        text = input("Enter the text to encrypt: ")
        password = input("Enter the password: ")

        encrypted_text = encrypt_text(text, password)
        print("Encrypted text:", encrypted_text)

        decrypted_text = decrypt_text(encrypted_text, password)
        print("Decrypted text:", decrypted_text)


if __name__ == "__main__":
    main()
