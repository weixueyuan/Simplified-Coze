#!/usr/bin/env python3
"""
主程序
展示如何使用配置化的LangChain LLM
"""

from langchain_llm import LangChainLLM
from config_reader import ConfigReader

def save_images_from_response(response_data: list, output_dir: str = "saved_images"):
    """从响应中保存图片"""
    import os
    import base64
    from pathlib import Path
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    result = {
        "saved_images": [],
        "errors": []
    }
    
    # 直接遍历列表
    for item in response_data:
        print("item is ",item)
        if item["type"] == "image":
            try:
                # 获取图片数据
                base64_data = item.get("base64_data")
                image_type = item.get("image_type", "png")
                
                if base64_data:
                    # 解码base64数据
                    image_data = base64.b64decode(base64_data)
                    
                    # 生成文件名
                    if image_type.lower() == 'jpeg':
                        image_type = 'jpg'
                    filename = f"generated_image_{item.get('index', 1)}.{image_type}"
                    file_path = output_path / filename
                    
                    # 保存图片
                    with open(file_path, 'wb') as f:
                        f.write(image_data)
                    
                    result["saved_images"].append({
                        "filename": filename,
                        "file_path": str(file_path),
                        "size_bytes": len(image_data),
                        "type": image_type
                    })
                    
                    print(f"✅ 图片已保存: {file_path}")
                else:
                    result["errors"].append(f"图片缺少base64数据")
                    
            except Exception as e:
                error_msg = f"保存图片失败: {e}"
                result["errors"].append(error_msg)
                print(f"❌ {error_msg}")

    
def main():
    """主函数"""
    print("=== LangChain配置化LLM使用示例 ===\n")
    
    # 创建LLM实例
    llm = LangChainLLM("config.ini")
    
    # 显示可用模型
    print("可用模型:")
    models = llm.get_available_models()
    print(models)
    
    # 获取当前配置
    config = llm.get_model_config()
    print(f"当前配置: {config['section']}")
    print(f"模型: {config['model']}")
    print()
    
    # 示例1：使用默认配置处理文本
    print("=== 示例1：文本处理（使用默认配置） ===")
    try:
        result = llm.smart_process("帮我生成一个吉卜力风格的人物头像,直接返回生成的头像,不要有任何解释")
        save_images_from_response(result)
        # print(f"结果: {result}")
    except Exception as e:
        print(f"错误: {e}")
    print()
    
    # # 示例3：图片处理
    print("=== 示例3：图片处理 ===")
    image_path = "/Users/macbook/Documents/19293.jpeg"  # 替换为你的图片路径
    try:
        result = llm.smart_process("请将这张图片的色彩换成黄色", file_path=image_path)
        save_images_from_response(result,"saved_images1")
        print(f"结果: {result}")
    except FileNotFoundError:
        print(f"图片文件未找到: {image_path}")
        print("请将 image_path 替换为你的实际图片路径")
    except Exception as e:
        print(f"错误: {e}")
    print()
    
    # # 示例4：视频处理
    # print("=== 示例4：视频处理 ===")
    # video_path = "test_video.mp4"  # 替换为你的视频路径
    # try:
    #     result = llm.smart_process("请描述这个视频的内容", file_path=video_path)
    #     print(f"结果: {result}")
    # except FileNotFoundError:
    #     print(f"视频文件未找到: {video_path}")
    #     print("请将 video_path 替换为你的实际视频路径")
    # except Exception as e:
    #     print(f"错误: {e}")
    # print()
    
    # # 示例5：音频处理
    # print("=== 示例5：音频处理 ===")
    # audio_path = "test_audio.wav"  # 替换为你的音频路径
    # try:
    #     result = llm.smart_process("请描述这个音频的内容", file_path=audio_path)
    #     print(f"结果: {result}")
    # except FileNotFoundError:
    #     print(f"音频文件未找到: {audio_path}")
    #     print("请将 audio_path 替换为你的实际音频路径")
    # except Exception as e:
    #     print(f"错误: {e}")
    # print()

def interactive_mode():
    """交互模式"""
    llm = LangChainLLM("config.ini")
    
    print("=== 交互模式 ===")
    print("输入 'quit' 退出")
    print("可用模型:", ", ".join(llm.get_available_models()))
    print()
    
    while True:
        # 选择模型
        print("可用模型:")
        models = llm.get_available_models()
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model}")
        
        try:
            choice = input("请选择模型编号（或输入模型名称）: ").strip()
            if choice.lower() == 'quit':
                break
            
            # 解析选择
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(models):
                    section = models[idx]
                else:
                    print("无效的选择")
                    continue
            else:
                section = choice
                if section not in models:
                    print(f"模型 '{section}' 不存在")
                    continue
            
            # 获取输入
            text = input("请输入问题: ").strip()
            if text.lower() == 'quit':
                break
            
            file_path = input("请输入文件路径（可选，直接回车跳过）: ").strip()
            if not file_path:
                file_path = None
            
            # 处理
            print(f"使用模型: {section}")
            result = llm.smart_process(text, file_path, section)
            print(f"结果: {result}")
            
        except Exception as e:
            print(f"处理失败: {e}")
        
        print("-" * 50)

def show_config():
    """显示配置信息"""
    config_reader = ConfigReader("config.ini")
    
    print("=== 当前配置 ===")
    configs = config_reader.get_all_configs()
    for section, config in configs.items():
        print(f"\n[{section}]")
        for key, value in config.items():
            if key == "api_key":
                # 隐藏API密钥
                masked_key = value[:8] + "..." if len(value) > 8 else "***"
                print(f"  {key} = {masked_key}")
            else:
                print(f"  {key} = {value}")

if __name__ == "__main__":
    # 显示配置信息
    show_config()
    print()
    
    # 运行示例
    main()
    
    # 可选：运行交互模式
    # interactive_mode() 