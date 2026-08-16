import pytest
import json
from spark_client import SparkLiteClient

# 参数化测试数据
normal_chat_cases = [
    ("简单问候", "你好"),
    ("代码提问", "写一段Python冒泡排序"),
    ("简短科普", "什么是单元测试")
]
invalid_model_cases = ["generalv3.5", "4.0Ultra", "abc123"]
tool_unsupported_case = {
    "model": "lite",
    "messages": [{"role": "user", "content": "今天天气"}],
    "tools": [{"type": "web_search", "web_search": {"enable": True}}]
}

client = SparkLiteClient()

# 工具函数：统一解析响应，兼容成功/401错误两种结构
def parse_response(resp):
    try:
        return resp.json()
    except Exception:
        return {}

# ====================== 正向业务测试 ======================
@pytest.mark.parametrize("case_name, user_input", normal_chat_cases)
def test_normal_chat(case_name, user_input):
    print("="*60)
    print(f"【正向用例执行开始】用例名称：{case_name}，用户提问：{user_input}")
    req = {
        "model": "lite",
        "messages": [{"role": "user", "content": user_input}],
        "max_tokens": 1024
    }
    resp = client.chat_completion(req)
    res_json = parse_response(resp)

    print(f"请求状态码：{resp.status_code}")
    print(f"接口完整返回报文：{json.dumps(res_json, ensure_ascii=False, indent=2)}")

    # 合法请求必须200，且code=0
    assert resp.status_code == 200, f"鉴权失败，请检查API_KEY！状态码{resp.status_code}"
    assert res_json.get("code", -1) == 0, f"业务失败：{res_json.get('message','无错误信息')}"
    assert len(res_json["choices"]) > 0
    answer = res_json["choices"][0]["message"]["content"]
    assert len(answer) > 0
    assert "prompt_tokens" in res_json["usage"]

    print(f"【{case_name} 执行成功】模型回复内容：{answer[:100]}...")
    print(f"本次消耗token：输入{res_json['usage']['prompt_tokens']}，输出{res_json['usage']['completion_tokens']}，总{res_json['usage']['total_tokens']}")
    print("="*60 + "\n")

# ====================== 非法密钥鉴权测试 ======================
def test_invalid_auth():
    print("="*60)
    print("【异常用例执行开始】非法密钥鉴权测试，使用错误密钥发起请求")
    bad_client = SparkLiteClient(api_key="wrong_key_123456")
    req = {
        "model": "lite",
        "messages": [{"role": "user", "content": "测试"}]
    }
    resp = bad_client.chat_completion(req)
    res_json = parse_response(resp)

    print(f"请求状态码：{resp.status_code}")
    print(f"接口完整返回报文：{json.dumps(res_json, ensure_ascii=False, indent=2)}")

    assert resp.status_code == 401
    assert "apikey" in res_json["message"] or "HMAC" in res_json["message"]
    print(f"【非法密钥用例执行成功】捕获预期鉴权错误，错误提示：{res_json['message']}")
    print("="*60 + "\n")

# ====================== 非法model参数 ======================
@pytest.mark.parametrize("wrong_model", invalid_model_cases)
def test_invalid_model(wrong_model):
    print("="*60)
    print(f"【异常用例执行开始】非法模型参数测试，传入model={wrong_model}")
    req = {
        "model": wrong_model,
        "messages": [{"role": "user", "content": "测试"}]
    }
    resp = client.chat_completion(req)
    res_json = parse_response(resp)

    print(f"请求状态码：{resp.status_code}")
    print(f"接口完整返回报文：{json.dumps(res_json, ensure_ascii=False, indent=2)}")

    if resp.status_code == 401:
        pytest.fail("API密钥错误，无法执行该用例，请先修复.env")
    # 只要返回包含error节点，说明模型参数非法，测试通过
    assert "error" in res_json
    err_info = res_json["error"]
    # 修复：把 err['code'] → err_info['code']
    print(f"【非法model用例执行成功】捕获预期参数/权限错误，错误码：{err_info['code']}，错误描述：{err_info['message']}")
    print("="*60 + "\n")

# ====================== Lite不支持web_search插件 ======================
def test_unsupported_websearch():
    print("="*60)
    print("【边界用例执行开始】Lite传入不支持的web_search联网插件测试")
    resp = client.chat_completion(tool_unsupported_case)
    res_json = parse_response(resp)

    print(f"请求状态码：{resp.status_code}")
    print(f"接口完整返回报文：{json.dumps(res_json, ensure_ascii=False, indent=2)}")

    if resp.status_code == 401:
        pytest.fail("API密钥错误，无法执行该用例，请先修复.env")
    # Lite忽略不支持的tools，正常返回code=0
    assert res_json.get("code") == 0
    # 验证返回内容没有联网搜索信源
    assert "search_ref" not in res_json
    print(f"【插件兼容性用例执行成功】Lite自动忽略不支持的web_search参数，正常返回对话：{res_json['choices'][0]['message']['content']}")
    print("="*60 + "\n")

# ====================== 流式输出测试 ======================
def test_stream_response():
    print("="*60)
    print("【边界用例执行开始】流式SSE返回解析测试")
    req = {
        "model": "lite",
        "messages": [{"role": "user", "content": "流式测试"}],
        "stream": True
    }
    resp = client.stream_chat(req)
    print(f"流式接口状态码：{resp.status_code}")

    assert resp.status_code == 200, "流式接口鉴权失败，请检查API_KEY"

    lines = []
    full_content = ""
    for line in resp.iter_lines(decode_unicode="utf-8"):
        # 过滤空行、结束标记
        if not line or line == "data:[DONE]":
            continue
        if line.startswith("data:"):
            # 清洗前缀、首尾空格
            json_str = line.replace("data:", "").strip()
            if not json_str:
                continue
            try:
                data = json.loads(json_str)
                lines.append(data)
                delta_text = data["choices"][0]["delta"].get("content", "")
                full_content += delta_text
                print(f"流式分片数据：{json.dumps(data, ensure_ascii=False, indent=1)}")
            except json.JSONDecodeError:
                print(f"跳过损坏分片：{line}")
                continue
    # 必须至少有一条有效分片
    assert len(lines) > 0, "流式接口未返回有效分片数据"
    first_chunk = lines[0]
    assert first_chunk["code"] == 0
    assert "delta" in first_chunk["choices"][0]
    print(f"【流式测试执行成功】累计拼接完整回答：{full_content}")
    print("="*60 + "\n")
