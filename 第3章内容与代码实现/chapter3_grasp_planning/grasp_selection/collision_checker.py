"""
碰撞检测模块
用于检测夹爪与线缆点云的碰撞
"""

import numpy as np
from typing import Tuple
import open3d as o3d


class CollisionChecker:
    """碰撞检测器"""
    
    def __init__(self, safety_margin: float = 0.01):
        """
        初始化碰撞检测器
        
        Args:
            safety_margin: 安全边距（米）
        """
        self.safety_margin = safety_margin
    
    def compute_min_distance(self,
                            points1: np.ndarray,
                            points2: np.ndarray) -> float:
        """
        计算两组点云之间的最小距离
        
        Args:
            points1: 第一组点云 (N1, 3)
            points2: 第二组点云 (N2, 3)
        
        Returns:
            最小距离（米）
        """
        if len(points1) == 0 or len(points2) == 0:
            return float('inf')
        
        # 使用KD树加速最近邻搜索
        pcd2 = o3d.geometry.PointCloud()
        pcd2.points = o3d.utility.Vector3dVector(points2)
        kdtree = o3d.geometry.KDTreeFlann(pcd2)
        
        min_dist = float('inf')
        
        for point in points1:
            # 查找最近邻
            [k, idx, dist_sq] = kdtree.search_knn_vector_3d(point, 1)
            if k > 0:
                dist = np.sqrt(dist_sq[0])
                min_dist = min(min_dist, dist)
        
        return min_dist
    
    def check_collision(self,
                       points1: np.ndarray,
                       points2: np.ndarray,
                       threshold: float = 0.0) -> bool:
        """
        检查两组点云是否碰撞
        
        Args:
            points1: 第一组点云
            points2: 第二组点云
            threshold: 碰撞阈值（考虑安全边距）
        
        Returns:
            是否发生碰撞
        """
        min_dist = self.compute_min_distance(points1, points2)
        return min_dist < (threshold + self.safety_margin)
    
    def check_collision_with_octomap(self,
                                    points: np.ndarray,
                                    octomap) -> bool:
        """
        检查点云与Octomap是否碰撞
        
        Args:
            points: 点云 (N, 3)
            octomap: Octomap对象
        
        Returns:
            是否发生碰撞
        """
        # 这里需要根据Octomap的实际API实现
        # 示例：检查每个点是否在占用体素内
        for point in points:
            # if octomap.isOccupied(point):
            #     return True
            pass
        
        return False

