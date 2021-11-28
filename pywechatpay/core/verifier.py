import abc
from base64 import b64decode

from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256

from pywechatpay.exceptions import WechatPayException


class Verifier(metaclass=abc.ABCMeta):
    """数字签名验证者"""

    @abc.abstractmethod
    def verify(self, serial_no: str, message: str, signature: str):
        """
        验证. 不通过则报错

        :param serial_no: 序列号
        :param message: 待验签字符串
        :param signature: 签名
        :return:
        """


class SHA256WithRSAVerifier(Verifier):
    """SHA256WithRSA 数字签名验证者"""

    def __init__(self, cert_getter):
        self.cert_getter = cert_getter

    def verify(self, serial_no, message, signature):
        message_bytes = str.encode(message)
        signature = b64decode(signature)
        certificate = self.cert_getter.get(serial_no)
        if not certificate:
            raise WechatPayException(f"certificate[{serial_no}] not found in verifier")

        public_key = certificate.public_key()

        try:
            public_key.verify(signature, message_bytes, PKCS1v15(), SHA256())
        except Exception as ex:
            raise WechatPayException(f"validate verify fail serial=[{serial_no}] err={ex}")
