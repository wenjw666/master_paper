"""
第4章训练可视化工具
生成强化学习训练相关的图表
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Dict

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def plot_training_curves(episodes: List[int],
                        rewards: Dict[str, List[float]],
                        output_path: str = None):
    """
    绘制训练曲线（图4-6）
    
    Args:
        episodes: 训练轮数列表
        rewards: 奖励字典 {
            'pure_position': [...],
            'impedance': [...],
            'ddpg': [...],
            'sac': [...]
        }
        output_path: 输出路径
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    ax.plot(episodes, rewards['pure_position'], 'k-', linewidth=2,
           label='纯位置控制', alpha=0.6)
    ax.plot(episodes, rewards['impedance'], 'b--', linewidth=2,
           label='传统阻抗控制', alpha=0.7)
    ax.plot(episodes, rewards['ddpg'], 'g-.', linewidth=2,
           label='DDPG算法', alpha=0.7)
    ax.plot(episodes, rewards['sac'], 'r-', linewidth=3,
           label='本文SAC算法', alpha=0.9)
    
    ax.set_xlabel('训练轮数 (Episodes)', fontsize=12)
    ax.set_ylabel('平均奖励', fontsize=12)
    ax.set_title('不同算法的平均奖励收敛曲线对比', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"训练曲线图已保存: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_force_history(force_history: List[np.ndarray],
                      timestamps: List[float],
                      output_path: str = None):
    """
    绘制装配过程中的力历史（图4-8）
    
    Args:
        force_history: 力历史列表，每个元素为(6,)数组
        timestamps: 时间戳列表
        output_path: 输出路径
    """
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    forces = np.array(force_history)
    time = np.array(timestamps)
    
    # 力分量
    ax1 = axes[0]
    ax1.plot(time, forces[:, 0], label='Fx', linewidth=2, alpha=0.8)
    ax1.plot(time, forces[:, 1], label='Fy', linewidth=2, alpha=0.8)
    ax1.plot(time, forces[:, 2], label='Fz', linewidth=2.5, alpha=0.9)
    ax1.axhline(y=10, color='orange', linestyle='--', linewidth=2, label='安全阈值 (10N)')
    ax1.axhline(y=30, color='red', linestyle='--', linewidth=2, label='急停阈值 (30N)')
    ax1.set_xlabel('时间 (s)', fontsize=12)
    ax1.set_ylabel('接触力 (N)', fontsize=12)
    ax1.set_title('装配全过程的接触力信号变化曲线', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 标注阶段
    if len(time) > 0:
        # 阶段I: 接近
        ax1.axvspan(time[0], time[len(time)//3], alpha=0.2, color='green', label='阶段I: 接近')
        # 阶段II: 接触/搜孔
        ax1.axvspan(time[len(time)//3], time[2*len(time)//3], alpha=0.2, color='yellow', label='阶段II: 接触/搜孔')
        # 阶段III: 插入
        ax1.axvspan(time[2*len(time)//3], time[-1], alpha=0.2, color='blue', label='阶段III: 插入')
    
    # 力矩分量
    ax2 = axes[1]
    ax2.plot(time, forces[:, 3], label='Mx', linewidth=2, alpha=0.8)
    ax2.plot(time, forces[:, 4], label='My', linewidth=2.5, alpha=0.9)
    ax2.plot(time, forces[:, 5], label='Mz', linewidth=2, alpha=0.8)
    ax2.set_xlabel('时间 (s)', fontsize=12)
    ax2.set_ylabel('接触力矩 (Nm)', fontsize=12)
    ax2.set_title('装配全过程的接触力矩信号变化曲线', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"力历史图已保存: {output_path}")
    else:
        plt.show()
    
    plt.close()

