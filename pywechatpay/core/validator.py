import abc

from .verifier import Verifier
from ..exceptions import WechatPayException


class Validator(metaclass=abc.ABCMeta):
    """验证器"""

    @abc.abstractmethod
    def validate(self, headers: dict, body: str):
        """
        验证. 不通过则报错

        :param headers: 请求头
        :param body: 请求主体
        :return:
        """


class NullValidateor(Validator):
    """空验证器，不对报文进行验证，对任意报文均不会返回错误，
       在不需要对报文签名进行验证的情况（如首次证书下载,微信支付账单文件下载）下使用
    """

    def validate(self, headers, body):
        return


class WechatPayValidator(Validator):
    def __init__(self, verifier: Verifier):
        self.verifier = verifier

    def validate(self, headers, body):
        request_id = headers.get("Request-ID", "")
        timestamp = headers.get("Wechatpay-Timestamp", "")
        nonce = headers.get("Wechatpay-Nonce", "")
        signature = headers.get("Wechatpay-Signature", "")
        serial = headers.get("Wechatpay-Serial", "")

        message = "%s\n%s\n%s\n" % (timestamp, nonce, body)

        try:
            self.verifier.verify(serial, message, signature)
        except Exception as ex:
            raise WechatPayException(f"validate verify fail serial=[{serial}] request-id=[{request_id}] err={ex}")


class WechatPayResponseValidator(WechatPayValidator):
    """微信支付 API v3 默认应答报文验证器"""
    pass


class WechatPayNotifyValidator(WechatPayValidator):
    """对接收到的微信支付 API v3 通知请求报文进行验证"""
    pass
