#!/usr/bin/env python3
"""
配置读取模块
读取config.ini文件中的配置信息
"""

import configparser
import os
from typing import Dict, Any, List

from pydantic import config

class ConfigReader:
    """配置读取类"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
    
    def get_llm_config(self, section: str = None) -> Dict[str, Any]:
        """获取LLM配置"""
        # 如果没有指定section，自动选择第一个可用的配置节
        print("=== 配置文件内容 ===")
        print("所有配置节:", self.config.sections())
        for sec in self.config.sections():
            print(f"\n[{sec}]")
            if self.config.has_section(sec):
                for key in self.config.options(sec):
                    value = self.config.get(sec, key)
                    if key == "api_key":
                        # 隐藏API密钥
                        masked_value = value[:8] + "..." if len(value) > 8 else "***"
                        print(f"  {key} = {masked_value}")
                    else:
                        print(f"  {key} = {value}")
        
        if section is None:
            for sec in self.config.sections():
                if sec != "available_modes":  # 排除模式配置节
                    section = sec
                    break
            if section is None:
                raise Exception("没有找到可用的LLM配置节")
        
        return {
            "section": section,
            "model": self.config.get(section, "model"),
            "base_url": self.config.get(section, "base_url"),
            "api_key": self.config.get(section, "api_key"),
            "max_tokens": self.config.getint(section, "max_tokens"),
            "temperature": self.config.getfloat(section, "temperature")
        }
    
    def get_available_modes(self) -> List[str]:
        """获取可用的模式列表"""
        if "available_modes" in self.config and self.config.has_option("available_modes", "modes"):
            modes_str = self.config.get("available_modes", "modes")
            return [mode.strip() for mode in modes_str.split(",")]
        return ["openai"]  # 默认只有openai模式
    
    def is_valid_mode(self, mode: str) -> bool:
        """检查模式是否有效"""
        available_modes = self.get_available_modes()
        return mode in available_modes
    
    def get_model_provider(self, section: str) -> str:
        """根据配置节名称获取提供商"""
        # 从配置节名称推断模式
        if section == "claude":
            return "claude"
        elif section == "google":
            return "google"
        elif section == "dashscope":
            return "dashscope"
        elif section == "zhipu":
            return "zhipu"
        else:
            # 检查配置节名称是否在可用模式列表中
            if self.is_valid_mode(section):
                return section
            else:
                # 如果不在可用列表中，默认使用openai
                return "openai"
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取所有配置"""
        configs = {}
        for section in self.config.sections():
            if section != "available_modes":  # 排除模式配置节
                configs[section] = self.get_llm_config(section)
        return configs
    
    def get_available_models(self) -> list:
        """获取可用的模型列表"""
        models = []
        for section in self.config.sections():
            if section != "available_modes":  # 排除模式配置节
                models.append(section)
        return models
    
    def update_config(self, section: str, key: str, value: str):
        """更新配置"""
        if section not in self.config:
            self.config.add_section(section)
        
        self.config.set(section, key, value)
        
        # 保存到文件
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def set_api_key(self, section: str, api_key: str):
        """设置API密钥"""
        self.update_config(section, "api_key", api_key)
    
    def add_available_mode(self, mode: str):
        """添加可用模式"""
        if "available_modes" not in self.config:
            self.config.add_section("available_modes")
        
        current_modes = self.get_available_modes()
        if mode not in current_modes:
            current_modes.append(mode)
            modes_str = ",".join(current_modes)
            self.config.set("available_modes", "modes", modes_str)
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
    
    def reload_config(self):
        """重新加载配置"""
        self.load_config() 