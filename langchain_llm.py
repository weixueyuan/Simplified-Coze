#!/usr/bin/env python3
"""
LangChain LLM模块
根据配置信息初始化LLM并处理输入输出
"""

import os
import base64
from typing import Optional, Dict, Any
from langchain.chat_models import init_chat_model
from config_reader import ConfigReader

class LangChainLLM:
    """LangChain LLM类，根据配置初始化模型并处理请求"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_reader = ConfigReader(config_file)
        self.model = None
        self.config = None
        self.provider = None
    
    def _setup_environment(self, config: Dict[str, Any], provider: str):
        """设置环境变量"""
        if provider == "anthropic" or provider == "claude":
            os.environ["ANTHROPIC_API_KEY"] = config["api_key"]
            os.environ["ANTHROPIC_BASE_URL"] = config["base_url"]
        elif provider == "openai":
            os.environ["OPENAI_API_KEY"] = config["api_key"]
            os.environ["OPENAI_BASE_URL"] = config["base_url"]
        elif provider == "google":
            os.environ["GOOGLE_API_KEY"] = config["api_key"]
            os.environ["GOOGLE_BASE_URL"] = config["base_url"]
        elif provider == "dashscope":
            os.environ["DASHSCOPE_API_KEY"] = config["api_key"]
            os.environ["DASHSCOPE_BASE_URL"] = config["base_url"]
        elif provider == "zhipu":
            os.environ["ZHIPU_API_KEY"] = config["api_key"]
            os.environ["ZHIPU_BASE_URL"] = config["base_url"]
        else:
            # 默认使用OpenAI兼容格式
            os.environ["OPENAI_API_KEY"] = config["api_key"]
            os.environ["OPENAI_BASE_URL"] = config["base_url"]
    
    def _get_full_model_name(self, model_name: str, provider: str) -> str:
        """获取完整的模型名称"""
        if provider == "openai":
            return f"openai:{model_name}"
        elif provider == "anthropic" or provider == "claude":
            return f"anthropic:{model_name}"
        elif provider == "google":
            return f"google_genai:{model_name}"
        elif provider == "dashscope":
            return f"dashscope:{model_name}"
        elif provider == "zhipu":
            return f"zhipu:{model_name}"
        else:
            # 默认使用OpenAI格式
            return f"openai:{model_name}"
    
    def init_model(self):
        """初始化模型"""
        try:
            # 获取配置
            config = self.config_reader.get_llm_config()
            
            # 根据配置节名称获取提供商
            section = config["section"]
            provider = self.config_reader.get_model_provider(section)
            
            # 设置环境变量
            self._setup_environment(config, provider)
            
            # 构建完整的模型名称
            model_name = config["model"]
            full_model_name = self._get_full_model_name(model_name, provider)
            print(full_model_name)
            print(config)
            print(provider)
            
            # 初始化模型
            model = init_chat_model(full_model_name)
            
            # 保存到实例变量
            self.model = model
            self.config = config
            self.provider = provider
            
            return model
        except Exception as e:
            raise Exception(f"模型初始化失败: {e}")
    
    def get_model(self):
        """获取模型实例"""
        if self.model is None:
            self.init_model()
        
        return self.model
    
    def _process_response(self, response) -> Dict[str, Any]:
        """处理响应，直接返回包含多个JSON对象的列表"""
        try:
            # 获取文本内容
            content = response.text()
            
            # 检查是否包含图片
            import re
            
            # 使用更简单的正则表达式直接匹配base64图片数据
            if 'data:image' in content:
                # 包含图片，返回列表
                result = []
                
                # 查找所有base64图片数据的位置
                pattern = r'data:image/([^;]+);base64,([^"]+)'
                image_matches = re.findall(pattern, content)
                
                # 找到第一个图片标记的位置
                first_image_pos = content.find('data:image')
                
                # 提取图片标记之前的纯文本内容
                if first_image_pos > 0:
                    text_content = content[:first_image_pos].strip()
                    # 清理文本末尾的换行符和图片标记开头
                    text_content = re.sub(r'\n*!\[image\]\(?$', '', text_content).strip()
                    
                    if text_content:
                        result.append({"type": "text", "text": text_content})
                
                # 添加图片
                for i, (image_type, base64_data) in enumerate(image_matches):
                    result.append({
                        "type": "image", 
                        "image_type": image_type,
                        "base64_data": base64_data,
                        "index": i + 1
                    })
                
                return result
            else:
                # 纯文本，返回列表
                return [{"type": "text", "text": content}]
                
        except Exception as e:
            # 如果解析失败，返回文本
            return [{"type": "text", "text": response.text()}]
            
    def process_text(self, text: str) -> Dict[str, Any]:
        """处理文本输入"""
        try:
            model = self.get_model()
            
            message = {
                "role": "user",
                "content": [{"type": "text", "text": text}]
            }
            
            response = model.invoke([message])
            return self._process_response(response)
        except Exception as e:
            return {"type": "error", "error": f"文本处理错误: {e}"}

    def process_image(self, image_path: str, text: str) -> Dict[str, Any]:
        """处理图片输入"""
        try:
            # 读取图片文件
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            
            model = self.get_model()
            
            message = {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {
                        "type": "image",
                        "source_type": "base64",
                        "data": image_data,
                        "mime_type": "image/jpeg"
                    }
                ]
            }
            
            response = model.invoke([message])
            print(response)
            print(response.content)
            return self._process_response(response)
        except Exception as e:
            return {"type": "error", "error": f"图片处理错误: {e}"}

    def process_video(self, video_path: str, text: str) -> Dict[str, Any]:
        """处理视频输入"""
        try:
            # 读取视频文件
            with open(video_path, "rb") as f:
                video_data = base64.b64encode(f.read()).decode("utf-8")
            
            model = self.get_model()
            
            message = {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {
                        "type": "video",
                        "source_type": "base64",
                        "data": video_data,
                        "mime_type": "video/mp4"
                    }
                ]
            }
            
            response = model.invoke([message])
            return self._process_response(response)
        except Exception as e:
            return {"type": "error", "error": f"视频处理错误: {e}"}

    def process_audio(self, audio_path: str, text: str) -> Dict[str, Any]:
        """处理音频输入"""
        try:
            # 读取音频文件
            with open(audio_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode("utf-8")
            
            model = self.get_model()
            
            message = {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {
                        "type": "audio",
                        "source_type": "base64",
                        "data": audio_data,
                        "mime_type": "audio/wav"
                    }
                ]
            }
            
            response = model.invoke([message])
            return self._process_response(response)
        except Exception as e:
            return {"type": "error", "error": f"音频处理错误: {e}"}
    
    def smart_process(self, text: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        智能处理：根据输入自动选择处理方式
        """
        if file_path:
            # 根据文件扩展名判断类型
            ext = file_path.lower().split('.')[-1]
            
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                return self.process_image(file_path, text)
            elif ext in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm']:
                return self.process_video(file_path, text)
            elif ext in ['wav', 'mp3', 'aac', 'flac', 'ogg', 'm4a']:
                return self.process_audio(file_path, text)
            else:
                return {"type": "error", "error": f"不支持的文件类型: {ext}"}
        else:
            return self.process_text(text)
    
    def get_model_config(self) -> Dict[str, Any]:
        """获取模型配置"""
        if self.config is None:
            self.init_model()
        return self.config
    
    def get_model_provider(self) -> str:
        """获取模型提供商"""
        if self.provider is None:
            self.init_model()
        return self.provider
    
    def get_available_models(self) -> list:
        """获取可用的模型列表"""
        return self.config_reader.get_available_models() 