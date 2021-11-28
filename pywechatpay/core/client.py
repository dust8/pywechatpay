from json import dumps
from urllib.parse import urlparse

import requests

from .credential import WechatPayCredential
from .downloader_mgr import mgr_instance
from .signer import Sha256WithRSASigner, SignatureResult
from .validator import WechatPayResponseValidator
from .verifier import SHA256WithRSAVerifier
from ..constants import VERSION, USER_AGENT_FORMAT, DEFAULT_TIMEOUT
from ..exceptions import WechatPayAPIException
from ..utils.pem import load_private_key


class Client:
    def __init__(self, signer=None, credential=None, validator=None, cipher=None):
        """

        :param signer: 签名器
        :param credential: 认证器
        :param validator: 验证器
        :param cipher: 加解密器
        """
        self.signer = signer
        self.credential = credential
        self.validator = validator
        self.cipher = cipher

        self.http_client = requests.Session()

    def request(self, method, url, params=None, data=None, json=None, headers={}, **kwargs):
        body = data or json
        sign_body = body if isinstance(body, str) else dumps(body) if body else ""
        up = urlparse(url)
        query = f"?{up.query}" if up.query else ""
        path = up.path + query
        authorization = self.credential.gen_authorization_header(method, path, sign_body)
        _headers = {
            "User-Agent": USER_AGENT_FORMAT % VERSION,
            "Authorization": authorization,
        }
        headers.update(_headers)

        if "timeout" not in kwargs:
            kwargs["timeout"] = DEFAULT_TIMEOUT

        response = self.http_client.request(method, url, params, data, headers=headers, json=json, **kwargs)

        # check is success
        self.check_response(response)

        # validate signature
        self.validator.validate(response.headers, response.text)

        return response

    @staticmethod
    def check_response(resp):
        if 200 <= resp.status_code <= 299:
            return

        raise WechatPayAPIException(resp.text)

    def sign(self, message: str) -> SignatureResult:
        """
        使用 signer 对字符串进行签名

        :param message: 待签名字符串
        :return:
        """
        return self.signer.sign(message)


def with_wechat_pay_auto_auth_cipher_using_downloader_mgr(mch_id: str, mch_cert_serial_no: str, mch_private_key: str,
                                                          mgr) -> Client:
    """一键初始化 Client，使其具备「签名/验签/敏感字段加解密」能力。
       需要使用者自行提供 CertificateDownloaderMgr 实现平台证书的自动更新
    """
    cert_visitor = mgr.get_certificate_visitor(mch_id)

    private_key = load_private_key(mch_private_key)
    signer = Sha256WithRSASigner(mch_id, mch_cert_serial_no, private_key)
    credential = WechatPayCredential(signer)
    validator = WechatPayResponseValidator(SHA256WithRSAVerifier(cert_visitor))
    return Client(signer=signer, credential=credential, validator=validator)


def with_wechat_pay_auto_auth_cipher(mch_id: str, mch_cert_serial_no: str, mch_private_key: str,
                                     mch_api_v3_key: str) -> Client:
    """
    一键初始化 Client，使其具备「签名/验签/敏感字段加解密」能力。
    同时提供证书定时更新功能（因此需要提供 mchAPIv3Key 用于证书解密），不再需要本地提供平台证书

    :param mch_id: 商户号
    :param mch_cert_serial_no: 商户证书序列号
    :param mch_private_key:  商户证书私钥
    :param mch_api_v3_key:  商户APIv3密钥
    :return:
    """
    if not mgr_instance.has_downloader(mch_id):
        mgr_instance.register_downloader_with_private_key(mch_id=mch_id, mch_cert_serial_no=mch_cert_serial_no,
                                                          mch_private_key=mch_private_key,
                                                          mch_api_v3_key=mch_api_v3_key)
    return with_wechat_pay_auto_auth_cipher_using_downloader_mgr(mch_id, mch_cert_serial_no, mch_private_key,
                                                                 mgr_instance)
