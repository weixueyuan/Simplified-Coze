#!/usr/bin/env python3
"""
配置读取器
使用configparser读取配置文件
"""

import os
from typing import Dict, Any, List
import configparser
from utils.log_config import get_logger

class ConfigReader:
    """配置读取器"""
    
    def __init__(self, config_file: str = "config/config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.logger = get_logger('config.reader')
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
        
        self.config.read(self.config_file, encoding='utf-8')
        self.logger.info(f"📋 成功加载配置文件: {self.config_file}")
    
    def get_pipeline_configs(self) -> List[Dict[str, Any]]:
        """获取流水线配置列表"""
        configs = []
        
        # 获取所有配置节（排除特殊节）
        sections = self.config.sections()
        exclude_sections = ['available_modes']
        
        for section in sections:
            if section not in exclude_sections:
                config = self.get_llm_config(section)
                configs.append(config)
        
        for i, config in enumerate(configs):
            self.logger.info(f"  {i+1}. {config['section_name']}: {config['model']}")
        
        return configs
    
    def get_llm_config(self, section: str) -> Dict[str, Any]:
        """获取指定节的LLM配置"""
        if section not in self.config.sections():
            raise ValueError(f"配置节不存在: {section}")
        
        config = {
            "section_name": section,
            "model": self.config.get(section, 'model'),
            "api_key": self.config.get(section, 'api_key'),
            "base_url": self.config.get(section, 'base_url'),
        }
        
        # 读取其他配置项（如prompt等）
        for option in self.config.options(section):
            if option not in ["max_tokens", "temperature", "prompt"]:
                config[option] = self.config.get(section, option)
        
        return config 