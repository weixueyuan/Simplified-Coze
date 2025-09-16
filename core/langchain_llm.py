#!/usr/bin/env python3
"""
LangChain LLM模块
根据配置信息初始化LLM并处理输入输出
"""

import os
from typing import Dict, Any
from langchain.chat_models import init_chat_model
from utils.log_config import get_logger

class LangChainLLM:
    """LangChain LLM类，根据配置初始化模型并处理请求"""
    
    def __init__(self, config_file: str = "config/config.ini"):
        self.model = None
        self.config = None
        self.logger = get_logger('core.langchain_llm')
        self.provider = None
    
    def _setup_environment(self, config: Dict[str, Any]):
        """设置环境变量"""
        # 根据配置节名称设置不同的环境变量
        section_name = config.get("section_name", "").lower()
        
        if "claude" in section_name:
            os.environ["ANTHROPIC_API_KEY"] = config["api_key"]
            os.environ["ANTHROPIC_BASE_URL"] = config["base_url"]
        elif "gemini" in section_name:
            os.environ["GOOGLE_API_KEY"] = config["api_key"]
            os.environ["GOOGLE_BASE_URL"] = config["base_url"]
        else:
            # 默认使用OpenAI兼容格式
            os.environ["OPENAI_API_KEY"] = config["api_key"]
            os.environ["OPENAI_BASE_URL"] = config["base_url"]
    
    def _get_full_model_name(self, model_name: str, provider: str) -> str:
        """获取完整的模型名称"""
        if provider == "openai" or "openai" in provider:
            return f"openai:{model_name}"
        elif provider == "anthropic" or provider == "claude":
            return f"anthropic:{model_name}"
        elif provider == "google" or "gemini" in provider:
            return f"google_genai:{model_name}"
        else:
            # 默认使用OpenAI格式
            return f"openai:{model_name}"
    
    def smart_process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能处理输入数据，支持多模态输入（文本+图片/视频）
        
        Args:
            input_data: 输入数据字典，包含text、image、video键
            
        Returns:
            Dict[str, Any]: 处理结果，包含text、image、video键
        """
        return self._process_input(input_data)
    
    def _process_response(self, response) -> Dict[str, Any]:
        """处理响应，返回包含text、image、video键的字典"""
        try:
            # 获取文本内容
            content = response.text()
            
            # 初始化结果字典
            result = {
                "text": "",
                "image": "",
                "video": ""
            }
            
            # 检查是否包含图片
            import re
            
            # 使用正则表达式匹配base64图片数据
            if 'data:image' in content:
                # 包含图片
                # 查找所有base64图片数据的位置，支持跨行匹配
                pattern = r'data:image/([^;]+);base64,([A-Za-z0-9+/=\s]+)'
                image_matches = re.findall(pattern, content, re.DOTALL)
                
                # 找到第一个图片标记的位置
                first_image_pos = content.find('data:image')
                
                # 提取图片标记之前的纯文本内容
                if first_image_pos > 0:
                    text_content = content[:first_image_pos].strip()
                    # 清理文本末尾的换行符和图片标记开头
                    text_content = re.sub(r'\n*!\[image\]\(?$', '', text_content).strip()
                    result["text"] = text_content
                
                # 只添加第一张图片（默认只返回一张）
                if image_matches:
                    image_type, base64_data = image_matches[0]
                    # 清理 base64 数据中的空白字符
                    clean_base64 = "".join(base64_data.split())
                    result["image"] = f"data:image/{image_type};base64,{clean_base64}"
            else:
                # 纯文本
                result["text"] = content
            
            return result
                
        except Exception as e:
            self.logger.error(f"响应处理失败: {e}")
            return {"text": "", "image": "", "video": ""}
            
    def _process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理多模态输入（文本+图片/视频）"""
        try:
            # 确保模型已初始化
            if not self.model:
                raise Exception("模型未初始化")
                
            content = []
            
            # 处理文本输入
            if input_data.get('text'):
                content.append({
                    "type": "text",
                    "text": input_data.get('text')
                })
            
            # 处理图片输入
            img = input_data.get("image")
            if img:
                from utils.file_utils import sanitize_base64
                img = sanitize_base64(img) or ""
                if img and not str(img).startswith("data:image"):
                    img = f"data:image/jpeg;base64,{img}"
                content.append({"type":"image_url","image_url":{"url": img}})
            
            # 处理视频输入
            if input_data.get('video'):
                data_video = input_data['video']
                from utils.file_utils import sanitize_base64
                data_video = sanitize_base64(data_video) or ""
                if data_video and self.provider and "gemini" in str(self.provider).lower():
                    if not str(data_video).startswith("data:video"):
                        data_url = f"data:video/mp4;base64,{data_video}"
                    else:
                        data_url = data_video
                    content.append({
                        "type": "video_url", 
                        "video_url": {"url": data_url}
                    })
            
            # 构建消息
            message = {"role": "user", "content": content}
            response = self.model.invoke([message])
            return self._process_response(response)
            
        except Exception as e:
            # 记录错误日志
            self.logger.error(f"多模态处理失败: {e}")
            # 返回空结果而不是错误信息
            return {"text": "", "image": "", "video": ""}
    
    def init_model_with_config(self, config: Dict[str, Any]):
        """使用指定配置初始化模型"""
        try:
            # 设置环境变量
            self._setup_environment(config)
            
            # 构建完整的模型名称
            model_name = config["model"]
            full_model_name = self._get_full_model_name(model_name, config.get("section_name", "openai"))
            
            self.logger.info(f"🔧 初始化模型: {full_model_name}")
            
            # 初始化模型
            model = init_chat_model(full_model_name)
            
            # 保存到实例变量
            self.model = model
            self.config = config
            self.provider = config.get("section_name", "openai")
            
            return model
        except Exception as e:
            raise Exception(f"模型初始化失败: {e}")
