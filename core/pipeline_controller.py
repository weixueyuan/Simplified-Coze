#!/usr/bin/env python3
"""
流水线控制器 - 核心逻辑模块
管理整个流水线的执行，支持配置驱动的多轮处理
"""

from typing import Dict, Any, List, Optional
from config.config_reader import ConfigReader
from core.langchain_llm import LangChainLLM
from core.pipeline_memory import PipelineMemory
from processors.input_processor import PipelineInputProcessor
from utils import create_error_data
from utils.log_config import get_logger

class PipelineController:
    """流水线控制器 - 纯核心逻辑"""
    
    def __init__(self, config_file: str = "config/config.ini"):
        # 首先初始化logger，因为其他方法会用到
        self.logger = get_logger('pipeline.controller')
        self.config_reader = ConfigReader(config_file)
        self.memory = PipelineMemory()
        self.pipeline_configs = self._load_pipeline_configs()
        self.llm_instances = {}  # 缓存LLM实例
        self.config_file = config_file
        self.error_occurred = False  # 错误标志
        self.error_message = ""      # 错误信息
    
    def _load_pipeline_configs(self) -> List[Dict[str, Any]]:
        """加载流水线配置，按顺序排列"""
        configs = self.config_reader.get_pipeline_configs()
        
        self.logger.info(f"📋 加载了 {len(configs)} 轮流水线配置")
        for i, config in enumerate(configs):
            self.logger.info(f"配置 {i+1}: {config['section_name']} -> {config['model']}")
            if config.get('prompt'):
                self.logger.debug(f"提示词预览: {config['prompt'][:100]}...")
        
        return configs
    
    def execute_pipeline(self, initial_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行完整的流水线 - 纯逻辑，不处理输入输出"""
        self.error_occurred = False
        self.error_message = ""        
        results = []
        try:
            for i, config in enumerate(self.pipeline_configs):
                self.logger.info(f"{'='*20} 第{i}轮: {config['section_name']} {'='*20}")
                if i == 0:
                    if isinstance(initial_input, dict) and initial_input.get("promptVariables"):
                        self.memory.store_round_memory(initial_input["promptVariables"], -1)
                output = self._execute_single_round(config, i, initial_input)
                
                if not self._handle_round_result(output, config, i, results):
                    break  # 停止流水线
            
            self._finalize_pipeline()
                
        except Exception as e:
            self._handle_critical_error(e)
            self.memory.clear_memory()
        
        return results
    
    def _execute_single_round(self, config: Dict[str, Any], round_index: int, initial_input: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """执行单轮处理"""
        # 获取或创建LLM实例（内部会设置环境变量）
        llm = self._get_llm_instance(config)
        
        # 处理输入
        input_processor = PipelineInputProcessor(self.memory)
        if round_index == 0:
            input_dict = input_processor.process(config, initial_input)
            self.memory.store_round_memory(input_dict, 0)  
        else:
            input_dict = input_processor.process(config, {})
      
        # 打印输入信息（避免打印base64等长内容）
        self.logger.info(f"第{round_index}轮输入: {self._mask_media_for_log(input_dict)}")
        
        # 调用LLM处理
        try:
            output = llm.smart_process(input_dict)
        except Exception as e:
            self.logger.error(f"第{round_index}轮执行失败: {e}")
            output = create_error_data(str(e))
        
        # 打印输出信息
        self.logger.info(f"📥 第{round_index}轮输出:")
        self.logger.info(f"  文本: {output.get('text', '')[:100]}..." if output.get('text') else "  文本: 无")
        self.logger.info(f"  图片: {'已生成' if output.get('image') else '无'}")
        self.logger.info(f"  视频: {'已生成' if output.get('video') else '无'}")
        
        return output
    

    def _handle_round_result(self, output: Dict[str, Any], config: Dict[str, Any], round_index: int, results: List) -> bool:
        """处理单轮结果，返回是否继续执行"""
        # 检查输出是否有错误
        if self._is_error_output(output):
            self._handle_pipeline_error(round_index, config, output)
            return False  # 停止流水线
        
        # 存储输出到memory
        self.memory.store_round_memory(output, round_index+1)
        results.append({
            "round": round_index+1,
            "config": config['section_name'],
            "output": output,
            "status": "success"
        })
        
        self.memory.print_memory_status()
        self.logger.info(f"✅ 第{round_index}轮执行成功")
        
        return True  # 继续执行
    
    def _finalize_pipeline(self) -> None:
        """完成流水线处理"""
        if not self.error_occurred:
            self.logger.info("🎉 流水线执行完成！")
            # 避免直接打印包含base64的完整内存
            self.logger.info("流水线结果概要:")
            self.logger.info(self.memory.get_memory_summary())
        else:
            self.logger.error("流水线执行失败")
            self.logger.error(f"错误信息: {self.error_message}")
        
        # 所有轮次结束后清空记忆
        self.memory.clear_memory()

    def _get_llm_instance(self, config: Dict[str, Any]) -> LangChainLLM:
        """获取或创建LLM实例"""
        section_name = config['section_name']
        
        if section_name not in self.llm_instances:
            llm = LangChainLLM(self.config_file)
            llm.init_model_with_config(config)  # 这里会设置环境变量
            self.llm_instances[section_name] = llm
        
        return self.llm_instances[section_name]
    

    def _is_error_output(self, output: Dict[str, Any]) -> bool:
        """检查输出是否表示错误"""
        text = output.get('text', '').lower()
        error_keywords = ['执行失败', 'error', '失败', '错误', 'exception']
        return any(keyword in text for keyword in error_keywords)
    
    def _handle_pipeline_error(self, round_index: int, config: Dict[str, Any], output: Dict[str, Any]):
        """处理流水线错误"""
        error_message = f"第{round_index}轮 ({config['section_name']}) 执行失败: {output.get('text', '未知错误')}"
        self._stop_pipeline(
            title="流水线错误报警",
            error_message=error_message,
            extra_info={
                "错误轮次": f"第{round_index}轮",
                "错误配置": config['section_name']
            }
        )
    
    def _handle_critical_error(self, error: Exception):
        """处理严重错误"""
        self._stop_pipeline(
            title="严重错误",
            error_message=f"严重错误: {str(error)}"
        )

    def _stop_pipeline(self, title: str, error_message: str, extra_info: Dict[str, Any] | None = None):
        """统一停止流水线并输出错误信息"""
        self.error_occurred = True
        self.error_message = error_message
        self.logger.critical(f"{title}")
        if extra_info:
            for key, value in extra_info.items():
                self.logger.error(f"{key}: {value}")
        self.logger.error(f"错误信息: {self.error_message}")
        self.logger.error("流水线已停止执行！")
    
    def print_pipeline_status(self):
        """打印流水线状态"""
        self.logger.info("=== 流水线状态 ===")
        self.logger.info(f"总轮数: {len(self.pipeline_configs)}")
        self.logger.info(f"已完成: {len(self.memory.memory)}")
        if self.error_occurred:
            self.logger.error(f"状态: 有错误")
            self.logger.error(f"错误信息: {self.error_message}")
        else:
            self.logger.info("状态: 正常")
        
        self.memory.print_memory_status()

    def _mask_media_for_log(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """将包含媒体内容的输入/输出进行脱敏，避免在日志中打印base64等大字段"""
        if not isinstance(data, dict):
            return data
        masked: Dict[str, Any] = dict(data)
        if masked.get('image'):
            masked['image'] = '[image base64 omitted]'
        if masked.get('video'):
            masked['video'] = '[video base64 omitted]'
        if isinstance(masked.get('text'), str) and len(masked.get('text')) > 200:
            masked['text'] = masked['text'][:200] + '...'
        return masked
