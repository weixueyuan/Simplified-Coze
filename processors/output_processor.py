#!/usr/bin/env python3
"""
输出处理器模块
处理流水线输出，支持多种输出方式
"""

from typing import Dict, Any, List
from pathlib import Path
from utils import save_image, save_json, save_text
from utils.log_config import get_logger

class FileOutputProcessor:
    """文件输出处理器"""
    
    def __init__(self):
        self.logger = get_logger('pipeline.output_processor')
    
    def process(self, results: List[Dict[str, Any]], output_dir: str = "outputs", filename: str = "default", save_mode: str = "rounds", **kwargs):
        """
        保存到文件，支持两种文件结构：
        
        Mode 1 (combined): 默认模式
        outputs/
        ├── {filename}/
        │   ├── images/
        │   │   ├── {filename}_1.png
        │   │   ├── {filename}_2.png
        │   │   └── ...
        │   ├── videos/
        │   │   ├── {filename}_1.mp4
        │   │   ├── {filename}_2.mp4
        │   │   └── ...
        │   └── output.jsonl  (每行一个JSON对象，只包含text内容)
        
        Mode 2 (rounds): 按轮次分组
        outputs/
        ├── round1/
        │   ├── images/
        │   │   └── {filename}.png
        │   ├── videos/
        │   │   └── {filename}.mp4
        │   └── output.json
        ├── round2/
        │   ├── images/
        │   │   └── {filename}.png
        │   └── output.json
        ├── round3/
        │   └── output.json
        └── summary.jsonl  (所有轮次的汇总)
        
        Args:
            results: 流水线执行结果
            output_dir: 输出目录
            filename: 文件名前缀，用于组织文件结构
            save_mode: 保存模式 ("combined" 或 "rounds")
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"保存流水线输出到: {output_path} (模式: {save_mode})")
        
        if save_mode == "filename":
            # 创建filename目录
            filename_dir = output_path / filename
            filename_dir.mkdir(exist_ok=True)
            self._save_combined(results, filename_dir, filename)            
        else:
            self._save_by_rounds(results, output_path, filename)

        
        self.logger.info("✅ 所有输出已保存完成")
    
    def _save_combined(self, results: List[Dict[str, Any]], filename_dir: Path, filename: str):
        """默认的合并保存模式"""
        # 创建images和videos子目录
        images_dir = filename_dir / "images"
        videos_dir = filename_dir / "videos"
        images_dir.mkdir(exist_ok=True)
        videos_dir.mkdir(exist_ok=True)
        
        # 处理每轮输出并创建简化的结果
        simplified_results = []
        for result in results:
            round_num = result["round"]
            output = result["output"]
            
            # 保存图片内容
            if output.get("image"):
                image_file = images_dir / f"{filename}_{round_num}.png"
                if save_image(output["image"], str(image_file)):
                    self.logger.info(f"保存图片: {image_file}")
                else:
                    self.logger.error(f"保存图片失败: {image_file}")
            
            # 保存视频内容
            if output.get("video"):
                video_file = videos_dir / f"{filename}_{round_num}.mp4"
                if save_image(output["video"], str(video_file)):  # 视频也用save_image，因为都是base64
                    self.logger.info(f"保存视频: {video_file}")
                else:
                    self.logger.error(f"保存视频失败: {video_file}")
            
            # 创建简化的result，只保留text内容，去掉base64数据
            simplified_result = {
                "filename": filename,
                "round": result["round"],
                "config": result["config"],
                "status": result["status"],
                "output": {
                    "text": output.get("text", ""),
                    "has_image": bool(output.get("image")),
                    "has_video": bool(output.get("video"))
                }
            }
            simplified_results.append(simplified_result)
        
        # 保存JSONL格式文件，每行一个JSON对象（只包含文本内容）
        output_jsonl = filename_dir / "output.jsonl"
        if save_json(simplified_results, str(output_jsonl), format="jsonl"):
            self.logger.info(f"保存输出JSONL: {output_jsonl}")
        else:
            self.logger.error(f"保存JSONL失败: {output_jsonl}")
    
    def _save_by_rounds(self, results: List[Dict[str, Any]], output_path: Path, filename: str):
        """按轮次分组的保存模式 - 直接在outputs下创建round1, round2等目录"""
        simplified_results = []
        
        for result in results:
            round_num = result["round"]
            output = result["output"]
            
            # 创建轮次目录（直接在outputs下）
            round_dir = output_path / f"round{round_num}"
            round_dir.mkdir(exist_ok=True)
            
            # 创建images和videos子目录
            images_dir = round_dir / "images"
            videos_dir = round_dir / "videos"
            
            # 保存图片内容
            if output.get("image"):
                images_dir.mkdir(exist_ok=True)
                image_file = images_dir / f"{filename}.png"
                if save_image(output["image"], str(image_file)):
                    self.logger.info(f"保存图片: {image_file}")
                else:
                    self.logger.error(f"保存图片失败: {image_file}")
            
            # 保存视频内容
            if output.get("video"):
                videos_dir.mkdir(exist_ok=True)
                video_file = videos_dir / f"{filename}.mp4"
                if save_image(output["video"], str(video_file)):
                    self.logger.info(f"保存视频: {video_file}")
                else:
                    self.logger.error(f"保存视频失败: {video_file}")
            
            # 保存当前轮次的JSON文件
            round_result = {
                "filename": filename,
                "round": result["round"],
                "config": result["config"],
                "status": result["status"],
                "output": {
                    "text": output.get("text", ""),
                    "has_image": bool(output.get("image")),
                    "has_video": bool(output.get("video"))
                }
            }
            
            round_json = round_dir / "output.json"
            if save_json(round_result, str(round_json), format="json"):
                self.logger.info(f"保存轮次JSON: {round_json}")
            else:
                self.logger.error(f"保存轮次JSON失败: {round_json}")
            
            simplified_results.append(round_result)
        
        # 保存汇总JSONL文件（在outputs根目录下）
        summary_jsonl = output_path / "summary.jsonl"
        if save_json(simplified_results, str(summary_jsonl), format="jsonl"):
            self.logger.info(f"保存汇总JSONL: {summary_jsonl}")
        else:
            self.logger.error(f"保存汇总JSONL失败: {summary_jsonl}")

class ConsoleOutputProcessor:
    """控制台输出处理器"""
    
    def __init__(self):
        self.logger = get_logger('pipeline.console_output')
    
    def process(self, results: List[Dict[str, Any]], **kwargs):
        """
        打印到控制台
        
        Args:
            results: 流水线执行结果
        """
        self.logger.info("=== 流水线执行结果 ===")
        for result in results:
            self.logger.info(f"第{result['round']}轮 ({result['config']}):")
            if result['status'] == 'success':
                self.logger.info(f"  状态: {result['status']}")
            else:
                self.logger.error(f"  状态: {result['status']}")
            if result["output"].get("text"):
                self.logger.info(f"文本: {result['output']['text']}")
            if result["output"].get("image"):
                self.logger.info("图片: [已生成]")
            if result["output"].get("video"):
                self.logger.info("视频: [已生成]")


