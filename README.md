# Simplified-Coze

A simplified AI workflow orchestration system that supports multi-round conversation pipeline building, with the ability to use variables and reference outputs from previous rounds in prompts.

## ✨ Core Features

- 🔧 **Pipeline Building**: Define multi-round AI processing workflows through configuration files
- 🔄 **Round Output Reference**: Reference outputs from previous rounds in prompts
- 📝 **Variable System**: Use custom variables in prompts
- 🎯 **Multimodal Support**: Support for text, image, and video input/output
- 📊 **Structured Output**: Automatically save each round's results in JSONL format
- 🎨 **Multi-Model Support**: Compatible with OpenAI, Claude, Gemini, and other mainstream models

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/weixueyuan/Simplified-Coze.git
cd Simplified-Coze
pip install -r requirements.txt

# Configure workflow
cp config/config_example.ini config/config.ini
# Edit config.ini with your API keys

# Run workflow
python main.py
```

## 🔧 Workflow Configuration

### Basic Format

```ini
[step1_generation]
model = gpt-4o
base_url = https://api.openai.com/v1/
api_key = YOUR_API_KEY
prompt = Generate content about {topic}

[step2_analysis]
model = claude-3-5-sonnet-latest
base_url = https://api.anthropic.com/
api_key = YOUR_API_KEY
prompt = Analyze this content: {text1}. Focus on {analysis_type}.
```

### Variable System

**Custom Variables:**
```python
workflow_input = {
    "filename": "my_workflow",
    "promptVariables": {
        "topic": "AI technology",
        "analysis_type": "technical aspects"
    }
}
```

**Round References:**
- `{text1}` - Text output from round 1
- `{image1}` - Image output from round 1
- `{video2}` - Video output from round 2

## 📋 Complete Example

**Scenario: Image Generation → Style Transfer → Analysis**

```ini
[generate_image]
model = dall-e-3
api_key = YOUR_OPENAI_KEY
prompt = Create a {style} style image of {subject}

[transfer_style]
model = midjourney
api_key = YOUR_MIDJOURNEY_KEY  
prompt = Convert this image {image1} to {target_style} style

[analyze_result]
model = gpt-4-vision-preview
api_key = YOUR_OPENAI_KEY
prompt = Compare these images: Original: {image1}, Converted: {image2}
```

## 📁 Output Structure

```
outputs/
├── workflow_name/
│   ├── images/
│   │   ├── workflow_name_1.png
│   │   └── workflow_name_2.png
│   ├── videos/
│   │   └── workflow_name_1.mp4
│   └── output.jsonl
```

## 🎯 Use Cases

- **Content Creation Pipeline**: Text → Image → Video → Review
- **Data Analysis Workflow**: Collection → Cleaning → Analysis → Report
- **Multimodal Processing**: Image Input → Recognition → Style Transfer → Quality Assessment

## 🔧 Supported Models

- **OpenAI**: GPT-4, GPT-3.5, DALL-E
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Haiku  
- **Google**: Gemini Pro, Gemini Vision
- **Others**: OpenAI-compatible APIs

## 🔒 Security

- ✅ Config files in `.gitignore` - API keys won't be committed
- ✅ Environment variable support for sensitive info
- ✅ Auto-sanitized logs without base64 data

## 📄 License

MIT License

---

**Simplified-Coze** - Making AI workflow building simple and efficient 🚀
