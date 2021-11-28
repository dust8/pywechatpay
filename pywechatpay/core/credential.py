import time

from .signer import Signer
from ..constants import SIGNATURE_MESSAGE_FORMAT, HEADER_AUTHORIZATION_FORMAT
from ..utils.nonce import gen_noncestr


class WechatPayCredential:
    """认证器"""

    def __init__(self, signer: Signer):
        """

        :param signer: 签名器
        """
        self.signer = signer

    def gen_authorization_header(self, method: str, url: str, body: str) -> str:
        """
        签名生成
        https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_0.shtml

        :param method: 请求方法
        :param url: 请求的绝对URL，并去除域名部分得到参与签名的URL
        :param body: 请求报文主体
        :return:
        """
        timestamp = time.time()
        nonce_str = gen_noncestr()
        message = SIGNATURE_MESSAGE_FORMAT % (method.upper(), url, timestamp, nonce_str, body)
        signature_result = self.signer.sign(message)
        authorization_type = f"WECHATPAY2-{self.signer.algorithm()}"
        authorization = HEADER_AUTHORIZATION_FORMAT % (authorization_type, signature_result.mch_id, nonce_str,
                                                       timestamp, signature_result.cert_serial_no,
                                                       signature_result.signature)
        return authorization
