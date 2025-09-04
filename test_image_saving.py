#!/usr/bin/env python3
"""
测试图片保存功能
"""

from langchain_llm import LangChainLLM

def test_image_saving():
    """测试图片保存功能"""
    print("=== 测试图片保存功能 ===\n")
    
    # 创建LLM实例
    llm = LangChainLLM("config.ini")
    
    # 测试1：生成包含图片的响应
    print("1. 测试图片生成:")
    try:
        # 这里使用一个图片生成的提示词
        result = llm.smart_process("请生成一张黄色的花朵图片")
        
        print(f"响应类型: {result['type']}")
        
        if result['type'] == 'multimodal':
            print(f"内容数量: {len(result['content'])}")
            
            for item in result['content']:
                print(f"  类型: {item['type']}")
                if item['type'] == 'text':
                    print(f"    文本: {item['text'][:100]}...")
                elif item['type'] == 'image':
                    print(f"    图片类型: {item['image_type']}")
                    print(f"    图片索引: {item['index']}")
                    print(f"    base64数据长度: {len(item['base64_data'])}")
            
            # 保存图片
            print("\n2. 保存图片:")
            save_result = llm.save_images_from_response(result, "test_images")
            
            print(f"保存成功: {len(save_result['saved_images'])} 张")
            for img in save_result['saved_images']:
                print(f"  ✅ {img['filename']} - {img['size_bytes']} 字节")
            
            if save_result['errors']:
                print(f"保存失败: {len(save_result['errors'])} 张")
                for error in save_result['errors']:
                    print(f"  ❌ {error}")
        
        elif result['type'] == 'text':
            print("纯文本响应，没有图片")
            print(f"文本内容: {result['text'][:200]}...")
        
        elif result['type'] == 'error':
            print(f"处理错误: {result['error']}")
            
    except Exception as e:
        print(f"测试失败: {e}")
    
    print("\n" + "="*50)

def test_with_sample_response():
    """使用示例响应测试图片保存"""
    print("=== 使用示例响应测试 ===\n")
    
    llm = LangChainLLM("config.ini")
    
    # 模拟一个包含图片的响应
    sample_response = {
        "type": "multimodal",
        "content": [
            {
                "type": "text",
                "text": "好的，这是将图片色彩改为黄色的效果："
            },
            {
                "type": "image",
                "image_type": "png",
                "base64_data": "iVBORw0KGgoAAAANSUhEUgAABUAAAAMACAIAAABq7Fo6AAAAiXpUWHRSYXcgcHJvZmlsZSB0eXBlIGlwdGMAAAiZTYwxDgIxDAT7vOKekDjrtV1T0VHwgbtcIiEhgfh/QaDgmGlWW0w6X66n5fl6jNu9p+ULkapDENgzpj+Kl5aFfa6KnYWgSjZjGOiSYRxTY/v8KIijI/rXyc236kHdAK22RvHVummEN+91ML0BQ+siou79WmMAAAKHaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/PiA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA1LjUuMCI+IDxyZGY6UkRGIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+IDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiIHhtbG5zOklwdGM0eG1wRXh0PSJodHRwOi8vaXB0Yy5vcmcvc3RkL0lwdGM0eG1wRXh0LzIwMDgtMDItMjkvIiB4bWxuczpwaG90b3Nob3A9Imh0dHA6Ly9ucy5hZG9iZS5jb20vcGhvdG9zaG9wLzEuMC8iIElwdGM0eG1wRXh0OkRpZ2l0YWxTb3VyY2VGaWxlVHlwZT0iaHR0cDovL2N2LmlwdGMub3JnL25ld3Njb2Rlcy9kaWdpdGFsc291cmNldHlwZS90cmFpbmVkQWxnb3JpdGhtaWNNZWRpYSIgSXB0YzR4bXBFeHQ6RGlnaXRhbFNvdXJjZVR5cGU9Imh0dHA6Ly9jdi5pcHRjLm9yZy9uZXdzY29kZXMvZGlnaXRhbHNvdXJjZXR5cGUvdHJhaW5lZEFsZ29yaXRobWljTWVkaWEiIHBob3Rvc2hvcDpDcmVkaXQ9Ik1hZGUgd2l0aCBHb29nbGUgQUkiLz4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gICA8P3hwYWNrZXQgZW5kPSJ3Ij8+fxJoawAAIABJREFUeJycvVnTJElyGObuEZl1fFdf0z33ziyIBRbXYpdYYSWDSRRA8DBBlElmEk2v0rP0j/SiF8lkMJlJFAkYKa4IEjRiDaBwcW/N7tzT09fX/V1VlZnhrocI9/DIqh5AKpvpryozMsLv9/DwiMRffnsdEEUABAAAAQUFAQBAABEAMF8XAAQEkXwLAAQRqDwr1s4eyS3tU663F/VG/qe9i+67QO133s71i4DinwEBQMR6IcNJICJExMIggkgsgoiICCLCjIhA",
                "index": 1
            }
        ]
    }
    
    print("模拟响应内容:")
    print(f"类型: {sample_response['type']}")
    print(f"内容数量: {len(sample_response['content'])}")
    
    for item in sample_response['content']:
        print(f"  类型: {item['type']}")
        if item['type'] == 'text':
            print(f"    文本: {item['text']}")
        elif item['type'] == 'image':
            print(f"    图片类型: {item['image_type']}")
            print(f"    图片索引: {item['index']}")
            print(f"    base64数据长度: {len(item['base64_data'])}")
    
    # 保存图片
    print("\n保存图片:")
    save_result = llm.save_images_from_response(sample_response, "sample_images")
    
    print(f"保存成功: {len(save_result['saved_images'])} 张")
    for img in save_result['saved_images']:
        print(f"  ✅ {img['filename']} - {img['size_bytes']} 字节")
    
    if save_result['errors']:
        print(f"保存失败: {len(save_result['errors'])} 张")
        for error in save_result['errors']:
            print(f"  ❌ {error}")

if __name__ == "__main__":
    # 测试真实API调用
    test_image_saving()
    
    # 测试示例响应
    test_with_sample_response() 