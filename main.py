#!/usr/bin/env python3
"""
主程序
使用流水线框架执行多轮AI处理
"""

from pipeline_controller import PipelineController
from typing import Dict, Any

def main():
    """主函数"""
    print("🚀 启动LangChain流水线系统")
    
    # 创建流水线控制器
    controller = PipelineController("config.ini")
    
    # 准备输入数据（字典格式）
    initial_input = {
        "text": "",
        # "image": "/Users/macbook/Documents/19293.jpeg"
    }
    
    # 在输入时就进行编码
    encoded_input = encode_input_files(initial_input)
    
    # 执行流水线
    print("\n开始执行流水线...")
    print(f"文本输入: {encoded_input['text']}")
    if 'image' in encoded_input:
        print(f"图片输入: [已编码，大小: {len(encoded_input['image'])} 字符]")
    if 'video' in encoded_input:
        print(f"视频输入: [已编码，大小: {len(encoded_input['video'])} 字符]")
    
    results = controller.execute_pipeline(encoded_input)
    
    # 打印流水线状态
    controller.print_pipeline_status()
    
    # 保存输出
    print("\n保存输出...")
    controller.save_pipeline_outputs(results, "outputs")
    
    print("\n🎉 流水线执行完成！")
    return results

def encode_input_files(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """编码输入文件为base64"""
    import base64
    import os
    
    encoded_dict = {}
    
    # 复制文本
    if 'text' in input_dict:
        encoded_dict['text'] = input_dict['text']
    
    # 编码图片
    if 'image' in input_dict:
        image_path = input_dict['image']
        if os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                encoded_dict['image'] = image_data
                print(f"✅ 图片编码成功: {image_path}")
            except Exception as e:
                print(f"❌ 图片编码失败: {e}")
        else:
            print(f"⚠️ 图片文件不存在: {image_path}")
    
    # 编码视频
    if 'video' in input_dict:
        video_path = input_dict['video']
        if os.path.exists(video_path):
            try:
                with open(video_path, 'rb') as f:
                    video_data = base64.b64encode(f.read()).decode('utf-8')
                encoded_dict['video'] = video_data
                print(f"✅ 视频编码成功: {video_path}")
            except Exception as e:
                print(f"❌ 视频编码失败: {e}")
        else:
            print(f"⚠️ 视频文件不存在: {video_path}")
    
    return encoded_dict

def test_memory_placeholders():
    """测试memory占位符功能"""
    print("\n=== 测试Memory占位符功能 ===\n")
    
    controller = PipelineController("config.ini")
    
    # 手动设置一些测试数据
    controller.memory.set_variable('description', '可爱的吉卜力风格头像')
    controller.memory.store_round_output('test_round', [
        {'type': 'text', 'text': '这是测试文本'},
        {'type': 'image', 'image_type': 'png', 'base64_data': 'test_data'}
    ])
    
    # 测试占位符解析
    test_prompts = [
        "描述是{description}",
        "第一轮输出: {test_round.output[0].text}",
        "图片类型: {test_round.output[1].image_type}",
        "变量: {description}"
    ]
    
    print("占位符解析测试:")
    for prompt in test_prompts:
        resolved = controller.memory.resolve_placeholders(prompt)
        print(f"  原始: {prompt}")
        print(f"  解析: {resolved}")
        print()
    
    controller.memory.print_memory_status()

if __name__ == "__main__":
    # 运行主流水线
    main()
    
    # 可选：测试memory占位符功能
    # test_memory_placeholders() 