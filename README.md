# pywechatpay
[![PyPI version](https://badge.fury.io/py/pywechatpay.svg)](https://badge.fury.io/py/pywechatpay)

## 介绍

**pywechatpay** 是微信支付 `V3` 版接口的库.

## 安装

从 PyPi 安装:

```
$ pip install pywechatpay
```

## 使用教程
### 准备
参考微信官方文档准备好密钥, 证书文件和配置( [证书/密钥/签名介绍](https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay3_0.shtml))

### 初始化
``` python
from pywechatpay import WechatPay

mch_private_key_string = """
-----BEGIN PRIVATE KEY-----
xxx
-----END PRIVATE KEY-----
"""
wechat_public_key_string = """
-----BEGIN PUBLIC KEY-----
xxx
-----END PUBLIC KEY-----
"""

wechatpay = WechatPay(
    mchid="xxx",
    mch_serial_no="xxx",
    mch_private_key_string=mch_private_key_string.strip(),
    wechat_public_key_string=wechat_public_key_string.strip(),
    notify_url="http://xxx.com",
    app_appid="xxx",
    offi_appid="xxx",
    mini_appid="xxx",
)
```

### 接口
- APP支付 [pay/transactions/app](https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_2_1.shtml)
```python
order_string = wechatpay.pay_transactions_app(
    description="test", out_trade_no="test0001", amount=1,
)
``` 

- H5支付 [pay/transactions/h5](https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_3_1.shtml)
```python
order_string = wechatpay.pay_transactions_h5(
    description="test", out_trade_no="test0001", amount=1,
)
``` 

- JSAPI支付 [pay/transactions/jsapi](https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_1_1.shtml)
```python
order_string = wechatpay.pay_transactions_jsapi(
    description="test", out_trade_no="test0001", amount=1, payer="xxx"
)
``` 

- 小程序支付 [pay/transactions/jsapi](https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_5_1.shtml)
```python
order_string = wechatpay.pay_transactions_jsapi(
    description="test", out_trade_no="test0001", amount=1, payer="xxx", tag="mini"
)
``` 

- 订单查询 [pay/transactions/out-trade-no](https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_2_2.shtml)
```python
result = wechatpay.pay_transactions_out_trade_no("test0001")
```

