import random
import string


def gen_noncestr(k: int = 32) -> str:
    """
    生成随机串，随机串包含字母或数字

    :param k: 长度
    :return:
    """
    return "".join(random.sample(string.ascii_letters + string.digits, k))
