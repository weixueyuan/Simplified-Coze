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