import time

from ..service import ServiceABC
from ...constants import WECHAT_PAY_API_SERVER
from ...utils.nonce import gen_noncestr


class AppApiService(ServiceABC):
    def pay_transactions_app(self, appid: str, mchid: str, description: str, out_trade_no: str, total: int,
                             notify_url: str, currency: str = "CNY", **kwargs) -> dict:
        """
        APP下单API
        https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_2_1.shtml

        :param appid: 应用ID
        :param mchid: 直连商户号
        :param description: 商品描述
        :param out_trade_no: 商户订单号
        :param total: 订单总金额，单位为分
        :param notify_url: 通知地址, 通知URL必须为直接可访问的URL，不允许携带查询串
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
        }
        content.update(kwargs)
        url = WECHAT_PAY_API_SERVER + "/v3/pay/transactions/app"
        result = self.client.request("post", url, json=content)
        return result.json()

    def prepay_with_request_payment(self, appid: str, mchid: str, description: str, out_trade_no: str, total: int,
                                    notify_url: str, currency: str = "CNY", **kwargs) -> dict:
        """
        APP支付下单，并返回调起支付的请求参数
        https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_2_1.shtml

        :param appid: 应用ID
        :param mchid: 直连商户号
        :param description: 商品描述
        :param out_trade_no: 商户订单号
        :param total: 订单总金额，单位为分
        :param notify_url: 通知地址, 通知URL必须为直接可访问的URL，不允许携带查询串
        :param currency: 货币类型, CNY：人民币
        :param kwargs: 可选参数
        :return:
        """
        result = self.pay_transactions_app(appid, mchid, description, out_trade_no, total, notify_url, currency,
                                           **kwargs)
        prepay_id = result["prepay_id"]
        timestamp = str(int(time.time()))
        nonce_str = gen_noncestr()
        message = "%s\n%s\n%s\n%s\n" % (appid, timestamp, nonce_str, prepay_id)
        pay_sign = self.client.sign(message).signature
        request_payment = {
            "appid": appid,
            "partnerid": mchid,
            "prepayid": prepay_id,
            "package": "Sign=WXPay",
            "noncestr": nonce_str,
            "timestamp": timestamp,
            "sign": pay_sign,
        }
        return request_payment

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
