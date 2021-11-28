import json

from .validator import WechatPayNotifyValidator, Validator
from .verifier import Verifier
from ..exceptions import WechatPayException
from ..utils.aes import decrypt_aes246gcm


class Handler:
    """微信支付通知 Handler"""

    def __init__(self, mch_api_v3_key: str, validator: Validator):
        """

        :param mch_api_v3_key: 商户APIv3密钥
        :param validator: 验证器
        """
        self.mch_api_v3_key = mch_api_v3_key
        self.validator = validator

    def parse_notify_request(self, headers: dict, body: str):
        """
        解析微信支付通知

        :param headers: 请求头
        :param body: 请求主体
        :return:
        """
        try:
            self.validator.validate(headers=headers, body=body)
        except Exception as ex:
            raise WechatPayException(f"not valid pywechatpay notify:{ex}")

        ret = json.loads(body)
        plain_text = decrypt_aes246gcm(self.mch_api_v3_key, ret["resource"]["nonce"], ret["resource"]["ciphertext"],
                                       ret["resource"]["associated_data"])
        return plain_text


def new_notify_handler(mch_api_v3_key: str, verifier: Verifier) -> Handler:
    """
    创建通知处理器

    :param mch_api_v3_key: 商户APIv3密钥
    :param verifier: 验证者
    :return:
    """
    return Handler(mch_api_v3_key=mch_api_v3_key, validator=WechatPayNotifyValidator(verifier))
