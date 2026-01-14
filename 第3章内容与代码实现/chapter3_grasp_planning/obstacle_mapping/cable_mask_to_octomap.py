"""
将Ch2输出的线缆掩膜映射为3D Octomap
"""

import numpy as np
import cv2
import open3d as o3d
from typing import Optional


def cable_mask_to_pointcloud(mask: np.ndarray,
                             depth_image: np.ndarray,
                             camera_intrinsic: np.ndarray,
                             depth_scale: float = 1000.0) -> o3d.geometry.PointCloud:
    """
    将线缆掩膜转换为3D点云
    
    Args:
        mask: 线缆二值掩膜 (H, W)，255为线缆区域
        depth_image: 深度图像 (H, W)，单位：mm
        camera_intrinsic: 相机内参矩阵 (3x3)
        depth_scale: 深度缩放因子
    
    Returns:
        线缆点云（Open3D格式）
    """
    height, width = mask.shape
    
    # 相机内参
    fx = camera_intrinsic[0, 0]
    fy = camera_intrinsic[1, 1]
    cx = camera_intrinsic[0, 2]
    cy = camera_intrinsic[1, 2]
    
    # 提取线缆区域点
    points = []
    colors = []
    
    cable_pixels = np.where(mask > 128)  # 掩膜阈值
    
    for v, u in zip(cable_pixels[0], cable_pixels[1]):
        z = depth_image[v, u] / depth_scale  # 转换为米
        
        if z > 0:  # 有效深度
            x = (u - cx) * z / fx
            y = (v - cy) * z / fy
            points.append([x, y, z])
            colors.append([1.0, 0.0, 0.0])  # 红色表示线缆
    
    if len(points) == 0:
        return o3d.geometry.PointCloud()
    
    # 创建点云
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np.array(points))
    pcd.colors = o3d.utility.Vector3dVector(np.array(colors))
    
    return pcd


def pointcloud_to_octomap(pcd: o3d.geometry.PointCloud,
                          resolution: float = 0.01,
                          occupancy_threshold: float = 0.5) -> o3d.geometry.Octree:
    """
    将点云转换为Octomap
    
    Args:
        pcd: 输入点云
        resolution: Octomap分辨率（米）
        occupancy_threshold: 占用阈值
    
    Returns:
        Octomap（Open3D Octree格式）
    """
    if len(pcd.points) == 0:
        return None
    
    # 创建Octomap
    octomap = o3d.geometry.Octree(max_depth=10)
    octomap.convert_from_point_cloud(pcd, size_expand=0.01)
    
    return octomap


def cable_mask_to_octomap(mask: np.ndarray,
                          depth_image: np.ndarray,
                          camera_intrinsic: np.ndarray,
                          resolution: float = 0.01) -> o3d.geometry.Octree:
    """
    完整的转换流程：线缆掩膜 → 点云 → Octomap
    
    Args:
        mask: 线缆掩膜
        depth_image: 深度图像
        camera_intrinsic: 相机内参
        resolution: Octomap分辨率
    
    Returns:
        Octomap对象
    """
    # 1. 掩膜转点云
    pcd = cable_mask_to_pointcloud(mask, depth_image, camera_intrinsic)
    
    if len(pcd.points) == 0:
        return None
    
    # 2. 点云转Octomap
    octomap = pointcloud_to_octomap(pcd, resolution)
    
    return octomap


def update_octomap_dynamic(octomap: o3d.geometry.Octree,
                          new_mask: np.ndarray,
                          new_depth: np.ndarray,
                          camera_intrinsic: np.ndarray):
    """
    动态更新Octomap（当线缆形态变化时）
    
    Args:
        octomap: 现有Octomap
        new_mask: 新的线缆掩膜
        new_depth: 新的深度图像
        camera_intrinsic: 相机内参
    """
    # 生成新的点云
    new_pcd = cable_mask_to_pointcloud(new_mask, new_depth, camera_intrinsic)
    
    if len(new_pcd.points) == 0:
        return
    
    # 更新Octomap（添加新点）
    octomap.convert_from_point_cloud(new_pcd, size_expand=0.01)

