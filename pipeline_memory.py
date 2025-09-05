#!/usr/bin/env python3
"""
流水线记忆模块
管理多轮对话的状态和输出
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class PipelineMemory:
    """流水线记忆管理"""
    
    def __init__(self):
        # memory结构: {index: {"text": "...", "image": "...", "video": "..."}}
        # index: 0=初始输入, 1=第一轮输出, 2=第二轮输出...
        self.memory = {}
        self.current_round = 0
    
    def store_round_output(self, output: Dict[str, Any], round_index: Optional[int] = None):
        """存储一轮的输出"""
        if round_index is None:
            round_index = self.current_round
        
        # 直接存储字典格式的输出
        self.memory[round_index] = output
        
        # 更新当前轮次
        if round_index >= self.current_round:
            self.current_round = round_index + 1
        
        print(f"💾 存储第{round_index}轮输出: {list(output.keys())}")
    
    def get_round_output(self, round_index: int) -> Dict[str, Any]:
        """获取指定轮次的输出"""
        return self.memory.get(round_index, {})
    
    def get_last_output(self) -> Dict[str, Any]:
        """获取上一轮输出"""
        if self.current_round > 0:
            return self.memory.get(self.current_round - 1, {})
        return {}
    
    def build_input_with_prompt(self, config: Dict[str, Any], initial_input: Dict[str, Any]) -> str:
        """根据配置构建输入（prompt + 数据）"""
        prompt = config.get('prompt', '')
        input_spec = config.get('input', '')
        
        if not input_spec:
            # 没有input参数，使用上一轮输出
            last_output = self.get_last_output()
            if last_output:
                # 组合上一轮的所有输出
                parts = []
                if 'text' in last_output:
                    parts.append(f"文本: {last_output['text']}")
                if 'image' in last_output:
                    parts.append(f"图片: [图片数据]")
                if 'video' in last_output:
                    parts.append(f"视频: [视频数据]")
                
                data_content = "\n".join(parts)
                return f"{prompt}\n\n输入数据:\n{data_content}"
            else:
                # 没有上一轮输出，使用初始输入（字典格式）
                input_parts = []
                if 'text' in initial_input:
                    input_parts.append(f"文本: {initial_input['text']}")
                if 'image' in initial_input:
                    # 对图片进行base64编码
                    image_data = self._encode_file(initial_input['image'])
                    if image_data:
                        input_parts.append(f"图片: [图片数据已编码]")
                    else:
                        input_parts.append(f"图片: 文件不存在或编码失败")
                if 'video' in initial_input:
                    # 对视频进行base64编码
                    video_data = self._encode_file(initial_input['video'])
                    if video_data:
                        input_parts.append(f"视频: [视频数据已编码]")
                    else:
                        input_parts.append(f"视频: 文件不存在或编码失败")
                
                if input_parts:
                    input_content = "\n".join(input_parts)
                    return f"{prompt}\n\n{input_content}"
                else:
                    return prompt
        else:
            # 有input参数，从memory取对应数据
            input_parts = [input_spec.strip()]
            data_parts = []
            
            # 解析input参数（如 "image1, text1"）
            for item in input_parts[0].split(','):
                item = item.strip()
                if not item:
                    continue
                
                # 解析格式：type + index（如 image1, text2）
                if len(item) >= 2:
                    content_type = item[:-1]  # image, text, video
                    try:
                        index = int(item[-1])  # 1, 2, 3...
                        
                        # 从memory获取对应数据
                        round_data = self.memory.get(index, {})
                        if content_type in round_data:
                            if content_type == 'text':
                                data_parts.append(f"{content_type}: {round_data[content_type]}")
                            else:
                                data_parts.append(f"{content_type}: [{content_type}数据]")
                    except ValueError:
                        # 如果不是数字索引，当作普通文本
                        data_parts.append(item)
                else:
                    data_parts.append(item)
            
            if data_parts:
                data_content = "\n".join(data_parts)
                return f"{prompt}\n\n输入数据:\n{data_content}"
            else:
                return prompt
    
    def _encode_file(self, file_path: str) -> str:
        """编码文件为base64"""
        try:
            import base64
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ 文件编码失败 {file_path}: {e}")
            return ""
    
    def get_memory_summary(self) -> str:
        """获取记忆摘要"""
        if not self.memory:
            return "记忆为空"
        
        summary = []
        for index in sorted(self.memory.keys()):
            round_data = self.memory[index]
            round_desc = f"第{index}轮: {list(round_data.keys())}"
            summary.append(round_desc)
        
        return "\n".join(summary)
    
    def print_memory_status(self):
        """打印记忆状态"""
        print("\n🧠 记忆状态:")
        print(self.get_memory_summary())
        print(f"当前轮次: {self.current_round}")
    
    def clear_memory(self):
        """清空记忆"""
        self.memory.clear()
        self.current_round = 0
        print("🧹 记忆已清空")
    
    def save_memory_log(self, output_dir: str):
        """保存记忆日志"""
        output_path = Path(output_dir) / "memory_log.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
        
        print(f"💾 记忆日志已保存: {output_path}") 