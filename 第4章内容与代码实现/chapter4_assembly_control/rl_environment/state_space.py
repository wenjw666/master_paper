"""
状态空间定义
18维状态向量：位姿偏差、速度、力/力矩、线缆方向向量
"""

import numpy as np
from typing import Dict, Optional


class StateSpace:
    """状态空间"""
    
    def __init__(self):
        """初始化状态空间"""
        self.dim = 18  # 状态维度
        
        # 归一化参数
        self.position_scale = 0.1  # 位置归一化（米）
        self.angle_scale = 1.0     # 角度归一化（弧度）
        self.velocity_scale = 0.1  # 速度归一化
        self.force_scale = 10.0    # 力归一化（N）
        self.moment_scale = 1.0    # 力矩归一化（Nm）
    
    def encode(self,
              current_pose: np.ndarray,
              target_pose: np.ndarray,
              velocity: np.ndarray,
              force_measured: np.ndarray,
              cable_vector: Optional[np.ndarray] = None) -> np.ndarray:
        """
        编码状态向量
        
        状态组成：
        - pose_error (6,): 位姿偏差 [x, y, z, roll, pitch, yaw]
        - velocity (6,): 末端速度
        - force_measured (6,): 力/力矩传感器读数
        - cable_vector (3,): 线缆方向向量（Ch2输出）
        
        Args:
            current_pose: 当前位姿 (6,)
            target_pose: 目标位姿 (6,)
            velocity: 末端速度 (6,)
            force_measured: 测量力/力矩 (6,)
            cable_vector: 线缆方向向量 (3,)，可选
        
        Returns:
            归一化后的状态向量 (18,)
        """
        # 计算位姿偏差
        pose_error = current_pose - target_pose
        
        # 归一化位姿偏差
        pose_error_normalized = np.zeros(6)
        pose_error_normalized[:3] = pose_error[:3] / self.position_scale  # 位置
        pose_error_normalized[3:] = pose_error[3:] / self.angle_scale    # 角度
        
        # 归一化速度
        velocity_normalized = velocity / self.velocity_scale
        
        # 归一化力/力矩
        force_normalized = np.zeros(6)
        force_normalized[:3] = force_measured[:3] / self.force_scale      # 力
        force_normalized[3:] = force_measured[3:] / self.moment_scale     # 力矩
        
        # 线缆方向向量（归一化）
        if cable_vector is not None:
            cable_vector_normalized = cable_vector / (np.linalg.norm(cable_vector) + 1e-6)
        else:
            cable_vector_normalized = np.array([0, 0, 1])  # 默认向下
        
        # 组合状态向量
        state = np.concatenate([
            pose_error_normalized,      # 6维
            velocity_normalized,        # 6维
            force_normalized,           # 6维
            cable_vector_normalized     # 3维
        ])
        
        return state.astype(np.float32)
    
    def decode(self, state: np.ndarray) -> Dict:
        """
        解码状态向量（用于分析）
        
        Args:
            state: 状态向量 (18,)
        
        Returns:
            解码后的状态字典
        """
        pose_error = state[:6].copy()
        pose_error[:3] *= self.position_scale
        pose_error[3:] *= self.angle_scale
        
        velocity = state[6:12] * self.velocity_scale
        
        force = state[12:18].copy()
        force[:3] *= self.force_scale
        force[3:] *= self.moment_scale
        
        cable_vector = state[18:21]
        
        return {
            'pose_error': pose_error,
            'velocity': velocity,
            'force': force,
            'cable_vector': cable_vector
        }

