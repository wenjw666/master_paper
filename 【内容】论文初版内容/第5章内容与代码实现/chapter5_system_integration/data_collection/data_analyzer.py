"""
实验数据分析工具
从ROS Bag中提取和分析数据
"""

import rosbag
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
from typing import Dict, List
import yaml


class DataAnalyzer:
    """数据分析器"""
    
    def __init__(self, bag_file: str):
        """
        初始化分析器
        
        Args:
            bag_file: ROS Bag文件路径
        """
        self.bag_file = bag_file
        self.bag = rosbag.Bag(bag_file, 'r')
    
    def extract_force_data(self) -> pd.DataFrame:
        """
        提取力传感器数据
        
        Returns:
            力/力矩数据DataFrame
        """
        force_data = []
        
        for topic, msg, t in self.bag.read_messages(topics=['/ft_sensor/raw']):
            timestamp = t.to_sec()
            
            # 提取力/力矩
            force_data.append({
                'timestamp': timestamp,
                'fx': msg.wrench.force.x,
                'fy': msg.wrench.force.y,
                'fz': msg.wrench.force.z,
                'mx': msg.wrench.torque.x,
                'my': msg.wrench.torque.y,
                'mz': msg.wrench.torque.z
            })
        
        df = pd.DataFrame(force_data)
        return df
    
    def extract_pose_data(self) -> pd.DataFrame:
        """
        提取位姿数据
        
        Returns:
            位姿数据DataFrame
        """
        pose_data = []
        
        for topic, msg, t in self.bag.read_messages(topics=['/connector/pose']):
            timestamp = t.to_sec()
            
            pose_data.append({
                'timestamp': timestamp,
                'x': msg.pose.position.x,
                'y': msg.pose.position.y,
                'z': msg.pose.position.z,
                'qx': msg.pose.orientation.x,
                'qy': msg.pose.orientation.y,
                'qz': msg.pose.orientation.z,
                'qw': msg.pose.orientation.w
            })
        
        df = pd.DataFrame(pose_data)
        return df
    
    def analyze_assembly_force(self, output_dir: str):
        """
        分析装配过程中的力曲线
        
        Args:
            output_dir: 输出目录
        """
        df_force = self.extract_force_data()
        
        if len(df_force) == 0:
            print("警告: 未找到力传感器数据")
            return
        
        # 计算力大小
        df_force['force_magnitude'] = np.sqrt(
            df_force['fx']**2 + df_force['fy']**2 + df_force['fz']**2
        )
        
        # 计算力矩大小
        df_force['torque_magnitude'] = np.sqrt(
            df_force['mx']**2 + df_force['my']**2 + df_force['mz']**2
        )
        
        # 绘制力曲线
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        # 力分量
        axes[0].plot(df_force['timestamp'], df_force['fx'], label='Fx')
        axes[0].plot(df_force['timestamp'], df_force['fy'], label='Fy')
        axes[0].plot(df_force['timestamp'], df_force['fz'], label='Fz')
        axes[0].set_xlabel('时间 (s)')
        axes[0].set_ylabel('力 (N)')
        axes[0].set_title('接触力分量')
        axes[0].legend()
        axes[0].grid(True)
        
        # 力大小
        axes[1].plot(df_force['timestamp'], df_force['force_magnitude'], 'r-', linewidth=2)
        axes[1].axhline(y=10, color='g', linestyle='--', label='安全阈值 (10N)')
        axes[1].axhline(y=30, color='r', linestyle='--', label='急停阈值 (30N)')
        axes[1].set_xlabel('时间 (s)')
        axes[1].set_ylabel('力大小 (N)')
        axes[1].set_title('接触力大小')
        axes[1].legend()
        axes[1].grid(True)
        
        # 力矩
        axes[2].plot(df_force['timestamp'], df_force['mx'], label='Mx')
        axes[2].plot(df_force['timestamp'], df_force['my'], label='My')
        axes[2].plot(df_force['timestamp'], df_force['mz'], label='Mz')
        axes[2].set_xlabel('时间 (s)')
        axes[2].set_ylabel('力矩 (Nm)')
        axes[2].set_title('接触力矩')
        axes[2].legend()
        axes[2].grid(True)
        
        plt.tight_layout()
        
        # 保存图像
        output_path = os.path.join(output_dir, 'force_analysis.png')
        plt.savefig(output_path, dpi=300)
        print(f"力曲线图已保存: {output_path}")
        
        # 统计信息
        stats = {
            'max_force': float(df_force['force_magnitude'].max()),
            'mean_force': float(df_force['force_magnitude'].mean()),
            'force_variance': float(df_force['force_magnitude'].var()),
            'max_torque': float(df_force['torque_magnitude'].max())
        }
        
        return stats
    
    def generate_report(self, output_dir: str):
        """
        生成分析报告
        
        Args:
            output_dir: 输出目录
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # 分析力数据
        force_stats = self.analyze_assembly_force(output_dir)
        
        # 生成报告
        report = {
            'bag_file': self.bag_file,
            'analysis_time': str(pd.Timestamp.now()),
            'force_statistics': force_stats
        }
        
        # 保存报告
        report_path = os.path.join(output_dir, 'analysis_report.yaml')
        with open(report_path, 'w') as f:
            yaml.dump(report, f, default_flow_style=False)
        
        print(f"分析报告已保存: {report_path}")
    
    def __del__(self):
        """析构函数"""
        if hasattr(self, 'bag'):
            self.bag.close()


def main():
    parser = argparse.ArgumentParser(description='ROS Bag数据分析工具')
    parser.add_argument('--bag-file', type=str, required=True,
                       help='Bag文件路径')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='输出目录')
    
    args = parser.parse_args()
    
    analyzer = DataAnalyzer(args.bag_file)
    analyzer.generate_report(args.output_dir)


if __name__ == '__main__':
    main()

