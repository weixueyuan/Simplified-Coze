#!/usr/bin/env python3
"""
流水线记忆模块
管理多轮对话的状态和输出
"""

from typing import Dict, Any, List, Optional

from utils.log_config import get_logger

class PipelineMemory:
    """流水线记忆管理"""
    
    def __init__(self):
        # memory结构: {index: {"text": "...", "image": "...", "video": "..."}}
        # index: 0=初始输入, 1=第一轮输出, 2=第二轮输出...
        self.memory = {}
        self.current_round = 0
        self.logger = get_logger('pipeline.memory')
    
    def store_round_memory(self, output: Dict[str, Any], round_index: Optional[int] = None):
        """存储一轮的内存数据"""
        if round_index is None:
            round_index = self.current_round
        
        # 直接存储字典格式的输出
        self.memory[round_index] = output
        
        # 更新当前轮次
        if round_index >= self.current_round:
            self.current_round = round_index + 1
        
        if round_index == -1:
            self.logger.info(f"💾 存储全局变量: {list(output.keys())}")
        elif round_index == 0:
            self.logger.info(f"💾 存储初始输入: {list(output.keys())}")
        else:
            self.logger.info(f"💾 存储第{round_index-1}轮输出: {list(output.keys())}")
    
    def get_round_memory(self, round_index: int) -> Dict[str, Any]:
        """获取指定轮次的内存数据"""
        return self.memory.get(round_index, {})
    
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
        self.logger.info("记忆状态:")
        self.logger.info(self.get_memory_summary())
        self.logger.info(f"当前轮次: {self.current_round}")
    
    def clear_memory(self):
        """清空记忆"""
        self.memory.clear()
        self.current_round = 0
        self.logger.info("记忆已清空")
    
 