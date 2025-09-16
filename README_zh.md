# LangChain 流水线系统

一个基于 LangChain 的多轮 AI 处理流水线系统，支持多模态输入输出（文本、图片、视频），采用模块化架构设计。

## ✨ 特性

- 🔄 **多轮流水线处理**：支持配置驱动的多轮 AI 处理流程
- 🎯 **多模态支持**：支持文本、图片、视频的输入和输出
- 🧠 **智能记忆管理**：跨轮次的数据传递和变量替换
- 📊 **多种输出方式**：控制台输出 + 文件保存
- 🎨 **彩色日志系统**：分级日志记录，支持文件轮转
- 🔧 **模块化架构**：易于扩展和维护

## 📁 项目结构

```
langchain/
├── config/                 # 配置模块
│   ├── config_reader.py   # 配置文件读取器
│   ├── config_example.ini # 配置文件示例
│   └── config.ini         # 主配置文件（不会被git追踪）
├── core/                   # 核心模块
│   ├── langchain_llm.py   # LangChain LLM 封装
│   ├── pipeline_controller.py  # 流水线控制器
│   └── pipeline_memory.py # 流水线记忆管理
├── processors/            # 处理器模块
│   ├── input_processor.py # 输入处理器
│   └── output_processor.py # 输出处理器
├── utils/                 # 工具模块
│   ├── file_utils.py      # 文件处理工具
│   ├── data_utils.py      # 数据处理工具
│   └── log_config.py      # 日志配置
├── examples/              # 示例代码
│   └── logging_example.py # 日志使用示例
├── input/                 # 输入文件目录
├── outputs/               # 输出文件目录
├── logs/                  # 日志文件目录
├── main.py               # 主程序入口
├── requirements.txt      # 依赖包列表
├── .gitignore            # Git 忽略文件
├── README.md             # 英文说明文档
└── README_zh.md          # 中文说明文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd langchain

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

复制示例配置文件并填入你的真实信息：

```bash
# 复制示例配置文件
cp config/config_example.ini config/config.ini

# 编辑配置文件，填入你的 API 密钥和基础URL
vim config/config.ini
```

配置文件格式：

```ini
[openai]
model = gpt-4o
api_key = your-api-key
base_url = https://api.openai.com/v1
prompt = 你的提示词内容

[claude]
model = claude-3-5-sonnet-20241022
api_key = your-anthropic-key
base_url = https://api.anthropic.com
prompt = 你的提示词内容
```

### 3. 运行程序

```bash
python main.py
```

**⚠️ 安全提醒：**
- `config/config.ini` 包含敏感的 API 密钥，已被添加到 `.gitignore` 中
- 请勿将真实的 API 密钥提交到版本控制系统
- 使用 `config/config_example.ini` 作为模板创建你的配置文件

## 📝 使用说明

### 输入数据格式

```python
raw_input = {
    "text": "文本内容",
    "image": "/path/to/image.jpg",  # 图片路径或 base64
    "video": "/path/to/video.mp4",  # 视频路径或 base64
    "filename": "output_name",      # 输出文件名
    "promptVariables": {            # 提示词变量（可选）
        "country": "中国",
        "age": 18
    }
}
```

### 输出文件结构

系统会按照以下结构组织输出文件：

```
outputs/
├── {filename}/
│   ├── images/
│   │   ├── {filename}_1.png    # 第1轮生成的图片
│   │   ├── {filename}_2.png    # 第2轮生成的图片
│   │   └── ...
│   ├── videos/
│   │   ├── {filename}_1.mp4    # 第1轮生成的视频
│   │   ├── {filename}_2.mp4    # 第2轮生成的视频
│   │   └── ...
│   └── output.jsonl            # JSONL格式输出（每行一个JSON对象，包含filename字段）
```

**JSONL格式说明：**
每行包含一个完整的JSON对象，包含以下字段：
- `filename`: 文件名前缀
- `round`: 轮次编号
- `config`: 配置名称
- `status`: 执行状态
- `output`: 输出内容
  - `text`: 文本内容
  - `has_image`: 是否包含图片（布尔值）
  - `has_video`: 是否包含视频（布尔值）

示例：
```json
{"filename": "test", "round": 1, "config": "image_generation", "status": "success", "output": {"text": "生成的图片描述文本", "has_image": true, "has_video": false}}
{"filename": "test", "round": 2, "config": "text_processing", "status": "success", "output": {"text": "处理后的文本结果", "has_image": false, "has_video": false}}
```

### 提示词变量替换

支持在 `config/config.ini` 文件的 `prompt` 中使用变量：

- `{country}`, `{age}` 等：来自 `promptVariables`
- `{text0}`, `{text1}` 等：引用历史轮次的文本输出
- `{image1}`, `{video2}` 等：引用历史轮次的媒体文件

示例：
```ini
prompt = 请为{country}的{age}岁用户生成内容。参考之前的输出：{text0}
```

## 🔧 核心组件

### 1. 流水线控制器 (PipelineController)

负责整个流水线的执行流程：
- 加载和管理配置
- 协调各个处理器
- 处理错误和异常
- 管理 LLM 实例

### 2. 记忆管理 (PipelineMemory)

管理跨轮次的数据传递：
- 存储每轮的输入输出
- 支持变量引用和替换
- 提供记忆状态查询

### 3. 输入处理器 (PipelineInputProcessor)

处理各种格式的输入：
- 文件路径到 base64 的转换
- 提示词变量替换
- 多模态数据整合

### 4. 输出处理器 (OutputProcessor)

处理流水线输出：
- **ConsoleOutputProcessor**：控制台输出
- **FileOutputProcessor**：文件保存（新的文件结构）

## 📊 日志系统

系统提供分级的彩色日志输出：

- **DEBUG**：详细调试信息
- **INFO**：关键步骤信息（绿色）
- **WARNING**：警告信息（黄色）
- **ERROR**：错误信息（红色）
- **CRITICAL**：严重错误（红底白字）

日志文件保存在 `logs/pipeline.log`，支持自动轮转（10MB，保留5个备份）。

### 日志示例

```bash
# 运行日志示例
python examples/logging_example.py
```

## ⚙️ 高级配置

### 多模型支持

系统支持多种 AI 模型提供商：

- **OpenAI**：GPT-4, GPT-3.5 等
- **Anthropic**：Claude 系列
- **Google**：Gemini 系列

### 自定义处理器

可以通过创建新的处理器类来扩展功能：

```python
from processors.output_processor import FileOutputProcessor

class CustomOutputProcessor:
    def process(self, results, **kwargs):
        # 自定义处理逻辑
        pass
```

## 🛠️ 开发指南

### 添加新的模型支持

1. 在 `config/config.ini` 中添加新的配置节
2. 在 `LangChainLLM` 中添加对应的环境变量设置
3. 更新模型名称映射逻辑

### 扩展输入处理

1. 修改 `PipelineInputProcessor` 类
2. 添加新的处理方法
3. 在主程序中使用新功能

### 自定义输出格式

1. 创建新的输出处理器类
2. 实现自定义的文件组织逻辑
3. 在主程序中使用新的处理器

## 🐛 故障排除

### 常见问题

1. **模型初始化失败**
   - 检查 API 密钥是否正确
   - 确认网络连接正常
   - 验证模型名称是否正确

2. **文件处理错误**
   - 确认文件路径存在
   - 检查文件格式是否支持
   - 验证文件权限

3. **内存不足**
   - 减少并发处理数量
   - 优化图片/视频大小
   - 增加系统内存

### 调试模式

启用详细日志：

```python
logger = setup_logging(level='DEBUG')
```

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件至：[your-email@example.com]

---

**注意**：请确保在使用前正确配置 API 密钥，并遵守相关服务提供商的使用条款。 