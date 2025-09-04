#!/usr/bin/env python3
import os
import requests

# # 从环境变量中获取 API 密钥
# api_key = os.getenv("API_KEY")  # 设置你的API密钥到环境变量
# api_url = "http://35.220.164.252:3888/v1/messages"  # 你的API URL

api_url = "http://35.220.164.252:3888/v1/chat/completions"
api_key = "sk-3H9lsju4iRuXP8nsR3EpCAnidg88ltB4OAbv5aYkv1gvLk1V"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "What is the capital of France?"}],
    "max_tokens": 100
}

response = requests.post(api_url, json=data, headers=headers)

if response.status_code == 200:
    print("API response:", response.json())
else:
    print(f"Error {response.status_code}: {response.text}") 