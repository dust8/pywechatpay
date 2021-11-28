from ..service import ServiceABC
from ...constants import WECHAT_PAY_API_SERVER


class H5ApiService(ServiceABC):
    def pay_transactions_h5(self, appid: str, mchid: str, description: str, out_trade_no: str, total: int,
                            notify_url: str, payer_client_ip: str, type: str = "Wap", currency: str = "CNY",
                            **kwargs) -> dict:
        """
        H5下单API
        https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_3_1.shtml

        :param appid: 应用ID
        :param mchid: 直连商户号
        :param description: 商品描述
        :param out_trade_no: 商户订单号
        :param total: 订单总金额，单位为分
        :param notify_url: 通知地址, 通知URL必须为直接可访问的URL，不允许携带查询串
        :param payer_client_ip: 订单总金额，单位为分
        :param type: 场景类型, 示例值：iOS, Android, Wap
        :param currency: 货币类型, CNY：人民币
        :param kwargs: 可选参数
        :return:
        """
        content = {
            "appid": appid,
            "mchid": mchid,
            "description": description,
            "out_trade_no": out_trade_no,
            "notify_url": notify_url,
            "amount": {"total": total, "currency": currency},
            "scene_info": {
                "payer_client_ip": payer_client_ip,
                "h5_info": {"type": type},
            },
        }
        content.update(kwargs)
        url = WECHAT_PAY_API_SERVER + "/v3/pay/transactions/h5"
        result = self.client.request("post", url, json=content)
        return result.json()

    def pay_transactions_id(self, mchid: str, transaction_id: str) -> dict:
        """
        微信支付订单号查询

        :param mchid: 直连商户号
        :param transaction_id: 微信支付订单号
        :return:
        """
        url = WECHAT_PAY_API_SERVER + f"/v3/pay/transactions/id/{transaction_id}?mchid={mchid}"
        result = self.client.request("get", url)
        return result.json()

    def pay_transactions_out_trade_no(self, mchid: str, out_trade_no: str) -> dict:
        """
        商户订单号查询

        :param mchid: 直连商户号
        :param out_trade_no: 商户订单号
        :return:
        """
        url = WECHAT_PAY_API_SERVER + f"/v3/pay/transactions/out-trade-no/{out_trade_no}?mchid={mchid}"
        result = self.client.request("get", url)
        return result.json()
