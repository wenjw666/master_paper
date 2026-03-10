"""
混合障碍物地图
结合AABB（刚性舱壁）和Octomap（柔性线缆）
"""

import numpy as np
from typing import List, Optional
import open3d as o3d


class AABB:
    """轴对齐包围盒（用于刚性舱壁）"""
    def __init__(self, min_bound: np.ndarray, max_bound: np.ndarray):
        self.min_bound = min_bound
        self.max_bound = max_bound
    
    def contains(self, point: np.ndarray) -> bool:
        """检查点是否在AABB内"""
        return np.all(point >= self.min_bound) and np.all(point <= self.max_bound)
    
    def intersects(self, other: 'AABB') -> bool:
        """检查两个AABB是否相交"""
        return np.all(self.min_bound <= other.max_bound) and np.all(self.max_bound >= other.min_bound)


class HybridObstacleMap:
    """混合障碍物地图"""
    
    def __init__(self):
        """初始化混合障碍物地图"""
        self.rigid_obstacles: List[AABB] = []  # 刚性障碍物（舱壁）
        self.cable_octomap = None  # 柔性线缆Octomap
    
    def add_rigid_obstacle(self, min_bound: np.ndarray, max_bound: np.ndarray):
        """
        添加刚性障碍物（AABB）
        
        Args:
            min_bound: 最小边界点 (3,)
            max_bound: 最大边界点 (3,)
        """
        aabb = AABB(min_bound, max_bound)
        self.rigid_obstacles.append(aabb)
    
    def set_cable_octomap(self, octomap: o3d.geometry.Octree):
        """
        设置线缆Octomap
        
        Args:
            octomap: Octomap对象
        """
        self.cable_octomap = octomap
    
    def is_free(self, config: np.ndarray) -> bool:
        """
        检查配置是否在自由空间
        
        Args:
            config: 配置（关节角度或笛卡尔坐标）
        
        Returns:
            是否自由（无碰撞）
        """
        # 将关节角度转换为末端位置（简化：假设6DOF）
        # 实际应使用正向运动学
        end_effector_pos = self._forward_kinematics(config)
        
        # 检查与刚性障碍物的碰撞
        for aabb in self.rigid_obstacles:
            if aabb.contains(end_effector_pos):
                return False
        
        # 检查与线缆Octomap的碰撞
        if self.cable_octomap is not None:
            # 检查点是否在Octomap的占用体素内
            # 这里简化处理，实际应使用Octomap的API
            # if self.cable_octomap.is_occupied(end_effector_pos):
            #     return False
            pass
        
        return True
    
    def _forward_kinematics(self, joint_angles: np.ndarray) -> np.ndarray:
        """
        正向运动学（简化实现）
        
        实际应使用完整的UR5正向运动学模型
        
        Args:
            joint_angles: 关节角度 (6,)
        
        Returns:
            末端执行器位置 (3,)
        """
        # 简化：假设末端位置与关节角度线性相关（仅用于示例）
        # 实际应使用DH参数或URDF模型计算
        return np.array([0.0, 0.0, 0.0])  # 占位实现

