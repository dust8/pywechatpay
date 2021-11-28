# pywechatpay

[![PyPI version](https://badge.fury.io/py/pywechatpay.svg)](https://badge.fury.io/py/pywechatpay)

**pywechatpay** 是微信支付`V3`版接口的`python SDK`.

## 功能介绍

1. 接口 SDK. 请看 `services` 里面的 `README.md` 文档.
2. HTTP 客户端 `core.client`, 支持请求签名和应答验签. 如果 SDK 未支持你需要的接口, 请用此客户端发起请求.
3. 回调通知处理 `core.notify`, 支持微信支付回调通知的验证和解密.
4. 证书下载等辅助能力

## 使用教程

### 安装

从 PyPi 安装:

```
$ pip install pywechatpay
```

### 准备

参考微信官方文档准备好密钥, 证书文件和配置( [证书/密钥/签名介绍](https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay3_0.shtml))

### 初始化

``` python
from pywechatpay.core.client import with_wechat_pay_auto_auth_cipher


MCH_ID = "xxx"
MCH_SERIAL_NO = "xxx"
MCH_PRIVATE_KEY_STRING = "xxx"
APIv3_KEY = "xxx"

# 初始化 client, 并使它具有获取微信支付平台证书的能力
client = with_wechat_pay_auto_auth_cipher(MCH_ID, MCH_SERIAL_NO, MCH_PRIVATE_KEY_STRING, APIv3_KEY)
```

### 接口

- APP支付 [pay/transactions/app](https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_2_1.shtml)

```python
from pywechatpay.services.payments.app import AppApiService

svc = AppApiService(client)

# 方式一, 返回客户端调起微信支付的参数
result = svc.prepay_with_request_payment(appid="xxx", mchid="xxx", description="xxx", out_trade_no="xxx", total=1,
                                         notify_url="xxx")

# 方式二, 返回原微信返回的响应
result = svc.pay_transactions_app(appid="xxx", mchid="xxx", description="xxx", out_trade_no="xxx", total=1,
                                  notify_url="xxx")

# 查询订单
# 微信支付订单号查询
result = svc.pay_transactions_id(mchid="xxx", transaction_id="xxx")
# 商户订单号查询
result = svc.pay_transactions_out_trade_no(mchid="xxx", out_trade_no="xxx")
```

- H5支付 [pay/transactions/h5](https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_3_1.shtml)

```python
from pywechatpay.services.payments.h5 import H5ApiService

svc = H5ApiService(client)
result = svc.pay_transactions_h5(appid="xxx", mchid="xxx", description="xxx", out_trade_no="xxx", total=1,
                                 payer_client_ip="x.x.x.x", notify_url="xxx")
```

### 发送 HTTP 请求

如果 SDK 还未支持你需要的接口, 使用 core.client.Client 的 GET,POST 等方法发送 HTTP 请求,而不用关注签名,验签等逻辑

```python
# Native支付 https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_4_1.shtml
url = "https://api.mch.weixin.qq.com/v3/pay/transactions/native"
content = {
    "appid": "xxx",
    "mchid": "xxx",
    "description": "xxx",
    "out_trade_no": "xxx",
    "notify_url": "xxx",
    "amount": {"total": 1},
}
response = client.request("post", url, json=content)
print(response.json())
```

### 回调通知的验签和解密

```python
from pywechatpay.core import downloader_mgr
from pywechatpay.core.notify import new_notify_handler
from pywechatpay.core.verifier import SHA256WithRSAVerifier

# 为回调请求的头部, 字典类型
headers = {
    "xxx": "xxx",
}
# 为回调请求的内容, 字符串类型
body = "xxx"

cert_visitor = downloader_mgr.mgr_instance.get_certificate_visitor(mch_id="xxx")
handler = new_notify_handler(mch_api_v3_key="xxx", verifier=SHA256WithRSAVerifier(cert_visitor))
notify_req = handler.parse_notify_request(headers=headers, body=body)
```

## 参考链接

- [wechatpay-apiv3/wechatpay-go](https://github.com/wechatpay-apiv3/wechatpay-go)

