# checkout_test.py 缺陷版本（评审前代码）
import requests

# 无文档注释、变量命名无意义、硬编码地址、无异常捕获、无参数校验
def pay(a,b):
    url = "https://127.0.0.1:8080/api/pay"
    data = {"num":a,"money":b}
    res = requests.post(url,data)
    txt = res.text
    return txt
