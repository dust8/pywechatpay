import abc
from collections import namedtuple

from ..utils.sign import sign_sha256_with_rsa

SignatureResult = namedtuple("SignatureResult", ["mch_id", "cert_serial_no", "signature"])


class Signer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def sign(self, message: str) -> SignatureResult:
        """
        签名

        :param message: 待签名字符串
        :return:
        """

    @abc.abstractmethod
    def algorithm(self) -> str:
        """签名算法名称"""


class Sha256WithRSASigner(Signer):
    def __init__(self, mch_id: str, cert_serial_no: str, private_key):
        self.mch_id = mch_id
        self.cert_serial_no = cert_serial_no
        self.private_key = private_key

    def sign(self, message: str) -> SignatureResult:
        signature = sign_sha256_with_rsa(message, self.private_key)
        return SignatureResult(self.mch_id, self.cert_serial_no, signature)

    def algorithm(self) -> str:
        return "SHA256-RSA2048"
