from .credential import WechatPayCredential
from .signer import Sha256WithRSASigner
from .validator import WechatPayResponseValidator, NullValidateor
from .verifier import SHA256WithRSAVerifier
from ..constants import WECHAT_PAY_API_SERVER
from ..exceptions import WechatPayException
from ..utils.aes import decrypt_aes246gcm
from ..utils.pem import load_certificate, load_private_key


class CertificateDownloader:
    """证书下载器"""

    def __init__(self, client, mch_api_v3_key: str):
        self.client = client
        self.mch_api_v3_key = mch_api_v3_key

        self.cert_contents = {}
        self.certificates = {}

    def get(self, serial_no: str):
        """
        获取证书序列号对应的平台证书

        :param serial_no: 证书序列号
        :return:
        """
        return self.certificates.get(serial_no)

    def get_newest_serial(self):
        """获取最新的平台证书的证书序列号"""
        return ""

    def download_certificates(self):
        """立即下载平台证书列表"""
        url = WECHAT_PAY_API_SERVER + "/v3/certificates"
        result = self.client.request("get", url)
        data = result.json()
        raw_cert_content_map = {}
        certificate_map = {}
        for encrypt_certificate in data["data"]:
            cert_content = self.decrypt_certificate(encrypt_certificate["encrypt_certificate"])
            certificate = load_certificate(cert_content)

            serial_no = encrypt_certificate["serial_no"]
            raw_cert_content_map[serial_no] = cert_content
            certificate_map[serial_no] = certificate

        if len(certificate_map.keys()) == 0:
            raise WechatPayException("no certificate downloaded")

        self.update_certificates(raw_cert_content_map, certificate_map)

    def decrypt_certificate(self, encrypt_certificate):
        try:
            cert_content = decrypt_aes246gcm(self.mch_api_v3_key, encrypt_certificate["nonce"],
                                             encrypt_certificate["ciphertext"], encrypt_certificate["associated_data"])
        except Exception as ex:
            raise WechatPayException(f"decrypt downloaded certificate failed:{ex}")
        return cert_content

    def update_certificates(self, cert_contents, certificates):
        self.cert_contents = cert_contents
        self.certificates = certificates

        self.client.validator = WechatPayResponseValidator(SHA256WithRSAVerifier(certificates))


def new_certificate_downloader_with_client(client, mch_api_v3_key: str) -> CertificateDownloader:
    downloader = CertificateDownloader(client=client, mch_api_v3_key=mch_api_v3_key)
    downloader.download_certificates()
    return downloader


def new_certificate_downloader(mch_id: str, mch_cert_serial_no: str, mch_private_key: str,
                               mch_api_v3_key: str) -> CertificateDownloader:
    """
    创建证书下载器

    :param mch_id:
    :param mch_cert_serial_no:
    :param mch_private_key:
    :param mch_api_v3_key:
    :return:
    """
    private_key = load_private_key(mch_private_key)
    signer = Sha256WithRSASigner(mch_id, mch_cert_serial_no, private_key)
    credential = WechatPayCredential(signer)
    validator = NullValidateor()

    from .client import Client
    client = Client(signer=signer, credential=credential, validator=validator)
    return new_certificate_downloader_with_client(client=client, mch_api_v3_key=mch_api_v3_key)
