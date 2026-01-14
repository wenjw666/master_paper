"""
第2章可视化工具
生成视觉感知相关的图表
"""

import matplotlib.pyplot as plt
import numpy as np
import cv2
from typing import Optional

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def visualize_detection_results(image: np.ndarray,
                               boxes: list,
                               masks: Optional[list] = None,
                               labels: Optional[list] = None,
                               output_path: str = None):
    """
    可视化YOLOv8-seg检测结果
    
    Args:
        image: 输入图像
        boxes: 边界框列表
        masks: 分割掩膜列表（可选）
        labels: 标签列表（可选）
        output_path: 输出路径（可选）
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    ax.axis('off')
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(boxes)))
    
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = box[:4]
        rect = plt.Rectangle((x1, y1), x2-x1, y2-y1,
                           fill=False, edgecolor=colors[i], linewidth=2)
        ax.add_patch(rect)
        
        if labels and i < len(labels):
            ax.text(x1, y1-10, labels[i], color=colors[i],
                   fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        if masks and i < len(masks):
            mask = masks[i]
            mask_colored = np.zeros((*mask.shape, 4))
            mask_colored[mask > 0] = [*colors[i][:3], 0.3]
            ax.imshow(mask_colored)
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"检测结果图已保存: {output_path}")
    else:
        plt.show()
    
    plt.close()


def visualize_keypoint_heatmaps(image: np.ndarray,
                                heatmaps: np.ndarray,
                                keypoint_names: list,
                                output_path: str = None):
    """
    可视化关键点热力图
    
    Args:
        image: 输入图像
        heatmaps: 热力图数组 (num_keypoints, H, W)
        keypoint_names: 关键点名称列表
        output_path: 输出路径（可选）
    """
    num_keypoints = len(keypoint_names)
    fig, axes = plt.subplots(2, (num_keypoints+1)//2, figsize=(14, 8))
    axes = axes.flatten() if num_keypoints > 1 else [axes]
    
    for i, (heatmap, name) in enumerate(zip(heatmaps, keypoint_names)):
        ax = axes[i]
        ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        im = ax.imshow(heatmap, alpha=0.6, cmap='jet')
        ax.set_title(f'{name} 热力图', fontsize=11, fontweight='bold')
        ax.axis('off')
        plt.colorbar(im, ax=ax)
    
    # 隐藏多余的子图
    for i in range(num_keypoints, len(axes)):
        axes[i].axis('off')
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"关键点热力图已保存: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_pose_accuracy_curve(occlusion_rates: list,
                            accuracies_2mm: list,
                            accuracies_5mm: list,
                            method_names: list,
                            output_path: str = None):
    """
    绘制位姿精度曲线（图2-8）
    
    Args:
        occlusion_rates: 遮挡率列表
        accuracies_2mm: 2mm阈值下的准确率（多个方法）
        accuracies_5mm: 5mm阈值下的准确率
        method_names: 方法名称列表
        output_path: 输出路径
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    # 2mm阈值
    ax1 = axes[0]
    for i, (name, acc) in enumerate(zip(method_names, accuracies_2mm)):
        ax1.plot(occlusion_rates, acc, 'o-', linewidth=2.5, markersize=8,
                label=name, color=colors[i % len(colors)])
    ax1.set_xlabel('线缆遮挡率 (%)', fontsize=12)
    ax1.set_ylabel('准确率 (2mm阈值)', fontsize=12)
    ax1.set_title('高精度指标 (2mm) 下的位姿估计准确率', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 1.05])
    
    # 5mm阈值
    ax2 = axes[1]
    for i, (name, acc) in enumerate(zip(method_names, accuracies_5mm)):
        ax2.plot(occlusion_rates, acc, 's-', linewidth=2.5, markersize=8,
                label=name, color=colors[i % len(colors)])
    ax2.set_xlabel('线缆遮挡率 (%)', fontsize=12)
    ax2.set_ylabel('准确率 (5mm阈值)', fontsize=12)
    ax2.set_title('抓取容许误差 (5mm) 下的位姿估计准确率', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 1.05])
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"位姿精度曲线已保存: {output_path}")
    else:
        plt.show()
    
    plt.close()

