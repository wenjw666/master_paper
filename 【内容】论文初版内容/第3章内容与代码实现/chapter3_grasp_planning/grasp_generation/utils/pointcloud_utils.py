"""
点云预处理工具
用于RGB-D融合、背景去除、下采样等操作
"""

import numpy as np
import open3d as o3d
import cv2
from typing import Tuple, Optional


def rgbd_to_pointcloud(rgb_image: np.ndarray,
                       depth_image: np.ndarray,
                       camera_intrinsic: np.ndarray,
                       depth_scale: float = 1000.0) -> o3d.geometry.PointCloud:
    """
    将RGB-D图像转换为点云
    
    Args:
        rgb_image: RGB图像 (H, W, 3)
        depth_image: 深度图像 (H, W)，单位：mm
        camera_intrinsic: 相机内参矩阵 (3x3)
        depth_scale: 深度缩放因子（将深度值转换为米）
    
    Returns:
        Open3D点云对象
    """
    height, width = depth_image.shape
    
    # 创建相机内参对象
    fx = camera_intrinsic[0, 0]
    fy = camera_intrinsic[1, 1]
    cx = camera_intrinsic[0, 2]
    cy = camera_intrinsic[1, 2]
    
    # 生成点云
    points = []
    colors = []
    
    for v in range(height):
        for u in range(width):
            z = depth_image[v, u] / depth_scale  # 转换为米
            if z > 0:  # 有效深度
                x = (u - cx) * z / fx
                y = (v - cy) * z / fy
                points.append([x, y, z])
                colors.append(rgb_image[v, u] / 255.0)  # 归一化到[0,1]
    
    # 创建Open3D点云
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np.array(points))
    pcd.colors = o3d.utility.Vector3dVector(np.array(colors))
    
    return pcd


def remove_background(pcd: o3d.geometry.PointCloud,
                     mask: np.ndarray,
                     depth_image: np.ndarray,
                     camera_intrinsic: np.ndarray) -> o3d.geometry.PointCloud:
    """
    利用掩膜去除背景，仅保留目标区域点云
    
    使用第二章YOLOv8-seg输出的连接器掩膜
    
    Args:
        pcd: 原始点云
        mask: 二值掩膜 (H, W)，255为目标区域，0为背景
        depth_image: 深度图像（用于确定点云索引）
        camera_intrinsic: 相机内参矩阵
    
    Returns:
        去除背景后的点云
    """
    # 获取点云坐标
    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors)
    
    # 将3D点投影回2D图像平面，检查是否在掩膜内
    fx = camera_intrinsic[0, 0]
    fy = camera_intrinsic[1, 1]
    cx = camera_intrinsic[0, 2]
    cy = camera_intrinsic[1, 2]
    
    valid_indices = []
    for i, point in enumerate(points):
        x, y, z = point
        if z > 0:  # 有效深度
            u = int(fx * x / z + cx)
            v = int(fy * y / z + cy)
            
            # 检查是否在图像范围内且在掩膜内
            if 0 <= u < mask.shape[1] and 0 <= v < mask.shape[0]:
                if mask[v, u] > 128:  # 掩膜阈值
                    valid_indices.append(i)
    
    # 提取有效点
    filtered_points = points[valid_indices]
    filtered_colors = colors[valid_indices]
    
    # 创建新点云
    filtered_pcd = o3d.geometry.PointCloud()
    filtered_pcd.points = o3d.utility.Vector3dVector(filtered_points)
    filtered_pcd.colors = o3d.utility.Vector3dVector(filtered_colors)
    
    return filtered_pcd


def voxel_downsample(pcd: o3d.geometry.PointCloud,
                    voxel_size: float = 0.005) -> o3d.geometry.PointCloud:
    """
    体素下采样点云
    
    按照论文要求，将点云密度降至0.005m
    
    Args:
        pcd: 输入点云
        voxel_size: 体素大小（米）
    
    Returns:
        下采样后的点云
    """
    downsampled_pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
    return downsampled_pcd


def preprocess_pointcloud(rgb_image: np.ndarray,
                          depth_image: np.ndarray,
                          camera_intrinsic: np.ndarray,
                          connector_mask: Optional[np.ndarray] = None,
                          voxel_size: float = 0.005) -> o3d.geometry.PointCloud:
    """
    完整的点云预处理流程
    
    Args:
        rgb_image: RGB图像
        depth_image: 深度图像
        camera_intrinsic: 相机内参
        connector_mask: 连接器掩膜（来自Ch2，可选）
        voxel_size: 体素下采样大小
    
    Returns:
        预处理后的点云
    """
    # 1. RGB-D融合生成点云
    pcd = rgbd_to_pointcloud(rgb_image, depth_image, camera_intrinsic)
    
    # 2. 背景去除（如果提供了掩膜）
    if connector_mask is not None:
        pcd = remove_background(pcd, connector_mask, depth_image, camera_intrinsic)
    
    # 3. 体素下采样
    pcd = voxel_downsample(pcd, voxel_size=voxel_size)
    
    # 4. 移除离群点（可选）
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    
    return pcd


def pointcloud_to_numpy(pcd: o3d.geometry.PointCloud) -> Tuple[np.ndarray, np.ndarray]:
    """
    将Open3D点云转换为numpy数组
    
    Args:
        pcd: Open3D点云
    
    Returns:
        (points, colors) - 点坐标和颜色
    """
    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors)
    return points, colors


def numpy_to_pointcloud(points: np.ndarray, colors: Optional[np.ndarray] = None) -> o3d.geometry.PointCloud:
    """
    将numpy数组转换为Open3D点云
    
    Args:
        points: 点坐标 (N, 3)
        colors: 颜色 (N, 3)，可选
    
    Returns:
        Open3D点云
    """
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    if colors is not None:
        pcd.colors = o3d.utility.Vector3dVector(colors)
    return pcd

