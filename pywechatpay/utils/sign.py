from base64 import b64encode

from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256


def sign_sha256_with_rsa(message: str, private_key) -> str:
    message_bytes = str.encode(message)
    signature = private_key.sign(message_bytes, padding=PKCS1v15(), algorithm=SHA256())
    return b64encode(signature).decode()
