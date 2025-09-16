#!/usr/bin/env python3
"""
日志系统使用示例
展示新的基于标准logging的日志功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.log_config import setup_logging, get_logger, set_log_level

def demonstrate_logging():
    """演示日志功能"""
    
    # 1. 基本日志设置
    print("=== 基本日志设置示例 ===")
    logger = setup_logging(
        level='INFO',
        log_file='logs/example.log',
        console_output=True,
        colored=True
    )
    
    # 2. 不同级别的日志输出
    logger.debug("这是调试信息 - 默认不会显示")
    logger.info("这是一般信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    logger.critical("这是严重错误信息")
    
    print("\n=== 调整日志级别到DEBUG ===")
    # 3. 动态调整日志级别
    set_log_level('DEBUG')
    logger.debug("现在可以看到调试信息了")
    logger.info("修改级别后的信息输出")
    
    print("\n=== 不同模块的日志器 ===")
    # 4. 不同模块使用不同的日志器
    pipeline_logger = get_logger('pipeline.test')
    memory_logger = get_logger('memory.test')
    processor_logger = get_logger('processor.test')
    
    pipeline_logger.info("流水线模块日志")
    memory_logger.info("内存模块日志")
    processor_logger.error("处理器模块错误")
    
    print("\n=== 日志级别对比 ===")
    # 5. 展示不同日志级别的使用场景
    logger.debug("调试信息：变量值、函数调用等详细信息")
    logger.info("一般信息：程序正常运行的关键步骤")
    logger.warning("警告信息：程序可以继续但需要注意的问题")
    logger.error("错误信息：程序出现错误但可以恢复")
    logger.critical("严重错误：程序无法继续运行的致命错误")
    
    print("\n✅ 日志示例完成！")
    print(f"📁 日志文件保存位置: logs/example.log")
    print("💡 提示：可以通过 set_log_level() 动态调整日志级别")

if __name__ == "__main__":
    demonstrate_logging() 