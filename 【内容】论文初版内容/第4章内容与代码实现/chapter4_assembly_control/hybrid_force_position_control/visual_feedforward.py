"""
视觉前馈补偿
利用Ch2输出的线缆方向向量计算前馈力，抵消线缆干扰
"""

import numpy as np
from typing import Optional


class VisualFeedforward:
    """视觉前馈补偿器"""
    
    def __init__(self, cable_stiffness: float = 1.0):
        """
        初始化视觉前馈补偿器
        
        Args:
            cable_stiffness: 线缆刚度系数 k_cable（根据线缆材质测定）
        """
        self.cable_stiffness = cable_stiffness
    
    def compute_feedforward_force(self,
                                 cable_vector: np.ndarray,
                                 cable_curvature: Optional[float] = None) -> np.ndarray:
        """
        计算前馈补偿力
        
        基于线缆力学先验模型：
        F_cable = k_cable * (theta * curvature)
        
        其中：
        - theta: 线缆根部切向角（从cable_vector推导）
        - curvature: 线缆曲率
        
        Args:
            cable_vector: Ch2输出的线缆方向向量 (3,)
            cable_curvature: 线缆曲率（可选，如果未提供则从方向向量估算）
        
        Returns:
            前馈补偿力/力矩 (6,) [Fx, Fy, Fz, Mx, My, Mz]
        """
        if cable_vector is None or len(cable_vector) == 0:
            return np.zeros(6)
        
        # 归一化线缆方向向量
        cable_vector = cable_vector / (np.linalg.norm(cable_vector) + 1e-6)
        
        # 计算线缆根部切向角（相对于垂直方向）
        vertical = np.array([0, 0, 1])  # 垂直向下
        theta = np.arccos(np.clip(np.dot(cable_vector, vertical), -1, 1))
        
        # 估算曲率（如果未提供）
        if cable_curvature is None:
            # 简化：曲率与角度成正比
            curvature = theta / 0.5  # 归一化因子
        else:
            curvature = cable_curvature
        
        # 计算干扰力（主要影响力矩）
        # 线缆拉扯产生的力矩与角度和曲率成正比
        interference_moment = self.cable_stiffness * theta * curvature
        
        # 构建干扰力/力矩向量
        # 主要影响侧向力矩（My, Mz）
        feedforward_force = np.zeros(6)
        
        # 侧向力（垂直于线缆方向）
        if np.abs(cable_vector[0]) > 0.1:  # 有X方向分量
            feedforward_force[1] = -interference_moment * cable_vector[0]  # Fy
            feedforward_force[4] = interference_moment  # My
        
        if np.abs(cable_vector[1]) > 0.1:  # 有Y方向分量
            feedforward_force[0] = -interference_moment * cable_vector[1]  # Fx
            feedforward_force[5] = interference_moment  # Mz
        
        # 前馈补偿应为反向力（抵消干扰）
        feedforward_force = -feedforward_force
        
        return feedforward_force
    
    def update_stiffness(self, new_stiffness: float):
        """
        更新线缆刚度系数
        
        Args:
            new_stiffness: 新的刚度系数
        """
        self.cable_stiffness = new_stiffness

