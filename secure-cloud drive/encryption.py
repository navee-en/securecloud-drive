from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"


def generate_key():
    key = Fernet.generate_key()

    with open(KEY_FILE, "wb") as f:
        f.write(key)


def load_key():
    return open(KEY_FILE, "rb").read()


if not os.path.exists(KEY_FILE):
    generate_key()

cipher = Fernet(load_key())


def encrypt_file(filepath):
    with open(filepath, "rb") as f:
        data = f.read()

    encrypted = cipher.encrypt(data)

    with open(filepath, "wb") as f:
        f.write(encrypted)


def decrypt_file(filepath):
    with open(filepath, "rb") as f:
        data = f.read()

    decrypted = cipher.decrypt(data)

    with open(filepath, "wb") as f:
        f.write(decrypted)