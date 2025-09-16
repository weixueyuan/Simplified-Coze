#!/usr/bin/env python3
"""
输入处理器模块
处理各种输入格式，转换为标准化的字典格式
"""

from typing import Dict, Any
import re
from utils import encode_file_to_base64, is_base64_data
from utils.log_config import get_logger

class PipelineInputProcessor:
    """流水线输入处理器 - 处理流水线中的输入数据编码和提示词拼接"""
    
    def __init__(self, memory=None):
        """
        初始化流水线输入处理器
        
        Args:
            memory: 流水线记忆对象，用于获取历史数据
        """
        self.memory = memory
        self.logger = get_logger('pipeline.input_processor')
    
    def process(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理流水线输入：编码文件、拼接提示词、处理input配置
        
        Args:
            config: 配置字典，包含prompt、input等信息
            input_data: 输入数据字典
            
        Returns:
            Dict[str, Any]: 处理后的输入字典
        """

        # 1. 处理输入数据（编码文件等）
        encode_input = self._encode_input_data(input_data)
        
        # 2. 构建最终输入（添加提示词、处理input配置）
        final_input = self._build_final_input(config, encode_input)
        
        return final_input
    
    def _encode_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理输入数据：编码文件、转换格式等
        
        Args:
            input_data: 原始输入数据，可能为None（第二轮及之后）
            
        Returns:
            Dict[str, Any]: 处理后的输入数据
        """
        # 如果input_data为None（第二轮及之后），初始化为空字典
        if input_data is None:
            input_data = {}
            
        encode_input_data = {
            "text": input_data.get("text", ""),
            "image": input_data.get("image", ""),
            "video": input_data.get("video", "")
        }
        
        # 处理图片：如果是文件路径，编码为base64
        if encode_input_data["image"] and not is_base64_data(encode_input_data["image"]):
            encoded_image = encode_file_to_base64(encode_input_data["image"])
            if encoded_image:
                encode_input_data["image"] = encoded_image
            else:
                encode_input_data["image"] = ""
        
        # 处理视频：如果是文件路径，编码为base64
        if encode_input_data["video"] and not is_base64_data(encode_input_data["video"]):
            encoded_video = encode_file_to_base64(encode_input_data["video"])
            if encoded_video:
                encode_input_data["video"] = encoded_video
            else:
                encode_input_data["video"] = ""
        
        # 统一清洗，确保为纯净的base64字符串
        from utils.file_utils import sanitize_base64
        if encode_input_data["image"]:
            cleaned = sanitize_base64(encode_input_data["image"])
            encode_input_data["image"] = cleaned or ""
        if encode_input_data["video"]:
            cleaned = sanitize_base64(encode_input_data["video"])
            encode_input_data["video"] = cleaned or ""
        
        return encode_input_data
    
    def _build_final_input(self, config: Dict[str, Any], encode_input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建最终的输入字典：仅基于 prompt 变量替换与本轮输入拼接（不再使用 input 规范）
        """
        # 获取配置中的提示词，并进行变量替换（-1轮 + 本轮promptVariables + memory索引）
        prompt = config.get('prompt', '')
        prompt = self._replace_prompt_variables(prompt, encode_input_data)
        
        # 解析并注入 {imageN}/{videoN} 到输入字典的 image/video 字段
        # 优先使用本轮 encode_input_data 中已有的 image/video，否则回退到 memory 引用
        selected_image = encode_input_data.get('image', '')
        selected_video = encode_input_data.get('video', '')
        
        # 查找所有 {imageN}/{videoN} 引用
        media_refs = re.findall(r'\{(image|video)(\d+)\}', prompt)
        if self.memory and media_refs:
            for ctype, idx_str in media_refs:
                idx = int(idx_str)
                rd = self.memory.get_round_memory(idx)
                if not rd:
                    continue
                if ctype == 'image' and not selected_image and rd.get('image'):
                    selected_image = rd['image']
                if ctype == 'video' and not selected_video and rd.get('video'):
                    selected_video = rd['video']
        
        # 从 prompt 中移除媒体占位符，避免把二进制/路径注入到文本提示
        prompt = re.sub(r'\{(image|video)\d+\}', '', prompt).strip()
        
        # 对选中的媒体做最后的清洗
        from utils.file_utils import sanitize_base64
        if selected_image:
            selected_image = sanitize_base64(selected_image) or ""
        if selected_video:
            selected_video = sanitize_base64(selected_video) or ""
        
        # 最终仅拼接本轮 text（如果有），图片/视频透传
        input_dict = {
            "text": self._concat_text(prompt, [encode_input_data.get('text', '')]),
            "image": selected_image,
            "video": selected_video
        }
        
        return input_dict
    
    def _replace_prompt_variables(self, prompt: str, input_data: Dict[str, Any]) -> str:
        """
        替换prompt中的变量，顺序：
        1) memory[-1] 中的全局变量（直接dict）
        2) 本轮输入的 promptVariables（覆盖）
        3) {text0}/{image1}/{video2} 等 memory 索引变量
        """
        if not prompt:
            return prompt
        
        # 1) 合并 -1 轮的变量
        merged_vars: Dict[str, Any] = {}
        if self.memory:
            minus1 = self.memory.get_round_memory(-1)
            if isinstance(minus1, dict):
                merged_vars.update(minus1)
        
        # 2.1) 先替换简单变量 {age}/{country}（排除 type+index）
        def _repl_simple(m):
            key = m.group(1)
            if re.match(r'^[a-zA-Z]+\d+$', key):
                return m.group(0)
            return str(merged_vars.get(key, m.group(0)))
        prompt = re.sub(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', _repl_simple, prompt)
        
        # 3) 替换 memory 索引变量
        if self.memory:
            for ctype, idx in re.findall(r'\{([a-zA-Z]+)(\d+)\}', prompt):
                if ctype == 'image' or ctype == 'video':
                    continue
                ph = f"{{{ctype}{idx}}}"
                rd = self.memory.get_round_memory(int(idx))
                if rd and ctype in rd and rd[ctype] is not None:
                    prompt = prompt.replace(ph, str(rd[ctype]))
        self.logger.debug(f"处理后的提示词: {prompt}")
        return prompt
    
    def _concat_text(self, prompt: str, parts: list) -> str:
        """用换行拼接非空片段，并与prompt自然拼接"""
        nonempty = [p for p in parts if p]
        if prompt and nonempty:
            return f"{prompt}\n\n" + "\n\n".join(nonempty)
        if prompt:
            return prompt
        return "\n\n".join(nonempty)
    

    

