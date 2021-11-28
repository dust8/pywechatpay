from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import load_pem_x509_certificate


def format_private_key(private_key_str):
    """
    规整私钥格式

    :param private_key_str: 私钥字符串
    :return:
    """
    pem_start = "-----BEGIN PRIVATE KEY-----\n"
    pem_end = "\n-----END PRIVATE KEY-----"
    if not private_key_str.startswith(pem_start):
        private_key_str = pem_start + private_key_str
    if not private_key_str.endswith(pem_end):
        private_key_str = private_key_str + pem_end
    return private_key_str


def load_certificate(certificate_str: str):
    """
    载入证书

    :param certificate_str: 证书字符串
    :return:
    """
    certificate_bytes = str.encode(certificate_str)
    return load_pem_x509_certificate(certificate_bytes)


def load_private_key(private_key_str: str):
    """
    载入私钥

    :param private_key_str: 私钥字符串
    :return:
    """
    private_key_bytes = str.encode(format_private_key(private_key_str))
    return load_pem_private_key(private_key_bytes, password=None)
