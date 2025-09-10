#!/usr/bin/env python3
"""
流水线控制器
管理整个流水线的执行，支持配置驱动的多轮处理
"""

import os
from typing import Dict, Any, List, Optional
from config_reader import ConfigReader
from langchain_llm import LangChainLLM
from pipeline_memory import PipelineMemory
from pathlib import Path
import json
import re

class PipelineController:
    """流水线控制器"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_reader = ConfigReader(config_file)
        self.memory = PipelineMemory()
        self.pipeline_configs = self._load_pipeline_configs()
        self.llm_instances = {}  # 缓存LLM实例
        self.config_file = config_file # 添加config_file属性
        self.error_occurred = False  # 错误标志
        self.error_message = ""      # 错误信息
    
    def _load_pipeline_configs(self) -> List[Dict[str, Any]]:
        """加载流水线配置，按顺序排列"""
        # 直接获取配置列表
        configs = self.config_reader.get_pipeline_configs()
        
        print(f"📋 加载了 {len(configs)} 轮流水线配置")
        for i, config in enumerate(configs):
            print(f"  {i+1}. {config['section_name']}: {config['model']}")
            if config.get('prompt'):
                print(f"     提示词: {config['prompt']}")
        
        return configs
    
    def execute_pipeline(self, initial_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行完整的流水线"""
        print(f"🚀 开始执行流水线，共{len(self.pipeline_configs)}轮")
        
        # 重置错误状态
        self.error_occurred = False
        self.error_message = ""
        
        # 处理初始输入（一定是字典格式）
        print("📥 输入格式: 字典")
        if 'text' in initial_input:
            print(f"  文本: {initial_input['text']}")
        if 'image' in initial_input:
            print(f"  图片: [已编码，大小: {len(initial_input['image'])} 字符]")
        if 'video' in initial_input:
            print(f"  视频: [已编码，大小: {len(initial_input['video'])} 字符]")
        
        results = []
        
        try:
            for i, config in enumerate(self.pipeline_configs):
                print(f"\n{'='*50}")
                print(f"第{i}轮: {config['section_name']}")
                print(f"{'='*50}")
                print(f"🔍 初始输入: {initial_input}")
                
                # 执行当前轮次
                output = self._execute_round(config, i, initial_input)
                
                # 检查是否出错
                if self._is_error_output(output):
                    self._handle_pipeline_error(i, config, output)
                    break
                
                # 存储输出到memory
                self.memory.store_round_output(output, i+1)
                
                # 保存结果
                results.append({
                    'round': i+1,
                    'config': config['section_name'],
                    'output': output,
                    'status': 'success'
                })
                
                # 打印memory状态
                self.memory.print_memory_status()
                
                print(f"✅ 第{i}轮执行成功")
            
            if not self.error_occurred:
                print(f"\n🎉 流水线执行完成！")
                print(f"🔍 流水线结果: {self.memory.memory}")
            else:
                print(f"\n❌ 流水线执行失败！")
                print(f"🔍 错误信息: {self.error_message}")
                
        except Exception as e:
            self._handle_critical_error(e)
        
        return results
    
    def _execute_round(self, config: Dict[str, Any], round_index: int, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """执行单轮处理"""
        try:
            print(f"\n🔄 执行第{round_index}轮: {config['section_name']}")
            print(f"模型: {config['model']}")
            
            # 设置环境变量
            self._setup_environment(config)
            
            # 创建LLM实例
            llm = LangChainLLM(self.config_file)
            llm.init_model()
            
            # 判断是否有input配置
            input_spec = config.get('input', '')
            
            if not input_spec:
                # 没有input配置，默认使用上一轮输出
                if round_index == 0:
                    # 首轮，使用初始输入
                    input_dict = self._build_input_dict(config, initial_input)
                    self.memory.store_round_output(input_dict, 0)
                else:
                    # 非首轮，使用上一轮输出
                    last_output = self.memory.get_last_output()
                    if last_output:
                        input_dict = self._build_input_dict(config, last_output)
                    else:
                        print(f"❌ 第{round_index}轮执行失败: {e}")
                        return {"text": f"执行失败: {e}", "image": "", "video": ""}
                        # input_dict = self._build_input_dict(config, {"text": "请继续处理"})
            else:
                # 有input配置，从memory取对应数据
                input_dict = self._build_input_from_spec(config, input_spec)
                print(f"🔍 输入字典: {input_dict}")
            
            output = llm._process_input(input_dict)
            print(f"✅ 第{round_index}轮执行完成")
            return output
            
        except Exception as e:
            print(f"❌ 第{round_index}轮执行失败: {e}")
            return {"text": f"执行失败: {e}", "image": "", "video": ""}
    
    def _build_input_dict(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """构建输入字典：prompt + 数据"""
        prompt = config.get('prompt', '')
        input_dict = {
            "text": f"{prompt}\n\n{data.get('text', '')}"
        }
        
        # 添加图片和视频数据
        if 'image' in data:
            input_dict['image'] = data['image']
        if 'video' in data:
            input_dict['video'] = data['video']
        
        return input_dict
    
    def _build_input_from_spec(self, config: Dict[str, Any], input_spec: str) -> Dict[str, Any]:
        """根据input配置从memory构建输入"""
        prompt = config.get('prompt', '')
        input_dict = {"text": ""}
        
        # 解析input参数（如 "text0,text1"）
        text_parts = []
        
        for item in input_spec.split(','):
            item = item.strip()
            if not item:
                continue
            
            # 解析格式：type + index（如 text0, text1）
            # 找到最后一个数字作为索引
            match = re.search(r'([a-zA-Z]+)(\d+)$', item)
            
            if match:
                content_type = match.group(1)  # text, image, video
                index = int(match.group(2))    # 0, 1, 2...
                
                # 从memory获取对应数据
                round_data = self.memory.get_round_output(index)
                if round_data and content_type in round_data:
                    if content_type == 'text':
                        text_parts.append(round_data[content_type])
                    else:
                        input_dict[content_type] = round_data[content_type]
                else:
                    # 如果指定的轮次或内容类型不存在，抛出异常
                    raise ValueError(f"指定的{content_type}{index}不存在或为空")
            else:
                # 如果格式不正确，抛出异常
                raise ValueError(f"input配置格式错误: '{item}'，应为 'type+index' 格式（如 'text0, text1'）")
        
        # 组合所有文本内容
        if text_parts:
            input_dict['text'] = f"{prompt}\n\n" + ",".join(text_parts)
        else:
            input_dict['text'] = prompt
            
        return input_dict
    
    def _setup_environment(self, config: Dict):
        """设置环境变量"""
        # 根据模型类型设置不同的环境变量
        model = config['model'].lower()
        section_name = config.get('section_name', '').lower()
        
        if 'claude' in section_name:
            os.environ["ANTHROPIC_API_KEY"] = config['api_key']
            os.environ["ANTHROPIC_BASE_URL"] = config['base_url']
        elif 'gemini' in model or 'gemini' in section_name:
            os.environ["GOOGLE_API_KEY"] = config['api_key']
            os.environ["GOOGLE_BASE_URL"] = config['base_url']
        else:
            # 默认使用OpenAI兼容格式
            os.environ["OPENAI_API_KEY"] = config['api_key']
            os.environ["OPENAI_BASE_URL"] = config['base_url']
    
    def save_pipeline_outputs(self, results: List[Dict[str, Any]], output_dir: str = "outputs"):
        """保存流水线输出"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n💾 保存流水线输出到: {output_path}")
        
        # 保存每轮输出
        for result in results:
            round_num = result['round']
            config_name = result['config']
            output = result['output']
            
            # 创建轮次目录
            round_dir = output_path / f"round_{round_num}_{config_name}"
            round_dir.mkdir(exist_ok=True)
            
            # 保存文本内容
            if output.get("text"):
                text_file = round_dir / "output.txt"
                with open(text_file, "w", encoding="utf-8") as f:
                    f.write(output["text"])
                print(f"  📝 保存文本: {text_file}")
            
            # 保存图片内容
            if output.get("image"):
                image_file = round_dir / "output.png"
                try:
                    import base64
                    # 提取base64数据
                    match = re.match(r"data:image/([^;]+);base64,(.*)", output["image"])
                    if match:
                        image_type = match.group(1)
                        base64_data = match.group(2)
                        image_data = base64.b64decode(base64_data)
                        with open(image_file, "wb") as f:
                            f.write(image_data)
                        print(f"  🖼️ 保存图片: {image_file}")
                    else:
                        print(f"  ❌ 图片数据格式错误，无法保存")
                except Exception as e:
                    print(f"  ❌ 保存图片失败: {e}")
            
            # 保存JSON格式的输出
            json_file = round_dir / "output.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"  📄 保存JSON: {json_file}")
        
        # 保存完整的流水线日志
        pipeline_log = output_path / "pipeline_log.json"
        with open(pipeline_log, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"  📋 保存流水线日志: {pipeline_log}")
        
        # 保存memory日志
        self.memory.save_memory_log(str(output_path))
        
        # 在保存逻辑的最后添加错误日志保存
        if self.error_occurred:
            error_log = output_path / "error_log.txt"
            with open(error_log, 'w', encoding='utf-8') as f:
                f.write(f"Pipeline Error Log\n")
                f.write(f"==================\n")
                f.write(f"Error Occurred: {self.error_occurred}\n")
                f.write(f"Error Message: {self.error_message}\n")
                f.write(f"Timestamp: {__import__('datetime').datetime.now()}\n")
            print(f"  📋 保存错误日志: {error_log}")
        
        print(f"✅ 所有输出已保存完成！")
        
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """获取流水线执行摘要"""
        summary = {
            'total_rounds': len(self.pipeline_configs),
            'completed_rounds': len(self.memory.memory),
            'memory_summary': self.memory.get_memory_summary()
        }
        
        return summary
    
    def print_pipeline_status(self):
        """打印流水线状态"""
        print(f"\n=== 流水线状态 ===")
        print(f"总轮数: {len(self.pipeline_configs)}")
        print(f"已完成: {len(self.memory.memory)}")
        print(f"错误状态: {'❌ 有错误' if self.error_occurred else '✅ 正常'}")
        if self.error_occurred:
            print(f"错误信息: {self.error_message}")
        
        self.memory.print_memory_status()
    
    def reset_pipeline(self):
        """重置流水线"""
        self.memory.clear_memory()
        self.llm_instances.clear()
        print("🔄 流水线已重置")

def test_pipeline():
    """测试流水线功能"""
    print("=== 测试流水线功能 ===\n")
    
    controller = PipelineController("config.ini")
    
    # 执行流水线
    print("开始执行流水线...")
    results = controller.execute_pipeline("生成一个可爱的吉卜力风格头像")
    
    # 显示结果摘要
    controller.print_pipeline_status()
    
    # 保存输出
    print("\n保存输出...")
    save_results = controller.save_pipeline_outputs(results)
    
    return results

if __name__ == "__main__":
    test_pipeline() 