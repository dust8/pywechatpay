from .downloader import new_certificate_downloader


class PseudoCertificateDownloader:
    def __init__(self, mgr, mch_id: str):
        self.mgr = mgr
        self.mch_id = mch_id

    def get(self, serial_no: str):
        """
        获取某序列号的平台证书

        :param serial_no: 证书序列号
        :return:
        """
        return self.mgr.get_certificate(self.mch_id, serial_no)


class CertificateDownloaderMgr:
    """证书下载管理器"""

    def __init__(self):
        self.downloader_map = {}

    def get_certificate(self, mch_id: str, serial_no: str):
        """
        获取商户的某个平台证书

        :param mch_id: 商户号
        :param serial_no: 证书序列号
        :return:
        """
        downloader = self.downloader_map[mch_id]
        return downloader.get(serial_no)

    def get_certificate_visitor(self, mch_id: str):
        """
        获取某个商户的平台证书访问器

        :param mch_id: 商户号
        :return:
        """
        return PseudoCertificateDownloader(self, mch_id)

    def has_downloader(self, mch_id: str) -> bool:
        """
        检查是否已经注册过 mchID 这个商户的下载器

        :param mch_id: 商户号
        :return:
        """
        return mch_id in self.downloader_map

    def register_downloader_with_private_key(self, mch_id: str, mch_cert_serial_no: str, mch_private_key: str,
                                             mch_api_v3_key: str):
        """
        注册商户的平台证书下载器

        :param mch_id:
        :param mch_cert_serial_no:
        :param mch_private_key:
        :param mch_api_v3_key:
        :return:
        """
        downloader = new_certificate_downloader(mch_id, mch_cert_serial_no, mch_private_key, mch_api_v3_key)
        self.downloader_map[mch_id] = downloader


# 下载管理器单例
mgr_instance = CertificateDownloaderMgr()
