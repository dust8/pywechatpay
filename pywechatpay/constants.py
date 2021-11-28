# SDK 相关信息
VERSION = "0.1.0"  # SDK 版本
USER_AGENT_FORMAT = "PyWechatPay/%s"  # UserAgent中的信息

# 微信支付 API 地址
WECHAT_PAY_API_SERVER = 'https://api.mch.weixin.qq.com'

# 请求报文签名相关常量
SIGNATURE_MESSAGE_FORMAT = '%s\n%s\n%d\n%s\n%s\n'  # 数字签名原文格式
# 请求头中的 Authorization 拼接格式
HEADER_AUTHORIZATION_FORMAT = '%s mchid=\"%s\",nonce_str=\"%s\",timestamp=\"%d\",serial_no=\"%s\",signature=\"%s\"'

# 默认超时时间
DEFAULT_TIMEOUT = 30
