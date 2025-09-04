# import aisuite as ai

# # 创建客户端并配置模型参数
# client = ai.Client()

# # 配置模型信息
# model = "claude-3-5-sonnet-20250219"  # 注意：你写的是claude-3-7，应该是claude-3-5
# base_url = "http://35.220.164.252:3888/v1/"
# api_key = "sk-3H9lsju4iRuXP8nsR3EpCAnidg88ltB4OAbv5aYkv1gvLk1V"
# max_tokens = 8192
# temperature = 0.0

# # 设置消息
# messages = [
#     {"role": "system", "content": "Respond in Pirate English. Always try to include the phrase - No rum No fun."},
#     {"role": "user", "content": "Tell me about artificial intelligence"}  # 补全用户消息
# ]

# # 方式1: 直接在chat调用中传递参数
# response = client.chat.completions.create(
#     model=model,
#     messages=messages,
#     max_tokens=max_tokens,
#     temperature=temperature,
#     # 如果aisuite支持自定义base_url，可能需要额外配置
# )

# print(response.choices[0].message.content)
from langchain.chat_models import init_chat_model

# 配置参数
model = "claude-3-7-sonnet-20250219"
base_url = "http://35.220.164.252:3888/v1/"
api_key = "sk-3H9lsju4iRuXP8nsR3EpCAnidg88ltB4OAbv5aYkv1gvLk1V"
max_tokens = 8192
temperature = 0.0

# 创建LLM实例
llm = init_chat_model(
    f"openai:{model}",  # 或者直接使用 openai:gpt-4 格式，取决于你的API兼容性
    api_key=api_key,
    base_url=base_url,
    max_tokens=max_tokens,
    temperature=temperature
)

# 设置消息
messages = [
    {"role": "system", "content": "Respond in Pirate English. Always try to include the phrase - No rum No fun."},
    {"role": "user", "content": "Tell me about artificial intelligence"}
]

# 调用
response = llm.invoke(messages)
print(response.content)
