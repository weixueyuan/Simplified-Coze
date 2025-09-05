#!/usr/bin/env python3
"""
配置读取器
使用configparser读取配置文件
"""

import os
from typing import Dict, Any, List
import configparser

class ConfigReader:
    """配置读取器"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
        
        self.config.read(self.config_file, encoding='utf-8')
        print(f"📋 成功加载配置文件: {self.config_file}")
    
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
        
        print(f"📋 找到 {len(configs)} 个流水线配置")
        for i, config in enumerate(configs):
            print(f"  {i+1}. {config['section_name']}: {config['model']}")
        
        return configs
    
    def get_llm_config(self, section: str) -> Dict[str, Any]:
        """获取LLM配置"""
        if section not in self.config:
            raise Exception(f"配置节不存在: {section}")
        
        # 基础配置
        config = {
            "section_name": section,
            "model": self.config.get(section, "model"),
            "base_url": self.config.get(section, "base_url"),
            "api_key": self.config.get(section, "api_key"),
            "max_tokens": self.config.getint(section, "max_tokens"),
            "temperature": self.config.getfloat(section, "temperature")
        }
        
        # 读取所有其他配置项（如prompt, input等）
        for option in self.config.options(section):
            if option not in ["model", "base_url", "api_key", "max_tokens", "temperature"]:
                config[option] = self.config.get(section, option)
        
        return config
    
    def get_config_by_name(self, section_name: str) -> Dict[str, Any]:
        """根据section名称获取配置"""
        return self.get_llm_config(section_name)
    
    def reload_config(self):
        """重新加载配置"""
        self.config.clear()
        self.load_config() 