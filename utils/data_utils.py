#!/usr/bin/env python3
"""
数据工具模块
提供数据验证、转换等通用功能
"""

from typing import Dict, Any


def create_error_data(error_message: str) -> Dict[str, Any]:
    """
    创建错误数据结构
    
    Args:
        error_message: 错误信息
        
    Returns:
        Dict[str, Any]: 错误数据
    """
    return {
        "text": f"执行失败: {error_message}",
        "image": "",
        "video": ""
    } 