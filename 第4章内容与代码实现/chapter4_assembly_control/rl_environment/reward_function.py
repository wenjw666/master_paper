"""
奖励函数设计
距离引导 + 力安全约束 + 稀疏完成奖励
"""

import numpy as np
from typing import Optional


class RewardFunction:
    """奖励函数"""
    
    def __init__(self,
                 distance_weight: float = 1.0,
                 force_weight: float = 0.5,
                 time_penalty: float = -0.01,
                 completion_reward: float = 100.0,
                 force_threshold: float = 10.0):
        """
        初始化奖励函数
        
        Args:
            distance_weight: 距离引导奖励权重
            force_weight: 力安全约束权重
            time_penalty: 时间惩罚常数
            completion_reward: 完成奖励
            force_threshold: 力安全阈值（N）
        """
        self.distance_weight = distance_weight
        self.force_weight = force_weight
        self.time_penalty = time_penalty
        self.completion_reward = completion_reward
        self.force_threshold = force_threshold
    
    def compute(self,
               current_pose: np.ndarray,
               target_pose: np.ndarray,
               force_measured: np.ndarray,
               cable_vector: Optional[np.ndarray] = None) -> float:
        """
        计算奖励
        
        奖励函数：
        r_t = w1 * r_distance + w2 * r_force_safety + r_time + r_completion
        
        Args:
            current_pose: 当前位姿 (6,)
            target_pose: 目标位姿 (6,)
            force_measured: 测量力/力矩 (6,)
            cable_vector: 线缆方向向量（可选）
        
        Returns:
            奖励值
        """
        # 1. 距离引导奖励
        r_distance = self._compute_distance_reward(current_pose, target_pose)
        
        # 2. 力安全奖励
        r_force = self._compute_force_safety_reward(force_measured)
        
        # 3. 时间惩罚
        r_time = self.time_penalty
        
        # 4. 稀疏完成奖励（在_check_completion中处理）
        r_completion = 0.0
        if self._check_completion(current_pose, target_pose):
            r_completion = self.completion_reward
        
        # 总奖励
        total_reward = (
            self.distance_weight * r_distance +
            self.force_weight * r_force +
            r_time +
            r_completion
        )
        
        return total_reward
    
    def _compute_distance_reward(self,
                                 current_pose: np.ndarray,
                                 target_pose: np.ndarray) -> float:
        """
        计算距离引导奖励
        
        r_distance = -||p_current - p_target||
        
        Args:
            current_pose: 当前位姿
            target_pose: 目标位姿
        
        Returns:
            距离奖励
        """
        # 位置误差
        position_error = np.linalg.norm(current_pose[:3] - target_pose[:3])
        
        # 角度误差（使用四元数距离或欧拉角）
        angle_error = np.linalg.norm(current_pose[3:] - target_pose[3:])
        
        # 总误差（加权）
        total_error = position_error + 0.1 * angle_error
        
        # 奖励（负误差）
        reward = -total_error
        
        return reward
    
    def _compute_force_safety_reward(self, force_measured: np.ndarray) -> float:
        """
        计算力安全奖励（软约束）
        
        r_force = -max(0, |F| - F_threshold)^2
        
        Args:
            force_measured: 测量力/力矩 (6,)
        
        Returns:
            力安全奖励
        """
        # 计算力的大小
        force_magnitude = np.linalg.norm(force_measured[:3])
        
        # 软约束惩罚
        if force_magnitude > self.force_threshold:
            penalty = (force_magnitude - self.force_threshold) ** 2
            reward = -penalty
        else:
            reward = 0.0
        
        return reward
    
    def _check_completion(self,
                         current_pose: np.ndarray,
                         target_pose: np.ndarray,
                         position_tolerance: float = 0.001,
                         angle_tolerance: float = 0.01) -> bool:
        """
        检查装配是否完成
        
        Args:
            current_pose: 当前位姿
            target_pose: 目标位姿
            position_tolerance: 位置容差（米）
            angle_tolerance: 角度容差（弧度）
        
        Returns:
            是否完成
        """
        position_error = np.linalg.norm(current_pose[:3] - target_pose[:3])
        angle_error = np.linalg.norm(current_pose[3:] - target_pose[3:])
        
        return position_error < position_tolerance and angle_error < angle_tolerance

