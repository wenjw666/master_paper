"""
第3章可视化工具
生成抓取规划相关的图表
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import open3d as o3d
from typing import List, Dict

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def visualize_grasp_poses(pointcloud: o3d.geometry.PointCloud,
                          grasps: List[Dict],
                          top_k: int = 10,
                          output_path: str = None):
    """
    可视化抓取位姿（图3-3）
    
    Args:
        pointcloud: 点云
        grasps: 抓取位姿列表
        top_k: 显示前k个
        output_path: 输出路径
    """
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # 绘制点云
    points = np.asarray(pointcloud.points)
    colors = np.asarray(pointcloud.colors) if pointcloud.has_colors() else None
    
    if colors is not None:
        ax.scatter(points[:, 0], points[:, 1], points[:, 2],
                  c=colors, s=1, alpha=0.5)
    else:
        ax.scatter(points[:, 0], points[:, 1], points[:, 2],
                  c='gray', s=1, alpha=0.5)
    
    # 绘制抓取位姿（前top_k个）
    sorted_grasps = sorted(grasps, key=lambda x: x.get('score', 0), reverse=True)[:top_k]
    
    for i, grasp in enumerate(sorted_grasps):
        t = grasp['translation']
        R = grasp['rotation']
        score = grasp.get('score', 0)
        
        # 抓取方向（Z轴）
        direction = R[:, 2] * 0.05  # 5cm箭头
        
        # 绘制箭头
        ax.quiver(t[0], t[1], t[2],
                 direction[0], direction[1], direction[2],
                 color=plt.cm.viridis(score), length=0.05,
                 arrow_length_ratio=0.3, linewidth=2, alpha=0.8)
    
    ax.set_xlabel('X (m)', fontsize=11)
    ax.set_ylabel('Y (m)', fontsize=11)
    ax.set_zlabel('Z (m)', fontsize=11)
    ax.set_title('电连接器表面的候选抓取位姿分布', fontsize=14, fontweight='bold')
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"抓取位姿可视化已保存: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_planning_comparison(data: Dict, output_path: str = None):
    """
    绘制规划算法对比图（图3-8）
    
    Args:
        data: 数据字典 {
            'obstacle_density': [...],
            'baseline': {'time': [...], 'path_length': [...], 'success': [...]},
            'method_a': {...},
            'ours': {...}
        }
        output_path: 输出路径
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    density = data['obstacle_density']
    baseline = data['baseline']
    method_a = data.get('method_a', {})
    ours = data['ours']
    
    # 规划时间
    ax1 = axes[0]
    ax1.plot(density, baseline['time'], 'b--o', linewidth=2, markersize=8,
            label='Baseline', alpha=0.7)
    if method_a:
        ax1.plot(density, method_a['time'], 'g-.s', linewidth=2, markersize=8,
                label='Method-A', alpha=0.7)
    ax1.plot(density, ours['time'], 'r-^', linewidth=2.5, markersize=8,
            label='Ours (GRRT-Connect)', alpha=0.9)
    ax1.set_xlabel('障碍物密度', fontsize=11)
    ax1.set_ylabel('规划时间 (s)', fontsize=11)
    ax1.set_title('规划时间对比', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 路径长度
    ax2 = axes[1]
    ax2.plot(density, baseline['path_length'], 'b--o', linewidth=2, markersize=8,
            label='Baseline', alpha=0.7)
    if method_a:
        ax2.plot(density, method_a['path_length'], 'g-.s', linewidth=2, markersize=8,
                label='Method-A', alpha=0.7)
    ax2.plot(density, ours['path_length'], 'r-^', linewidth=2.5, markersize=8,
            label='Ours', alpha=0.9)
    ax2.set_xlabel('障碍物密度', fontsize=11)
    ax2.set_ylabel('路径长度', fontsize=11)
    ax2.set_title('路径长度对比', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 抓取成功率
    ax3 = axes[2]
    ax3.plot(density, baseline['success'], 'b--o', linewidth=2, markersize=8,
            label='Baseline', alpha=0.7)
    if method_a:
        ax3.plot(density, method_a['success'], 'g-.s', linewidth=2, markersize=8,
                label='Method-A', alpha=0.7)
    ax3.plot(density, ours['success'], 'r-^', linewidth=2.5, markersize=8,
            label='Ours', alpha=0.9)
    ax3.set_xlabel('障碍物密度', fontsize=11)
    ax3.set_ylabel('抓取成功率', fontsize=11)
    ax3.set_title('抓取成功率对比', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.set_ylim([0, 1.05])
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"规划对比图已保存: {output_path}")
    else:
        plt.show()
    
    plt.close()

