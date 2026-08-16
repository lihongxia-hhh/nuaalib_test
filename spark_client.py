import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

class SparkLiteClient:
    def __init__(self, api_key: str = API_KEY):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def chat_completion(self, req_data: dict):
        """发起非流式对话请求"""
        resp = requests.post(BASE_URL, headers=self.headers, json=req_data, timeout=30)
        return resp

    def stream_chat(self, req_data: dict):
        """发起流式对话请求"""
        req_data["stream"] = True
        resp = requests.post(BASE_URL, headers=self.headers, json=req_data, stream=True, timeout=30)
        return resp
