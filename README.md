# LangChain Pipeline System

A modular multi-round AI processing pipeline system based on LangChain, supporting multimodal input/output (text, image, video).

## Features

- 🔄 Multi-round pipeline processing
- 🎯 Multimodal support (text, image, video)
- 🧠 Intelligent memory management
- 📊 Multiple output formats
- 🎨 Colored logging system
- 🔧 Modular architecture

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure your API keys in config.ini
# Run the pipeline
python main.py
```

## Documentation

For detailed documentation in Chinese, please see [README_zh.md](README_zh.md).

## Project Structure

```
langchain/
├── config/                 # Configuration module
├── core/                   # Core modules
├── processors/             # Input/Output processors
├── utils/                  # Utility modules
├── docs/                   # Documentation
├── examples/               # Example code
├── input/                  # Input files
├── outputs/                # Output files
├── logs/                   # Log files
├── main.py                 # Main entry point
├── requirements.txt        # Dependencies
└── README_zh.md           # Chinese documentation
```

## Output Structure

```
outputs/
├── {filename}/
│   ├── images/
│   │   ├── {filename}_1.png
│   │   └── {filename}_2.png
│   ├── videos/
│   │   ├── {filename}_1.mp4
│   │   └── {filename}_2.mp4
│   └── output.json
```

## License

MIT License
