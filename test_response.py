#!/usr/bin/env python3
"""
测试新的响应格式
"""

from langchain_llm import LangChainLLM

def test_new_response_format():
    """测试新的响应格式"""
    print("=== 测试新的响应格式 ===\n")
    
    # 创建LLM实例
    llm = LangChainLLM("config.ini")
    
    # 测试文本处理
    print("1. 测试文本处理:")
    result = llm.process_text("请简单介绍一下Python")
    print(f"返回类型: {result['type']}")
    if result['type'] == 'text':
        print(f"文本内容: {result['text'][:100]}...")
    elif result['type'] == 'error':
        print(f"错误: {result['error']}")
    print()
    
    # 测试图片处理（如果有图片文件的话）
    print("2. 测试图片处理:")
    try:
        # 这里需要替换为实际的图片路径
        image_path = "/Users/macbook/Documents/19293.jpeg"
        result = llm.process_image(image_path, "请描述这张图片")
        print(f"返回类型: {result['type']}")
        if result['type'] == 'multimodal':
            for item in result['content']:
                if item['type'] == 'text':
                    print(f"文本内容: {item['text'][:100]}...")
                elif item['type'] == 'image':
                    print(f"图片数据: {item['data'][:50] if item['data'] else 'None'}...")
        elif result['type'] == 'text':
            print(f"文本内容: {result['text'][:100]}...")
        elif result['type'] == 'error':
            print(f"错误: {result['error']}")
    except Exception as e:
        print(f"图片处理测试失败: {e}")
    print()
    
    # 测试智能处理
    print("3. 测试智能处理:")
    result = llm.smart_process("请介绍一下机器学习")
    print(f"返回类型: {result['type']}")
    if result['type'] == 'text':
        print(f"文本内容: {result['text'][:100]}...")
    elif result['type'] == 'error':
        print(f"错误: {result['error']}")
    print()

if __name__ == "__main__":
    test_new_response_format() 