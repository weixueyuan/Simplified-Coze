# LangChain配置化LLM使用指南

## 概述

这是一个基于配置文件的LangChain LLM调用模块，支持多种模型和多种输入类型（文本、图片、视频、音频）。

## 文件结构

```
├── config.ini          # 配置文件
├── config_reader.py    # 配置读取模块
├── langchain_llm.py    # LangChain LLM模块
├── main.py            # 主程序
└── README_simple.md   # 使用说明
```

## 快速开始

### 1. 配置API密钥

编辑 `config.ini` 文件，设置你的API密钥：

```ini
[llm]
model = "claude-3-5-sonnet-latest"
base_url = "https://api.anthropic.com/v1/"
api_key = "your_actual_api_key_here"
max_tokens = 8192
temperature = 0.0
```

### 2. 运行程序

```bash
python main.py
```

### 3. 基本使用

```python
from langchain_llm import LangChainLLM

# 创建LLM实例
llm = LangChainLLM("config.ini")

# 文本处理
result = llm.smart_process("请介绍一下人工智能")

# 图片处理
result = llm.smart_process("请描述这张图片", file_path="image.jpg")

# 使用特定模型
result = llm.smart_process("请分析这个视频", file_path="video.mp4", section="claude")
```

## 配置文件格式

配置文件使用INI格式，每个模型一个section：

```ini
[模型名称]
model = "模型标识符"
base_url = "API基础URL"
api_key = "你的API密钥"
max_tokens = 8192
temperature = 0.0
```

## 支持的模型

### Anthropic Claude
```ini
[claude]
model = "claude-3-5-sonnet-latest"
base_url = "https://api.anthropic.com/v1/"
api_key = "your_anthropic_key"
```

### OpenAI GPT
```ini
[openai]
model = "gpt-4o"
base_url = "https://api.openai.com/v1/"
api_key = "your_openai_key"
```

### Google Gemini
```ini
[google]
model = "gemini-2.5-flash"
base_url = "https://generativelanguage.googleapis.com/"
api_key = "your_google_key"
```

### 通义千问
```ini
[qwen]
model = "qwen-turbo"
base_url = "https://dashscope.aliyuncs.com/api/v1/"
api_key = "your_dashscope_key"
```

### 智谱AI
```ini
[zhipu]
model = "glm-4"
base_url = "https://open.bigmodel.cn/api/paas/v4/"
api_key = "your_zhipu_key"
```

## 支持的文件类型

- **图片**: jpg, jpeg, png, gif, bmp, webp
- **视频**: mp4, avi, mov, wmv, flv, webm
- **音频**: wav, mp3, aac, flac, ogg, m4a

## 主要功能

### 1. 智能处理
```python
# 自动识别文件类型并处理
result = llm.smart_process("请分析这个文件", file_path="document.jpg")
```

### 2. 多模型支持
```python
# 使用不同的模型
result1 = llm.smart_process("问题1", section="claude")
result2 = llm.smart_process("问题2", section="openai")
```

### 3. 配置管理
```python
# 获取可用模型
models = llm.get_available_models()

# 获取模型配置
config = llm.get_model_config("claude")
```

## 错误处理

程序会自动处理以下错误：
- 配置文件不存在
- API密钥无效
- 文件不存在
- 不支持的文件类型
- 网络连接问题

## 注意事项

1. **API密钥安全**: 不要将真实的API密钥提交到版本控制系统
2. **文件大小**: 大文件可能需要更长的处理时间
3. **网络连接**: 确保能够访问相应的API服务
4. **模型限制**: 不同模型支持不同的输入类型和大小限制

## 示例输出

```
=== 当前配置 ===

[llm]
  model = claude-3-5-sonnet-latest
  base_url = https://api.anthropic.com/v1/
  api_key = sk-ant-...
  max_tokens = 8192
  temperature = 0.0

=== LangChain配置化LLM使用示例 ===

可用模型:
  llm: claude-3-5-sonnet-latest
  claude: claude-3-5-sonnet-latest
  openai: gpt-4o

=== 示例1：文本处理（使用默认配置） ===
结果: 人工智能（Artificial Intelligence，AI）的发展历史可以追溯到...
``` 