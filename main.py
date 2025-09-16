#!/usr/bin/env python3
"""
主程序 - 模块化架构
使用流水线框架执行多轮AI处理
"""

from core.pipeline_controller import PipelineController
from processors.output_processor import FileOutputProcessor, ConsoleOutputProcessor
from utils.log_config import setup_logging

def main():
    """主函数 - 使用模块化架构"""
    # 初始化日志系统
    logger = setup_logging(level='INFO', log_file='logs/pipeline.log')
    logger.info("启动LangChain流水线系统")
    
    # 1. 创建流水线控制器
    controller = PipelineController("config/config.ini")
    
    # 2. 准备输入数据（原始格式）
    raw_input = {
        "text": """Use the nano-banana model to create a 1/7 scale commercialized figure of the character in the illustration, 
in a realistic style and environment. Place the figure on a computer desk, using a circular transparent 
acrylic base without any text. On the computer screen, display the ZBrush modeling process of the figure. 
Next to the computer screen, place a BANDAI-style toy packaging box printed with the original artwork.""",
        "image": "/Users/macbook/Workspace/project/pjlab/langchain/input/test.jpg",
        "filename": "test"
    }

    # raw_input = {
    #     "text": "",
    #     # "image": "/Users/macbook/Workspace/project/pjlab/langchain/input/test.jpg",
    #     "promptVariables": {
    #         "country": "中国",
    #         "age": 18
    #     }
    # }    
    
    # 提取filename，如果没有则使用默认值
    filename = raw_input.get("filename", "default")
    
    # 3. 执行流水线
    logger.info("开始执行流水线...")
    results = controller.execute_pipeline(raw_input)
    
    # 4. 打印流水线状态
    controller.print_pipeline_status()
    
    # 5. 处理输出
    logger.info("处理输出...")
    console_processor = ConsoleOutputProcessor()
    output_processor = FileOutputProcessor()
    console_processor.process(results)  # 控制台输出
    output_processor.process(results, output_dir="outputs", filename=filename)  # 文件输出
    
    logger.info("🎉 流水线系统运行完成！")
    return results

if __name__ == "__main__":
    main()
