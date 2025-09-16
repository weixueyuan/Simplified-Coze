#!/usr/bin/env python3
"""
处理器模块 - 包含输入处理器和输出处理器
"""
from .input_processor import PipelineInputProcessor
from .output_processor import FileOutputProcessor, ConsoleOutputProcessor

__all__ = [
    'PipelineInputProcessor',
    'FileOutputProcessor',
    'ConsoleOutputProcessor',
]
