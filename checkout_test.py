# checkout_test.py 修复版本（评审通过代码）
import requests
import os
from dotenv import load_dotenv

# 加载环境配置文件，分离环境接口地址
load_dotenv()
PAY_API_URL = os.getenv("PAY_API_URL")

def create_pay_order(user_id: int, amount: float) -> str:
    """
    发起支付订单接口请求
    :param user_id: 用户唯一ID，整型
    :param amount: 支付金额，浮点正数
    :return: 接口返回文本结果
    """
    # 入参合法性校验
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("用户ID必须为正整数")
    if not isinstance(amount, float) or amount <= 0:
        raise ValueError("支付金额必须为大于0的数字")

    request_data = {
        "user_id": user_id,
        "pay_amount": amount
    }
    # 捕获网络异常
    try:
        resp = requests.post(PAY_API_URL, json=request_data, timeout=5)
        # 校验接口响应状态
        if resp.status_code == 200:
            return f"支付请求成功，响应内容：{resp.text}"
        else:
            return f"接口调用失败，状态码：{resp.status_code}，详情：{resp.text}"
    except requests.exceptions.RequestException as e:
        return f"网络请求异常：{str(e)}"
