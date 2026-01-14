"""
实验结果可视化工具
生成论文所需的图表
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import seaborn as sns

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置图表样式
sns.set_style("whitegrid")
sns.set_palette("husl")


class ExperimentVisualizer:
    """实验可视化工具类"""
    
    def __init__(self, figsize=(12, 8), dpi=300):
        """
        初始化可视化器
        
        Args:
            figsize: 图像尺寸
            dpi: 分辨率
        """
        self.figsize = figsize
        self.dpi = dpi
    
    def plot_force_curves_comparison(self, 
                                     data_baseline1: Dict,
                                     data_baseline2: Dict,
                                     data_ours: Dict,
                                     output_path: str):
        """
        绘制力曲线对比图（图5-4）
        
        三种控制策略的装配力/力矩曲线对比
        
        Args:
            data_baseline1: Baseline 1数据 {'time': [...], 'force_z': [...], 'moment_y': [...]}
            data_baseline2: Baseline 2数据
            data_ours: Ours数据
            output_path: 输出路径
        """
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # 绘制Z轴接触力
        ax1 = axes[0]
        ax1.plot(data_baseline1['time'], data_baseline1['force_z'], 
                'b--', linewidth=2, label='Baseline 1 (传统阻抗控制)', alpha=0.7)
        ax1.plot(data_baseline2['time'], data_baseline2['force_z'], 
                'g-.', linewidth=2, label='Baseline 2 (SAC无前馈)', alpha=0.7)
        ax1.plot(data_ours['time'], data_ours['force_z'], 
                'r-', linewidth=2.5, label='Ours (SAC+视觉前馈)', alpha=0.9)
        
        # 标注关键点
        ax1.axhline(y=10, color='orange', linestyle=':', linewidth=1.5, label='安全阈值 (10N)')
        ax1.axhline(y=30, color='red', linestyle=':', linewidth=1.5, label='急停阈值 (30N)')
        
        # 标注接触时刻
        if 'contact_time' in data_ours:
            ax1.axvline(x=data_ours['contact_time'], color='gray', 
                       linestyle='--', linewidth=1, alpha=0.5)
            ax1.text(data_ours['contact_time'], ax1.get_ylim()[1]*0.9, 
                    '接触时刻', rotation=90, ha='right', va='top')
        
        ax1.set_xlabel('时间 (s)', fontsize=12)
        ax1.set_ylabel('Z轴接触力 (N)', fontsize=12)
        ax1.set_title('装配过程中的Z轴接触力对比', fontsize=14, fontweight='bold')
        ax1.legend(loc='upper right', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # 绘制Y轴力矩
        ax2 = axes[1]
        ax2.plot(data_baseline1['time'], data_baseline1['moment_y'], 
                'b--', linewidth=2, label='Baseline 1', alpha=0.7)
        ax2.plot(data_baseline2['time'], data_baseline2['moment_y'], 
                'g-.', linewidth=2, label='Baseline 2', alpha=0.7)
        ax2.plot(data_ours['time'], data_ours['moment_y'], 
                'r-', linewidth=2.5, label='Ours', alpha=0.9)
        
        # 标注前馈介入时刻
        if 'feedforward_time' in data_ours:
            ax2.axvline(x=data_ours['feedforward_time'], color='purple', 
                       linestyle='--', linewidth=1, alpha=0.5)
            ax2.text(data_ours['feedforward_time'], ax2.get_ylim()[1]*0.9, 
                    '前馈介入', rotation=90, ha='right', va='top')
        
        ax2.set_xlabel('时间 (s)', fontsize=12)
        ax2.set_ylabel('Y轴力矩 (Nm)', fontsize=12)
        ax2.set_title('装配过程中的Y轴力矩对比', fontsize=14, fontweight='bold')
        ax2.legend(loc='upper right', fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        print(f"力曲线对比图已保存: {output_path}")
        plt.close()
    
    def plot_success_rate_comparison(self,
                                     data: Dict,
                                     output_path: str):
        """
        绘制成功率对比图
        
        Args:
            data: 数据字典 {
                'methods': ['Baseline 1', 'Baseline 2', 'Ours'],
                'success_rates': [0.10, 0.65, 1.0],
                'avg_times': [None, 15.2, 8.2],
                'max_forces': [32.4, 16.8, 6.5]
            }
            output_path: 输出路径
        """
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        methods = data['methods']
        success_rates = data['success_rates']
        avg_times = data.get('avg_times', [None] * len(methods))
        max_forces = data.get('max_forces', [None] * len(methods))
        
        # 成功率柱状图
        ax1 = axes[0]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        bars = ax1.bar(methods, success_rates, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        ax1.set_ylabel('成功率', fontsize=12)
        ax1.set_title('装配成功率对比', fontsize=14, fontweight='bold')
        ax1.set_ylim([0, 1.1])
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标签
        for i, (bar, rate) in enumerate(zip(bars, success_rates)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{rate*100:.0f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # 平均耗时对比
        ax2 = axes[1]
        valid_times = [(t if t is not None else 0) for t in avg_times]
        bars2 = ax2.bar(methods, valid_times, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        ax2.set_ylabel('平均耗时 (s)', fontsize=12)
        ax2.set_title('平均装配耗时对比', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        for i, (bar, time) in enumerate(zip(bars2, avg_times)):
            if time is not None:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{time:.1f}s', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # 最大接触力对比
        ax3 = axes[2]
        valid_forces = [(f if f is not None else 0) for f in max_forces]
        bars3 = ax3.bar(methods, valid_forces, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        ax3.axhline(y=10, color='orange', linestyle='--', linewidth=2, label='安全阈值')
        ax3.axhline(y=30, color='red', linestyle='--', linewidth=2, label='急停阈值')
        ax3.set_ylabel('最大接触力 (N)', fontsize=12)
        ax3.set_title('最大接触力对比', fontsize=14, fontweight='bold')
        ax3.legend(loc='upper right', fontsize=9)
        ax3.grid(True, alpha=0.3, axis='y')
        
        for i, (bar, force) in enumerate(zip(bars3, max_forces)):
            if force is not None:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{force:.1f}N', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        print(f"成功率对比图已保存: {output_path}")
        plt.close()
    
    def plot_system_architecture(self, output_path: str):
        """
        绘制系统架构图（图5-2）
        
        ROS节点与数据流向图
        
        Args:
            output_path: 输出路径
        """
        fig, ax = plt.subplots(figsize=(16, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # 定义节点位置和大小
        nodes = {
            'camera': {'pos': (1, 8), 'size': (1.5, 0.8), 'label': 'RealSense\nD435i', 'color': '#FFE66D'},
            'vision': {'pos': (3, 8), 'size': (1.5, 0.8), 'label': 'Vision Node\n(Ch2)', 'color': '#95E1D3'},
            'planning': {'pos': (5.5, 8), 'size': (1.5, 0.8), 'label': 'Planning Node\n(Ch3)', 'color': '#F38181'},
            'control': {'pos': (8, 8), 'size': (1.5, 0.8), 'label': 'Control Node\n(Ch4)', 'color': '#AA96DA'},
            'state_mgr': {'pos': (5.5, 6), 'size': (1.5, 0.8), 'label': 'State Manager\n(SMACH)', 'color': '#FCBAD3'},
            'robot': {'pos': (8, 4), 'size': (1.5, 0.8), 'label': 'UR5e\nRobot', 'color': '#C7CEEA'},
            'ft_sensor': {'pos': (8, 2), 'size': (1.5, 0.8), 'label': 'ATI Gamma\nF/T Sensor', 'color': '#FFB6C1'},
        }
        
        # 绘制节点
        for name, node in nodes.items():
            x, y = node['pos']
            w, h = node['size']
            rect = FancyBboxPatch((x-w/2, y-h/2), w, h,
                                 boxstyle="round,pad=0.1",
                                 facecolor=node['color'],
                                 edgecolor='black',
                                 linewidth=2)
            ax.add_patch(rect)
            ax.text(x, y, node['label'], ha='center', va='center',
                   fontsize=10, fontweight='bold')
        
        # 绘制数据流箭头
        arrows = [
            # 相机到视觉节点
            ((1.75, 8), (2.25, 8), '/camera/color/image_raw\n/camera/aligned_depth_to_color'),
            # 视觉节点到规划节点
            ((4.5, 8), (4.75, 8), '/connector/pose\n/cable/vector'),
            # 规划节点到控制节点
            ((7, 8), (7.25, 8), '/joint_trajectory'),
            # 视觉节点到控制节点（线缆向量）
            ((3.75, 7.5), (7.25, 7.5), '/cable/vector'),
            # 状态机连接
            ((5.5, 6.8), (5.5, 7.2), ''),
            ((4.5, 6), (5, 6), ''),
            ((7, 6), (7.5, 6), ''),
            # 控制节点到机器人
            ((8, 7.2), (8, 4.8), '/joint_group_vel_controller/command'),
            # 力传感器到控制节点
            ((8, 2.8), (8, 3.2), '/ft_sensor/raw'),
        ]
        
        for start, end, label in arrows:
            if label:
                arrow = FancyArrowPatch(start, end,
                                     arrowstyle='->', lw=2,
                                     color='#2C3E50', alpha=0.7)
                ax.add_patch(arrow)
                # 添加标签
                mid_x, mid_y = (start[0] + end[0])/2, (start[1] + end[1])/2
                ax.text(mid_x, mid_y - 0.2, label, ha='center', va='top',
                       fontsize=8, bbox=dict(boxstyle='round,pad=0.3',
                                            facecolor='white', alpha=0.8))
        
        # 添加标题
        ax.text(5, 9.5, '基于ROS的电连接器自主装配系统架构', 
               ha='center', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        print(f"系统架构图已保存: {output_path}")
        plt.close()
    
    def plot_state_machine_diagram(self, output_path: str):
        """
        绘制状态机流程图
        
        Args:
            output_path: 输出路径
        """
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # 定义状态
        states = {
            'IDLE': {'pos': (2, 8), 'color': '#E8F4F8'},
            'PERCEPTION': {'pos': (5, 8), 'color': '#95E1D3'},
            'APPROACH': {'pos': (8, 8), 'color': '#F38181'},
            'GRASP': {'pos': (8, 6), 'color': '#FCE38A'},
            'TRANSPORT': {'pos': (8, 4), 'color': '#AA96DA'},
            'ASSEMBLY': {'pos': (5, 4), 'color': '#FCBAD3'},
            'ERROR_RECOVERY': {'pos': (2, 5), 'color': '#FFB6C1'},
            'COMPLETE': {'pos': (2, 2), 'color': '#C7CEEA'},
        }
        
        # 绘制状态节点
        for name, state in states.items():
            x, y = state['pos']
            circle = plt.Circle((x, y), 0.4, color=state['color'],
                              edgecolor='black', linewidth=2)
            ax.add_patch(circle)
            ax.text(x, y, name, ha='center', va='center',
                   fontsize=9, fontweight='bold')
        
        # 绘制状态转换箭头
        transitions = [
            ('IDLE', 'PERCEPTION', 'start_assembly'),
            ('PERCEPTION', 'APPROACH', 'success'),
            ('APPROACH', 'GRASP', 'success'),
            ('GRASP', 'TRANSPORT', 'success'),
            ('TRANSPORT', 'ASSEMBLY', 'success'),
            ('ASSEMBLY', 'COMPLETE', 'success'),
            ('PERCEPTION', 'ERROR_RECOVERY', 'failed'),
            ('APPROACH', 'ERROR_RECOVERY', 'failed'),
            ('GRASP', 'ERROR_RECOVERY', 'failed'),
            ('ASSEMBLY', 'ERROR_RECOVERY', 'failed'),
            ('ERROR_RECOVERY', 'PERCEPTION', 'recovery_success'),
        ]
        
        for start, end, label in transitions:
            start_pos = states[start]['pos']
            end_pos = states[end]['pos']
            
            arrow = FancyArrowPatch(start_pos, end_pos,
                                   arrowstyle='->', lw=1.5,
                                   color='#2C3E50', alpha=0.6)
            ax.add_patch(arrow)
            
            # 添加标签
            mid_x, mid_y = (start_pos[0] + end_pos[0])/2, (start_pos[1] + end_pos[1])/2
            ax.text(mid_x, mid_y - 0.15, label, ha='center', va='top',
                   fontsize=7, style='italic')
        
        ax.text(5, 9.5, '电连接器装配状态机流程', 
               ha='center', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        print(f"状态机流程图已保存: {output_path}")
        plt.close()
    
    def plot_perception_planning_results(self,
                                        data: Dict,
                                        output_path: str):
        """
        绘制感知-规划联合实验结果（表5-1可视化）
        
        Args:
            data: 数据字典 {
                'occlusion_levels': ['轻度', '中度', '重度'],
                'baseline': {'recognition': [...], 'collision': [...], 'time': [...], 'success': [...]},
                'ours': {...}
            }
            output_path: 输出路径
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        levels = data['occlusion_levels']
        baseline = data['baseline']
        ours = data['ours']
        
        x = np.arange(len(levels))
        width = 0.35
        
        # 识别成功率
        ax1 = axes[0, 0]
        ax1.bar(x - width/2, baseline['recognition'], width, 
               label='Baseline', color='#FF6B6B', alpha=0.8)
        ax1.bar(x + width/2, ours['recognition'], width,
               label='Ours', color='#4ECDC4', alpha=0.8)
        ax1.set_ylabel('识别成功率', fontsize=11)
        ax1.set_title('识别成功率对比', fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(levels)
        ax1.legend()
        ax1.set_ylim([0, 1.1])
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 碰撞次数
        ax2 = axes[0, 1]
        ax2.bar(x - width/2, baseline['collision'], width,
               label='Baseline', color='#FF6B6B', alpha=0.8)
        ax2.bar(x + width/2, ours['collision'], width,
               label='Ours', color='#4ECDC4', alpha=0.8)
        ax2.set_ylabel('碰撞次数', fontsize=11)
        ax2.set_title('碰撞次数对比', fontsize=12, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(levels)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 规划耗时
        ax3 = axes[1, 0]
        ax3.bar(x - width/2, baseline['time'], width,
               label='Baseline', color='#FF6B6B', alpha=0.8)
        ax3.bar(x + width/2, ours['time'], width,
               label='Ours', color='#4ECDC4', alpha=0.8)
        ax3.set_ylabel('平均规划耗时 (s)', fontsize=11)
        ax3.set_title('规划耗时对比', fontsize=12, fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(levels)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 任务总成功率
        ax4 = axes[1, 1]
        ax4.bar(x - width/2, baseline['success'], width,
               label='Baseline', color='#FF6B6B', alpha=0.8)
        ax4.bar(x + width/2, ours['success'], width,
               label='Ours', color='#4ECDC4', alpha=0.8)
        ax4.set_ylabel('任务总成功率', fontsize=11)
        ax4.set_title('任务总成功率对比', fontsize=12, fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(levels)
        ax4.legend()
        ax4.set_ylim([0, 1.1])
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        print(f"感知-规划结果图已保存: {output_path}")
        plt.close()
    
    def plot_training_curves(self,
                            data: Dict,
                            output_path: str):
        """
        绘制训练曲线（图4-6）
        
        Args:
            data: 数据字典 {
                'episodes': [...],
                'pure_position': [...],
                'impedance': [...],
                'ddpg': [...],
                'sac': [...]
            }
            output_path: 输出路径
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        episodes = data['episodes']
        
        ax.plot(episodes, data['pure_position'], 'k-', linewidth=2,
               label='纯位置控制', alpha=0.6)
        ax.plot(episodes, data['impedance'], 'b--', linewidth=2,
               label='传统阻抗控制', alpha=0.7)
        ax.plot(episodes, data['ddpg'], 'g-.', linewidth=2,
               label='DDPG算法', alpha=0.7)
        ax.plot(episodes, data['sac'], 'r-', linewidth=3,
               label='本文SAC算法', alpha=0.9)
        
        ax.set_xlabel('训练轮数 (Episodes)', fontsize=12)
        ax.set_ylabel('平均奖励', fontsize=12)
        ax.set_title('不同算法的平均奖励收敛曲线对比', fontsize=14, fontweight='bold')
        ax.legend(loc='lower right', fontsize=11)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        print(f"训练曲线图已保存: {output_path}")
        plt.close()


def generate_example_plots():
    """生成示例图表（用于测试）"""
    visualizer = ExperimentVisualizer()
    
    # 示例数据：力曲线对比
    time = np.linspace(0, 5, 100)
    data_baseline1 = {
        'time': time,
        'force_z': np.concatenate([
            np.zeros(40),
            np.random.normal(35, 5, 10),  # 接触瞬间峰值
            np.zeros(50)
        ]),
        'moment_y': np.random.normal(0, 0.5, 100)
    }
    
    data_baseline2 = {
        'time': time,
        'force_z': np.concatenate([
            np.zeros(40),
            np.random.normal(18, 3, 20),  # 震荡
            np.random.normal(15, 2, 40)
        ]),
        'moment_y': np.random.normal(0.8, 0.3, 100)
    }
    
    data_ours = {
        'time': time,
        'force_z': np.concatenate([
            np.zeros(40),
            np.random.normal(6.5, 1, 60)  # 平滑过渡
        ]),
        'moment_y': np.concatenate([
            np.random.normal(-0.5, 0.1, 40),  # 前馈补偿
            np.random.normal(0, 0.2, 60)
        ]),
        'contact_time': 2.0,
        'feedforward_time': 0.0
    }
    
    visualizer.plot_force_curves_comparison(
        data_baseline1, data_baseline2, data_ours,
        './results/force_curves_comparison.png'
    )
    
    # 示例数据：成功率对比
    success_data = {
        'methods': ['Baseline 1\n(传统阻抗)', 'Baseline 2\n(SAC无前馈)', 'Ours\n(SAC+前馈)'],
        'success_rates': [0.10, 0.65, 1.0],
        'avg_times': [None, 15.2, 8.2],
        'max_forces': [32.4, 16.8, 6.5]
    }
    
    visualizer.plot_success_rate_comparison(
        success_data,
        './results/success_rate_comparison.png'
    )
    
    # 系统架构图
    visualizer.plot_system_architecture('./results/system_architecture.png')
    
    # 状态机流程图
    visualizer.plot_state_machine_diagram('./results/state_machine_diagram.png')
    
    # 感知-规划结果
    perception_data = {
        'occlusion_levels': ['轻度遮挡\n(<10%)', '中度遮挡\n(30%)', '重度遮挡\n(>50%)'],
        'baseline': {
            'recognition': [1.0, 0.85, 0.40],
            'collision': [2, 9, 17],
            'time': [2.15, 3.55, 8.64],
            'success': [0.90, 0.55, 0.15]
        },
        'ours': {
            'recognition': [1.0, 0.95, 0.90],
            'collision': [0, 0, 1],
            'time': [2.42, 3.28, 4.82],
            'success': [1.0, 0.95, 0.90]
        }
    }
    
    visualizer.plot_perception_planning_results(
        perception_data,
        './results/perception_planning_results.png'
    )
    
    # 训练曲线
    episodes = np.arange(0, 2000, 10)
    training_data = {
        'episodes': episodes,
        'pure_position': np.random.normal(10, 2, len(episodes)),
        'impedance': np.random.normal(15, 3, len(episodes)),
        'ddpg': 20 + 30 * (1 - np.exp(-episodes/500)) + np.random.normal(0, 2, len(episodes)),
        'sac': 25 + 40 * (1 - np.exp(-episodes/400)) + np.random.normal(0, 1.5, len(episodes))
    }
    
    visualizer.plot_training_curves(
        training_data,
        './results/training_curves.png'
    )
    
    print("\n所有示例图表已生成完成！")


if __name__ == '__main__':
    import os
    os.makedirs('./results', exist_ok=True)
    generate_example_plots()

