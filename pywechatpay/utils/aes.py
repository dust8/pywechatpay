from base64 import b64decode

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def decrypt_aes246gcm(key: str, nonce: str, ciphertext: str, associated_data: str) -> str:
    key_bytes = str.encode(key)
    nonce_bytes = str.encode(nonce)
    ad_bytes = str.encode(associated_data)
    data = b64decode(ciphertext)
    aesgcm = AESGCM(key_bytes)
    return aesgcm.decrypt(nonce_bytes, data, ad_bytes).decode()
