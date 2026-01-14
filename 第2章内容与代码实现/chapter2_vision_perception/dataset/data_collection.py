"""
RealSense D435i 数据采集脚本
用于采集航空电连接器的RGB-D图像数据
"""

import pyrealsense2 as rs
import numpy as np
import cv2
import os
import argparse
from datetime import datetime
import json
from pathlib import Path


class RealSenseCollector:
    """RealSense D435i 数据采集器"""
    
    def __init__(self, width=1920, height=1080, fps=30):
        """
        初始化RealSense采集器
        
        Args:
            width: RGB图像宽度
            height: RGB图像高度
            fps: 帧率
        """
        self.width = width
        self.height = height
        self.fps = fps
        
        # 配置深度和颜色流
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        
        # 启用流
        self.config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
        self.config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
        
        # 启动管道
        self.profile = self.pipeline.start(self.config)
        
        # 获取深度传感器和深度缩放单元
        depth_sensor = self.profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()
        
        print(f"RealSense相机初始化完成")
        print(f"深度缩放: {self.depth_scale}")
        
    def collect_frame(self):
        """采集一帧RGB-D数据"""
        frames = self.pipeline.wait_for_frames()
        
        # 对齐深度帧到颜色帧
        align_to = rs.align(rs.stream.color)
        aligned_frames = align_to.process(frames)
        
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        
        if not aligned_depth_frame or not color_frame:
            return None, None
        
        # 转换为numpy数组
        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        
        return color_image, depth_image
    
    def save_frame(self, color_image, depth_image, save_dir, frame_id):
        """
        保存RGB-D图像对
        
        Args:
            color_image: RGB图像
            depth_image: 深度图像
            save_dir: 保存目录
            frame_id: 帧ID
        """
        # 创建目录
        os.makedirs(os.path.join(save_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(save_dir, "depth"), exist_ok=True)
        
        # 保存RGB图像
        rgb_path = os.path.join(save_dir, "images", f"frame_{frame_id:06d}.jpg")
        cv2.imwrite(rgb_path, color_image)
        
        # 保存深度图像（16位PNG）
        depth_path = os.path.join(save_dir, "depth", f"frame_{frame_id:06d}.png")
        cv2.imwrite(depth_path, depth_image)
        
        return rgb_path, depth_path
    
    def collect_dataset(self, output_dir, num_images, save_metadata=True):
        """
        采集数据集
        
        Args:
            output_dir: 输出目录
            num_images: 采集图像数量
            save_metadata: 是否保存元数据
        """
        os.makedirs(output_dir, exist_ok=True)
        
        metadata = {
            "collection_time": datetime.now().isoformat(),
            "num_images": num_images,
            "resolution": f"{self.width}x{self.height}",
            "fps": self.fps,
            "depth_scale": self.depth_scale,
            "frames": []
        }
        
        print(f"开始采集 {num_images} 张图像...")
        print("按 's' 保存当前帧，按 'q' 退出")
        
        frame_id = 0
        cv2.namedWindow('RealSense采集', cv2.WINDOW_AUTOSIZE)
        
        try:
            while frame_id < num_images:
                color_image, depth_image = self.collect_frame()
                
                if color_image is None:
                    continue
                
                # 显示图像
                display_image = color_image.copy()
                cv2.putText(display_image, f"Frame: {frame_id}/{num_images}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow('RealSense采集', display_image)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('s'):
                    # 保存当前帧
                    rgb_path, depth_path = self.save_frame(
                        color_image, depth_image, output_dir, frame_id
                    )
                    
                    frame_info = {
                        "frame_id": frame_id,
                        "rgb_path": rgb_path,
                        "depth_path": depth_path,
                        "timestamp": datetime.now().isoformat()
                    }
                    metadata["frames"].append(frame_info)
                    
                    frame_id += 1
                    print(f"已保存: {frame_id}/{num_images}")
                    
                elif key == ord('q'):
                    print("用户中断采集")
                    break
                    
        except KeyboardInterrupt:
            print("\n采集中断")
        finally:
            self.pipeline.stop()
            cv2.destroyAllWindows()
            
            # 保存元数据
            if save_metadata:
                metadata_path = os.path.join(output_dir, "metadata.json")
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                print(f"元数据已保存: {metadata_path}")
            
            print(f"采集完成，共保存 {frame_id} 张图像")
    
    def __del__(self):
        """析构函数"""
        try:
            self.pipeline.stop()
        except:
            pass


def main():
    parser = argparse.ArgumentParser(description='RealSense D435i 数据采集')
    parser.add_argument('--output_dir', type=str, default='./data/real',
                       help='输出目录')
    parser.add_argument('--num_images', type=int, default=2500,
                       help='采集图像数量')
    parser.add_argument('--width', type=int, default=1920,
                       help='RGB图像宽度')
    parser.add_argument('--height', type=int, default=1080,
                       help='RGB图像高度')
    parser.add_argument('--fps', type=int, default=30,
                       help='帧率')
    
    args = parser.parse_args()
    
    # 创建采集器
    collector = RealSenseCollector(
        width=args.width,
        height=args.height,
        fps=args.fps
    )
    
    # 开始采集
    collector.collect_dataset(
        output_dir=args.output_dir,
        num_images=args.num_images
    )


if __name__ == '__main__':
    main()

