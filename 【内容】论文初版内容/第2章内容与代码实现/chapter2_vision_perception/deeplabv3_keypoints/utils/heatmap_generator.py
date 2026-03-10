"""
高斯热力图生成工具
用于关键点标注和训练数据准备
"""

import numpy as np
import cv2


def generate_gaussian_heatmap(shape, center, sigma=2.0):
    """
    生成高斯热力图
    
    按照论文公式：
    H_k(x,y) = exp(-((x-x_k)^2 + (y-y_k)^2) / (2*sigma^2))
    
    Args:
        shape: 热力图尺寸 (height, width)
        center: 关键点中心坐标 (x, y)
        sigma: 高斯标准差，控制扩散程度
    
    Returns:
        高斯热力图 (numpy array, dtype=float32, 范围[0,1])
    """
    h, w = shape
    y_coords, x_coords = np.ogrid[:h, :w]
    
    # 计算到中心的距离
    x_center, y_center = center
    dist_sq = (x_coords - x_center) ** 2 + (y_coords - y_center) ** 2
    
    # 生成高斯分布
    heatmap = np.exp(-dist_sq / (2 * sigma ** 2))
    
    return heatmap.astype(np.float32)


def generate_multi_keypoint_heatmaps(shape, keypoints, sigma=2.0):
    """
    为多个关键点生成热力图
    
    Args:
        shape: 热力图尺寸 (height, width)
        keypoints: 关键点列表 [(x1, y1), (x2, y2), ...]
        sigma: 高斯标准差
    
    Returns:
        多通道热力图 (num_keypoints, height, width)
    """
    num_keypoints = len(keypoints)
    heatmaps = np.zeros((num_keypoints, shape[0], shape[1]), dtype=np.float32)
    
    for i, kpt in enumerate(keypoints):
        if kpt is not None and len(kpt) == 2:
            heatmaps[i] = generate_gaussian_heatmap(shape, kpt, sigma)
    
    return heatmaps


def extract_keypoint_from_heatmap(heatmap, threshold=0.3):
    """
    从热力图中提取关键点坐标（峰值位置）
    
    Args:
        heatmap: 单通道热力图
        threshold: 峰值阈值
    
    Returns:
        关键点坐标 (x, y) 或 None（如果未找到）
    """
    # 应用阈值
    heatmap_thresh = heatmap.copy()
    heatmap_thresh[heatmap_thresh < threshold] = 0
    
    # 找到最大值位置
    max_val = np.max(heatmap_thresh)
    if max_val < threshold:
        return None
    
    # 获取峰值坐标（可能有多个，取最大的）
    y, x = np.unravel_index(np.argmax(heatmap_thresh), heatmap_thresh.shape)
    
    # 可选：使用加权质心提高精度
    # 在峰值周围的小区域内计算质心
    window_size = 5
    y_min = max(0, y - window_size // 2)
    y_max = min(heatmap.shape[0], y + window_size // 2 + 1)
    x_min = max(0, x - window_size // 2)
    x_max = min(heatmap.shape[1], x + window_size // 2 + 1)
    
    window = heatmap_thresh[y_min:y_max, x_min:x_max]
    if window.sum() > 0:
        y_coords, x_coords = np.ogrid[y_min:y_max, x_min:x_max]
        y_centroid = (y_coords * window).sum() / window.sum()
        x_centroid = (x_coords * window).sum() / window.sum()
        return (x_centroid, y_centroid)
    
    return (x, y)


def visualize_heatmap(heatmap, image=None, alpha=0.6):
    """
    可视化热力图
    
    Args:
        heatmap: 热力图
        image: 原始图像（可选）
        alpha: 叠加透明度
    
    Returns:
        可视化图像
    """
    # 归一化到0-255
    heatmap_norm = (heatmap * 255).astype(np.uint8)
    
    # 应用颜色映射
    heatmap_colored = cv2.applyColorMap(heatmap_norm, cv2.COLORMAP_JET)
    
    if image is not None:
        # 叠加到原图
        vis = cv2.addWeighted(image, 1-alpha, heatmap_colored, alpha, 0)
        return vis
    
    return heatmap_colored

