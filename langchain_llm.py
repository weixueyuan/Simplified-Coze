#!/usr/bin/env python3
"""
LangChain LLM模块
根据配置信息初始化LLM并处理输入输出
"""

import os
import base64
from typing import Optional, Dict, Any, List
from langchain.chat_models import init_chat_model
from config_reader import ConfigReader

class LangChainLLM:
    """LangChain LLM类，根据配置初始化模型并处理请求"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_reader = ConfigReader(config_file)
        self.model = None
        self.config = None
        self.provider = None
    
    def init_model(self):
        """初始化模型"""
        try:
            # 获取配置
            config = self.config_reader.get_pipeline_configs()[0]  # 使用第一个配置
            
            # 设置环境变量
            self._setup_environment(config)
            
            # 构建完整的模型名称
            model_name = config["model"]
            full_model_name = self._get_full_model_name(model_name, config.get("section_name", "openai"))
            
            print(f"🔧 初始化模型: {full_model_name}")
            
            # 初始化模型
            model = init_chat_model(full_model_name)
            
            # 保存到实例变量
            self.model = model
            self.config = config
            self.provider = config.get("section_name", "openai")
            
            return model
        except Exception as e:
            raise Exception(f"模型初始化失败: {e}")
    
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
    
    def get_model(self):
        """获取模型实例"""
        if self.model is None:
            self.init_model()
        
        return self.model
    
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
                    result["text"] = text_content
                
                # 只添加第一张图片（默认只返回一张）
                if image_matches:
                    image_type, base64_data = image_matches[0]
                    result["image"] = f"data:image/{image_type};base64,{base64_data}"
            else:
                # 纯文本
                result["text"] = content
            
            return result
                
        except Exception as e:
            # 记录错误日志
            print(f"❌ 响应处理失败: {e}")
            # 返回空结果而不是错误信息
            return {"text": "", "image": "", "video": ""}
            
    def _process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理多模态输入（文本+图片/视频）"""
        try:
            model = self.get_model()
            content = []
            
            # 处理文本输入
            if 'text' in input_data:
                text_content = input_data['text']
                content.append({
                    "type": "text",
                    "text": text_content
                })
            
            # 处理图片输入
            if 'image' in input_data:
                content.append({
                    "type": "image",
                    "source_type": "base64",
                    "data": input_data['image'],
                    "mime_type": "image/jpeg"
                })
            
            # 处理视频输入
            if 'video' in input_data:
                content.append({
                    "type": "video",
                    "source_type": "base64",
                    "data": input_data['video'],
                    "mime_type": "video/mp4"
                })
            
            # 构建消息
            message = {"role": "user", "content": content}
            response = model.invoke([message])
            return self._process_response(response)
            
        except Exception as e:
            # 记录错误日志
            print(f"❌ 多模态处理失败: {e}")
            # 返回空结果而不是错误信息
            return {"text": "", "image": "", "video": ""}
    
    def save_images_from_response(self, response_data: List[Dict[str, Any]], output_dir: str = "saved_images") -> Dict[str, Any]:
        """从响应中保存图片"""
        import os
        import base64
        from pathlib import Path
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        result = {
            "saved_images": [],
            "errors": []
        }
        
        # 遍历响应列表
        for item in response_data:
            if item["type"] == "image":
                try:
                    # 获取图片数据
                    base64_data = item.get("base64_data")
                    image_type = item.get("image_type", "png")
                    
                    if base64_data:
                        # 解码base64数据
                        image_data = base64.b64decode(base64_data)
                        
                        # 生成文件名
                        if image_type.lower() == 'jpeg':
                            image_type = 'jpg'
                        filename = f"generated_image_{item.get('index', 1)}.{image_type}"
                        file_path = output_path / filename
                        
                        # 保存图片
                        with open(file_path, 'wb') as f:
                            f.write(image_data)
                        
                        result["saved_images"].append({
                            "filename": filename,
                            "file_path": str(file_path),
                            "size_bytes": len(image_data),
                            "type": image_type
                        })
                        
                        print(f"✅ 图片已保存: {file_path}")
                    else:
                        result["errors"].append(f"图片缺少base64数据")
                        
                except Exception as e:
                    error_msg = f"保存图片失败: {e}"
                    result["errors"].append(error_msg)
                    print(f"❌ {error_msg}")
        
        return result
    
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

    def _encode_file(self, file_path: str) -> str:
        """编码文件为base64"""
        try:
            with open(file_path, 'rb') as f:
                import base64
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ 文件编码失败: {e}")
            return ""
    
    def _get_mime_type(self, file_path: str) -> str:
        """获取文件的MIME类型"""
        ext = file_path.lower().split('.')[-1]
        mime_types = {
            'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
            'gif': 'image/gif', 'bmp': 'image/bmp', 'webp': 'image/webp',
            'mp4': 'video/mp4', 'avi': 'video/x-msvideo', 'mov': 'video/quicktime',
            'wmv': 'video/x-ms-wmv', 'flv': 'video/x-flv', 'webm': 'video/webm',
            'wav': 'audio/wav', 'mp3': 'audio/mpeg', 'aac': 'audio/aac',
            'flac': 'audio/flac', 'ogg': 'audio/ogg', 'm4a': 'audio/mp4'
        }
        return mime_types.get(ext, 'application/octet-stream') 