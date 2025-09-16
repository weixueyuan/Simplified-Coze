#!/usr/bin/env python3
"""
日志配置模块
使用标准logging库和colorlog实现彩色、分级日志输出
"""

import logging
import logging.handlers
import sys
from pathlib import Path

try:
    import colorlog
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False

# 全局logger缓存
_loggers = {}

def setup_logging(level: str = 'INFO', 
                 log_file: str = 'logs/pipeline.log',
                 console_output: bool = True,
                 colored: bool = True) -> logging.Logger:
    """
    设置日志配置
    
    Args:
        level: 日志级别
        log_file: 日志文件路径
        console_output: 是否控制台输出
        colored: 是否彩色输出
    
    Returns:
        配置好的logger
    """
    logger = logging.getLogger('pipeline')
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除现有handlers
    logger.handlers.clear()
    
    # 设置控制台输出
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        if colored and HAS_COLORLOG:
            # 使用colorlog的彩色格式
            color_formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s - %(levelname)-8s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
            console_handler.setFormatter(color_formatter)
        else:
            # 使用标准格式
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)-8s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    
    # 设置文件输出
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建文件handler，支持日志轮转
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)-8s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """获取logger实例"""
    if name:
        return logging.getLogger(name)
    return logging.getLogger('pipeline')

def set_log_level(level: str) -> None:
    """设置日志级别"""
    logger = get_logger()
    logger.setLevel(getattr(logging, level.upper()))
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            handler.setLevel(getattr(logging, level.upper())) 