"""
动作空间定义
连续6DOF位姿增量
"""

import numpy as np


class ActionSpace:
    """动作空间"""
    
    def __init__(self,
                 position_limit: float = 0.01,  # 1cm
                 angle_limit: float = 0.1):     # 0.1 rad
        """
        初始化动作空间
        
        Args:
            position_limit: 位置增量限制（米）
            angle_limit: 角度增量限制（弧度）
        """
        self.dim = 6  # 动作维度
        self.position_limit = position_limit
        self.angle_limit = angle_limit
        
        # 动作范围
        self.low = np.array([
            -position_limit, -position_limit, -position_limit,
            -angle_limit, -angle_limit, -angle_limit
        ], dtype=np.float32)
        
        self.high = np.array([
            position_limit, position_limit, position_limit,
            angle_limit, angle_limit, angle_limit
        ], dtype=np.float32)
    
    def clip(self, action: np.ndarray) -> np.ndarray:
        """
        裁剪动作到安全范围
        
        Args:
            action: 原始动作 (6,)
        
        Returns:
            裁剪后的动作 (6,)
        """
        return np.clip(action, self.low, self.high)
    
    def sample(self) -> np.ndarray:
        """
        随机采样动作（用于探索）
        
        Returns:
            随机动作 (6,)
        """
        return np.random.uniform(self.low, self.high)

