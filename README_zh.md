# Simplified-Coze

一个简化版的 AI 工作流编排系统，支持多轮对话流水线搭建，可以在提示词中使用变量和引用前几轮的输出结果。

## ✨ 核心特性

- 🔧 **可视化流水线搭建**：通过配置文件定义多轮 AI 处理流程
- 🔄 **轮次输出引用**：支持在提示词中引用前几轮的输出内容
- 📝 **变量替换系统**：支持在提示词中使用自定义变量
- 🎯 **多模态处理**：支持文本、图片、视频的输入和输出
- 📊 **结构化输出**：自动保存每轮结果为 JSONL 格式
- 🎨 **多模型支持**：兼容 OpenAI、Claude、Gemini 等主流模型

## 🚀 快速开始

### 1. 安装依赖

```bash
git clone https://github.com/weixueyuan/Simplified-Coze.git
cd Simplified-Coze
pip install -r requirements.txt
```

### 2. 配置工作流

```bash
# 复制示例配置
cp config/config_example.ini config/config.ini

# 编辑配置文件，填入你的 API 密钥
vim config/config.ini
```

### 3. 运行工作流

```bash
python main.py
```

## 🔧 工作流配置示例

### 基础配置格式

```ini
[step1_image_generation]
model = gpt-4o
base_url = https://api.openai.com/v1/
api_key = YOUR_API_KEY
prompt = 请生成一张关于{topic}的图片

[step2_image_analysis]
model = claude-3-5-sonnet-latest
base_url = https://api.anthropic.com/
api_key = YOUR_API_KEY
prompt = 请分析这张图片的内容：{image1}。分析结果要包含{analysis_type}方面的信息。

[step3_summary]
model = gpt-4o
base_url = https://api.openai.com/v1/
api_key = YOUR_API_KEY
prompt = 基于前面的结果进行总结：\n图片生成结果：{text1}\n图片分析结果：{text2}
```

### 变量和引用系统

#### 1. 自定义变量
在输入数据中定义变量：
```python
raw_input = {
    "text": "初始输入文本",
    "filename": "my_workflow",
    "promptVariables": {
        "topic": "未来城市",
        "analysis_type": "建筑风格"
    }
}
```

在提示词中使用：`{topic}`, `{analysis_type}`

#### 2. 轮次输出引用
- `{text1}` - 引用第1轮的文本输出
- `{text2}` - 引用第2轮的文本输出
- `{image1}` - 引用第1轮的图片输出
- `{video2}` - 引用第2轮的视频输出

## 📋 完整工作流示例

### 场景：图片生成 → 风格转换 → 内容分析

```ini
# 第一步：生成原始图片
[generate_base_image]
model = dall-e-3
base_url = https://api.openai.com/v1/
api_key = YOUR_OPENAI_KEY
prompt = 生成一张{style}风格的{subject}图片，要求：{requirements}

# 第二步：对图片进行风格转换
[style_transfer]
model = midjourney
base_url = YOUR_MIDJOURNEY_API
api_key = YOUR_MIDJOURNEY_KEY
prompt = 将这张图片{image1}转换为{target_style}风格，保持主体不变

# 第三步：分析最终结果
[final_analysis]
model = gpt-4-vision-preview
base_url = https://api.openai.com/v1/
api_key = YOUR_OPENAI_KEY
prompt = 请对比分析两张图片的差异：\n原图：{image1}\n转换后：{image2}\n分析重点：{analysis_focus}
```

对应的输入数据：
```python
workflow_input = {
    "text": "开始图片生成工作流",
    "filename": "image_workflow",
    "promptVariables": {
        "style": "赛博朋克",
        "subject": "未来城市街景",
        "requirements": "包含霓虹灯光和飞行汽车",
        "target_style": "水彩画",
        "analysis_focus": "色彩变化和艺术效果"
    }
}
```

## 📁 输出结构

系统支持两种输出组织方式：

### 模式1：合并保存（默认）
```
outputs/
├── image_workflow/
│   ├── images/
│   │   ├── image_workflow_1.png    # 第1轮生成的图片
│   │   ├── image_workflow_2.png    # 第2轮转换的图片
│   │   └── ...
│   ├── videos/
│   │   └── image_workflow_1.mp4    # 如果有视频输出
│   └── output.jsonl                # 结构化日志
```

### 模式2：按轮次分组
```
outputs/
├── round1/
│   ├── images/
│   │   └── {filename}.png          # 第1轮生成的图片
│   ├── videos/
│   │   └── {filename}.mp4          # 第1轮生成的视频（如果有）
│   └── output.json                 # 第1轮的详细输出
├── round2/
│   ├── images/
│   │   └── {filename}.png          # 第2轮生成的图片
│   └── output.json                 # 第2轮的详细输出
├── round3/
│   └── output.json                 # 第3轮的详细输出（纯文本）
└── summary.jsonl                   # 所有轮次的汇总
```

### 使用方法
```python
# 默认合并模式
output_processor.process(results, filename="my_workflow", save_mode="combined")

# 按轮次分组模式  
output_processor.process(results, filename="my_workflow", save_mode="rounds")
```

**JSONL格式示例：**
```json
{"filename": "image_workflow", "round": 1, "config": "generate_base_image", "status": "success", "output": {"text": "已生成赛博朋克风格的未来城市图片", "has_image": true, "has_video": false}}
{"filename": "image_workflow", "round": 2, "config": "style_transfer", "status": "success", "output": {"text": "已将图片转换为水彩画风格", "has_image": true, "has_video": false}}
{"filename": "image_workflow", "round": 3, "config": "final_analysis", "status": "success", "output": {"text": "两张图片的对比分析结果...", "has_image": false, "has_video": false}}
```

## 🎯 使用场景

### 1. 内容创作流水线
```
文本生成 → 图片生成 → 视频制作 → 内容审核
```

### 2. 数据分析工作流
```
数据收集 → 数据清洗 → 分析建模 → 报告生成
```

### 3. 多模态处理链
```
图片输入 → 内容识别 → 风格转换 → 质量评估
```

## 🔧 支持的模型

- **OpenAI**: GPT-4, GPT-3.5, DALL-E
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Haiku
- **Google**: Gemini Pro, Gemini Vision
- **其他**: 支持 OpenAI 兼容的 API

## 📚 项目结构

```
Simplified-Coze/
├── config/                 # 配置文件
│   ├── config_example.ini # 配置示例
│   └── config.ini         # 实际配置（不会被git追踪）
├── core/                   # 核心引擎
├── processors/            # 输入输出处理器
├── utils/                 # 工具函数
├── examples/              # 使用示例
└── main.py               # 程序入口
```

## ⚙️ 高级功能

### 条件执行
```ini
# 可以在提示词中加入条件逻辑
prompt = 如果{image1}包含人物，则进行人脸识别；否则进行物体检测
```

### 循环处理
```ini
# 通过配置多个相似步骤实现循环
[refine_step_1]
prompt = 优化这个结果：{text1}

[refine_step_2]  
prompt = 进一步优化：{text2}
```

### 并行分支
```ini
# 不同的分析分支可以并行处理同一个输入
[analysis_branch_a]
prompt = 从技术角度分析：{image1}

[analysis_branch_b]
prompt = 从艺术角度分析：{image1}
```

## 🔒 安全说明

- ✅ 配置文件已加入 `.gitignore`，API 密钥不会被意外提交
- ✅ 支持环境变量方式配置敏感信息
- ✅ 输出日志中自动脱敏，不包含 base64 等敏感数据

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**Simplified-Coze** - 让 AI 工作流搭建变得简单高效 🚀 