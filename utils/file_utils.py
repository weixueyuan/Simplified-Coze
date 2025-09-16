#!/usr/bin/env python3
"""
文件处理工具模块
提供统一的文件操作，特别是base64编码相关功能
"""

import os
import base64
import json
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from .log_config import get_logger

logger = get_logger('utils.file')


def encode_file_to_base64(file_path: str) -> Optional[str]:
    """
    将文件编码为base64字符串，或处理已有的base64数据
    
    Args:
        file_path: 文件路径、data URL或base64字符串
        
    Returns:
        str: base64编码的字符串，失败返回None
    """
    if not file_path:
        return None
        
    # 如果已经是data URL，提取base64部分返回
    if file_path.startswith("data:"):
        if ";base64," in file_path:
            return file_path.split(",", 1)[1]  # 返回纯base64部分
        else:
            return file_path  # 非base64的data URL，原样返回
    
    # 检查是否已经是base64字符串
    try:
        base64.b64decode(file_path, validate=True)
        # 如果解码成功，说明已经是base64，直接返回
        return file_path
    except:
        # 不是base64，继续按文件路径处理
        pass
        
    # 按文件路径处理
    if not os.path.exists(file_path):
        logger.warning(f"文件不存在: {file_path}")
        return None
    
    try:
        with open(file_path, "rb") as f:
            file_data = base64.b64encode(f.read()).decode("utf-8")
        logger.info(f"文件编码成功: {file_path}")
        return file_data
    except Exception as e:
        logger.error(f"文件编码失败: {e}")
        return None


def decode_base64_to_file(base64_data: str, output_path: str) -> bool:
    """
    将base64数据解码并保存为文件
    
    Args:
        base64_data: base64编码的数据
        output_path: 输出文件路径
        
    Returns:
        bool: 成功返回True，失败返回False
    """
    try:
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 如果是data URL格式，提取base64部分
        if base64_data.startswith("data:"):
            base64_data = base64_data.split(",", 1)[1]
        
        # 解码并保存
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(base64_data))
            
        logger.info(f"文件保存成功: {output_path}")
        return True
    except Exception as e:
        logger.error(f"文件保存失败: {e}")
        return False


def save_json(data: Any, output_path: str, format: str = "jsonl") -> bool:
    """
    保存数据为JSON格式文件
    
    Args:
        data: 要保存的数据
        output_path: 输出文件路径
        format: 格式类型 ("json" 或 "jsonl")
        
    Returns:
        bool: 成功返回True，失败返回False
    """
    try:
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            if format.lower() == "jsonl" and isinstance(data, list):
                # JSONL格式：每行一个JSON对象
                for item in data:
                    json_line = json.dumps(item, ensure_ascii=False)
                    f.write(json_line + "\n")
            else:
                # 标准JSON格式
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON文件保存成功: {output_path}")
        return True
    except Exception as e:
        logger.error(f"JSON文件保存失败: {e}")
        return False


def save_text(text: str, output_path: str) -> bool:
    """
    保存文本到文件
    
    Args:
        text: 要保存的文本内容
        output_path: 输出文件路径
        
    Returns:
        bool: 成功返回True，失败返回False
    """
    try:
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        logger.info(f"文本文件保存成功: {output_path}")
        return True
    except Exception as e:
        logger.error(f"文本文件保存失败: {e}")
        return False


def save_image(base64_data: str, output_path: str) -> bool:
    """
    保存base64图片数据到文件
    
    Args:
        base64_data: base64编码的图片数据
        output_path: 输出文件路径
        
    Returns:
        bool: 成功返回True，失败返回False
    """
    return decode_base64_to_file(base64_data, output_path)


def is_base64_data(data: str) -> bool:
    """
    判断字符串是否为已编码的base64数据（不需要再次编码）
    
    Args:
        data: 待检查的字符串
        
    Returns:
        bool: 已经是base64格式返回True
    """
    if not data or not isinstance(data, str):
        return False
    
    # 如果是data URL，认为已经是编码好的
    if data.startswith("data:"):
        return True
    
    # 检查是否为纯base64数据
    try:
        base64.b64decode(data, validate=True)
        return True
    except:
        return False


def sanitize_base64(data: str) -> Optional[str]:
    """
    规范化并校验base64字符串：
    - 如果是data URL，提取base64部分
    - 清理空白字符
    - 校验是否为合法base64；非法则返回None
    
    Args:
        data: 输入的base64字符串或data URL
        
    Returns:
        str: 清理后的纯base64字符串，失败返回None
    """
    if not data or not isinstance(data, str):
        return None
    
    # 如果是data URL，提取base64部分
    if data.startswith("data:") and ";base64," in data:
        data = data.split(",", 1)[1]
    
    # 清理空白字符
    cleaned = "".join(data.split())
    
    # 校验base64格式
    try:
        base64.b64decode(cleaned, validate=True)
        return cleaned
    except:
        return None


 