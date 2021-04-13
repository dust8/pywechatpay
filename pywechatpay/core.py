import json
import logging
import random
import string
import time
from base64 import b64encode, b64decode

import requests
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5
from OpenSSL.crypto import load_certificate, FILETYPE_PEM
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .exceptions import WechatPayException

logger = logging.getLogger(__name__)


class WechatPay:
    """

    加密：公钥加密，私钥解密；
    签名：私钥签名，公钥验签。
    """

    def __init__(
        self,
        mchid: str,
        mch_serial_no: str,
        mch_private_key_string: str,
        wechat_public_key_string: str,
        notify_url: str,
        apiv3_key: str = None,
        **kwargs,
    ):
        """https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay3_0.shtml

        :param mchid: 商户号
        :param mch_private_key_string: 商户API私钥
        :param wechat_public_key_string: 平台公钥
        :param notify_url:
        :param apiv3_key: APIv3密钥
        """
        self.mchid = mchid
        self._mch_serial_no = mch_serial_no
        self._mch_private_key_string = mch_private_key_string
        self._wechat_public_key_string = wechat_public_key_string
        self.apiv3_key = apiv3_key
        self._notify_url = notify_url

        # app appid
        self._app_appid = kwargs.get("app_appid", None)
        # 公众号 appid
        self._offi_appid = kwargs.get("offi_appid", None)
        # 小程序 appid
        self._mini_appid = kwargs.get("mini_appid", None)
        self._timeout = kwargs.get("timeout", 10)

        self._gateway = "https://api.mch.weixin.qq.com"
        self._mch_private_key = None
        self._wechat_public_key = None
        self._session = requests.Session()

        self._load_key()

    def _load_key(self):
        self._mch_private_key = RSA.importKey(self._mch_private_key_string)
        self._wechat_public_key = RSA.importKey(self._wechat_public_key_string)

    @staticmethod
    def generate_noncestr(k: int = 32):
        """生成随机串，随机串包含字母或数字

        :param k: 长度
        :return:
        """
        return "".join(random.sample(string.ascii_letters + string.digits, k))

    @staticmethod
    def generate_timestamp():
        return str(int(time.time()))

    @staticmethod
    def generate_sign_str(sign_list):
        return "\n".join(sign_list) + "\n"

    @staticmethod
    def sign_str(
        method: str,
        url_path: str,
        request_body: str,
        timestamp: str = None,
        nonce_str: str = None,
    ) -> str:
        """构造签名串

        :param method:
        :param url_path:
        :param request_body:
        :param timestamp:
        :param nonce_str:
        :return:

        https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_0.shtml
        """
        sign_list = [method, url_path, timestamp, nonce_str, request_body]
        return "\n".join(sign_list) + "\n"

    @staticmethod
    def verify_sign_str(timestamp: str, nonce_str: str, response_body: str) -> str:
        """构造验签名串

        :param timestamp:
        :param nonce_str:
        :param response_body:
        :return:

        https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_1.shtml#part-2
        """
        sign_list = [timestamp, nonce_str, response_body]
        return "\n".join(sign_list) + "\n"

    @staticmethod
    def get_serial_no(cert_pem_string: str) -> str:
        """获取证书序列号

        :param cert_pem_string: 证书字符串
        :return: 证书序列号
        """
        x509 = load_certificate(FILETYPE_PEM, cert_pem_string)
        return hex(x509.get_serial_number())[2:].upper()

    @staticmethod
    def decrypt(key: str, nonce: str, ciphertext: str, associated_data: str) -> bytes:
        """证书和回调报文解密

        :param key: APIv3密钥
        :param nonce:
        :param ciphertext:
        :param associated_data:
        :return:

        https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_2.shtml
        """
        key_bytes = str.encode(key)
        nonce_bytes = str.encode(nonce)
        ad_bytes = str.encode(associated_data)
        data = b64decode(ciphertext)

        aesgcm = AESGCM(key_bytes)
        return aesgcm.decrypt(nonce_bytes, data, ad_bytes)

    def decrypt_response(
        self, nonce: str, ciphertext: str, associated_data: str
    ) -> dict:
        return json.loads(
            self.decrypt(self.apiv3_key, nonce, ciphertext, associated_data)
        )

    def sign(self, sign_str: str) -> str:
        """计算签名值

        :param sign_str:
        :return:
        """
        signer = PKCS1_v1_5.new(self._mch_private_key)
        digest = SHA256.new(sign_str.encode())
        sign = b64encode(signer.sign(digest)).decode()
        return sign

    def _verify_sign(self, sign_str: str, signature) -> bool:
        signer = PKCS1_v1_5.new(self._wechat_public_key)
        digest = SHA256.new(sign_str.encode())
        return signer.verify(digest, b64decode(signature))

    def verify(self, timestamp, nonce, response_body, signature) -> bool:
        sign_str = self.verify_sign_str(timestamp, nonce, response_body)
        return self._verify_sign(sign_str, signature)

    def authorization(
        self,
        method: str,
        url_path: str,
        request_body: str,
        timestamp: str = None,
        nonce_str: str = None,
    ) -> str:
        """设置HTTP头

        :param method:
        :param url_path:
        :param request_body:
        :param timestamp:
        :param nonce_str:
        :return:
        """
        if timestamp is None:
            timestamp = self.generate_timestamp()

        if nonce_str is None:
            nonce_str = self.generate_noncestr()

        signstr = self.sign_str(
            method=method,
            url_path=url_path,
            request_body=request_body,
            timestamp=timestamp,
            nonce_str=nonce_str,
        )
        signature = self.sign(signstr)
        authorization = (
            "WECHATPAY2-SHA256-RSA2048 "
            f'mchid="{self.mchid}",'
            f'nonce_str="{nonce_str}",'
            f'signature="{signature}",'
            f'timestamp="{timestamp}",'
            f'serial_no="{self._mch_serial_no}"'
        )
        return authorization

    def build_body(self, content: dict, notify_url: str = None) -> dict:
        data = {"mchid": self.mchid, "notify_url": notify_url or self._notify_url}
        data.update(content)
        return data

    def _verify_and_return_sync_response(self, response, response_type, tag=None):
        timestamp = response.headers.get("Wechatpay-Timestamp", "")
        nonce = response.headers.get("Wechatpay-Nonce", "")
        signature = response.headers.get("Wechatpay-Signature", "")
        serial = response.headers.get("Wechatpay-Serial", "")
        response_body = response.text

        is_verify = self.verify(timestamp, nonce, response_body, signature)
        if is_verify is False:
            raise WechatPayException("wechatpay is not verify")

        data = response.json()

        noncestr = self.generate_noncestr()
        timestamp = self.generate_timestamp()

        if response_type == "/v3/pay/transactions/jsapi":
            # JSAPI调起支付API https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_1_4.shtml
            # 小程序调起支付API https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_5_4.shtml
            if tag == "mini":
                # 小程序支付
                appid = self._mini_appid
            else:
                # 公众号支付
                appid = self._offi_appid

            sign_str = self.generate_sign_str(
                [appid, timestamp, noncestr, f'prepay_id={data["prepay_id"]}']
            )
            sign = self.sign(sign_str)
            data = {
                "appid": appid,
                "package": f'prepay_id={data["prepay_id"]}',
                "nonceStr": noncestr,
                "timeStamp": timestamp,
                "signType": "RSA",
                "paySign": sign,
            }
        elif response_type == "/v3/pay/transactions/app":
            # APP调起支付API https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_2_4.shtml
            sign_str = self.generate_sign_str(
                [self._app_appid, timestamp, noncestr, data["prepay_id"]]
            )
            sign = self.sign(sign_str)
            data = {
                "appid": self._app_appid,
                "partnerid": self.mchid,
                "prepayid": data["prepay_id"],
                "package": "Sign=WXPay",
                "noncestr": noncestr,
                "timestamp": timestamp,
                "sign": sign,
            }
        elif response_type == "/v3/pay/transactions/h5":
            # H5调起支付API https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_3_4.shtml
            pass

        return data

    def verified_sync_response_for_get(self, data, response_type):
        url = f"{self._gateway}{response_type}/{data}"
        request_body = ""
        headers = {
            "Authorization": self.authorization(
                method="GET",
                url_path=f"{response_type}/{data}",
                request_body=request_body,
            )
        }
        response = self._session.get(url=url, headers=headers, timeout=self._timeout)
        response.raise_for_status()
        return self._verify_and_return_sync_response(response, response_type)

    def verified_sync_response(self, data, response_type, tag):
        url = f"{self._gateway}{response_type}"
        request_body = json.dumps(data)
        headers = {
            "Authorization": self.authorization(
                method="POST", url_path=response_type, request_body=request_body
            )
        }
        response = self._session.post(
            url=url, json=data, headers=headers, timeout=self._timeout
        )
        response.raise_for_status()
        return self._verify_and_return_sync_response(response, response_type, tag)

    def pay_transactions_jsapi(
        self,
        description: str,
        out_trade_no: str,
        amount: int,
        payer: str,
        currency: str = "CNY",
        notify_url: str = None,
        tag: str = "offi",
        **kwargs,
    ) -> dict:
        """公众号和小程序 统一下单API

        :param description: 商品描述
        :param out_trade_no: 商户订单号
        :param amount: 订单总金额，单位为分
        :param payer: openid
        :param currency: 货币类型, CNY：人民币
        :param notify_url: 通知地址, 通知URL必须为直接可访问的URL，不允许携带查询串
        :param tag: 可选参数, 默认公众号 offi, 可选小程序 mini
        :param kwargs: 可选参数
        :return:
        """
        content = {
            "appid": self._mini_appid if tag == "mini" else self._offi_appid,
            "description": description,
            "out_trade_no": out_trade_no,
            "amount": {"total": amount, "currency": currency},
            "payer": {"openid": payer},
        }
        content.update(kwargs)
        data = self.build_body(content, notify_url)
        response_type = "/v3/pay/transactions/jsapi"
        return self.verified_sync_response(data, response_type, tag)

    def pay_transactions_app(
        self,
        description,
        out_trade_no,
        amount,
        currency="CNY",
        notify_url=None,
        **kwargs,
    ) -> dict:
        """app 统一下单API

        :param description: 商品描述
        :param out_trade_no: 商户订单号
        :param amount: 订单总金额，单位为分
        :param currency: 货币类型, CNY：人民币
        :param notify_url: 通知地址, 通知URL必须为直接可访问的URL，不允许携带查询串
        :param kwargs: 可选参数
        :return:
        """
        content = {
            "appid": self._app_appid,
            "description": description,
            "out_trade_no": out_trade_no,
            "amount": {"total": amount, "currency": currency},
        }
        content.update(kwargs)
        data = self.build_body(content, notify_url)
        response_type = "/v3/pay/transactions/app"
        return self.verified_sync_response(data, response_type)

    def pay_transactions_h5(
        self,
        description,
        out_trade_no,
        amount,
        currency="CNY",
        notify_url=None,
        **kwargs,
    ) -> dict:
        """h5 统一下单API

        :param description: 商品描述
        :param out_trade_no: 商户订单号
        :param amount: 订单总金额，单位为分
        :param currency: 货币类型, CNY：人民币
        :param notify_url: 通知地址, 通知URL必须为直接可访问的URL，不允许携带查询串
        :param kwargs: 可选参数
        :return:
        """
        content = {
            "appid": self._app_appid or self._offi_appid,
            "description": description,
            "out_trade_no": out_trade_no,
            "amount": {"total": amount, "currency": currency},
        }
        content.update(kwargs)
        data = self.build_body(content, notify_url)
        response_type = "/v3/pay/transactions/h5"
        return self.verified_sync_response(data, response_type)

    def pay_transactions_out_trade_no(self, out_trade_no: str) -> dict:
        """商户订单号查询

        :param out_trade_no: 商户订单号
        :return:
        """
        data = f"{out_trade_no}?mchid={self.mchid}"
        response_type = "/v3/pay/transactions/out-trade-no"
        return self.verified_sync_response_for_get(data, response_type)
