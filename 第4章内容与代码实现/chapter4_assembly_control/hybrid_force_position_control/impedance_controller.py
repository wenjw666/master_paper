"""
阻抗控制器
实现内环柔顺性保证
"""

import numpy as np
from typing import Dict, Optional


class ImpedanceController:
    """阻抗控制器"""
    
    def __init__(self,
                 M: np.ndarray,
                 B: np.ndarray,
                 K: np.ndarray):
        """
        初始化阻抗控制器
        
        Args:
            M: 惯性矩阵 (6x6) - 目标阻抗参数
            B: 阻尼矩阵 (6x6)
            K: 刚度矩阵 (6x6)
        """
        self.M = M  # 惯性
        self.B = B  # 阻尼
        self.K = K  # 刚度
        
        # 默认参数（如果未提供）
        if M is None:
            self.M = np.eye(6) * 1.0
        if B is None:
            self.B = np.eye(6) * 50.0
        if K is None:
            self.K = np.eye(6) * 500.0
    
    def compute_control(self,
                       pose_error: np.ndarray,
                       velocity_error: np.ndarray,
                       force_measured: np.ndarray,
                       acceleration_desired: Optional[np.ndarray] = None) -> np.ndarray:
        """
        计算阻抗控制输出
        
        控制律：
        tau = M * (x_dd_desired - x_dd_current) + 
              B * (x_d_desired - x_d_current) + 
              K * (x_desired - x_current) - 
              F_ext
        
        Args:
            pose_error: 位姿误差 (6,) [x, y, z, roll, pitch, yaw]
            velocity_error: 速度误差 (6,)
            force_measured: 测量力/力矩 (6,)
            acceleration_desired: 期望加速度 (6,)，可选
        
        Returns:
            控制力矩/力 (6,)
        """
        if acceleration_desired is None:
            acceleration_desired = np.zeros(6)
        
        # 阻抗控制律
        # 位置项
        position_term = self.K @ pose_error
        
        # 速度项
        velocity_term = self.B @ velocity_error
        
        # 加速度项
        acceleration_term = self.M @ acceleration_desired
        
        # 外力补偿
        force_term = -force_measured
        
        # 总控制输出
        control_output = acceleration_term + velocity_term + position_term + force_term
        
        return control_output
    
    def update_impedance_params(self,
                               M: Optional[np.ndarray] = None,
                               B: Optional[np.ndarray] = None,
                               K: Optional[np.ndarray] = None):
        """
        更新阻抗参数（可用于自适应控制）
        
        Args:
            M: 新的惯性矩阵
            B: 新的阻尼矩阵
            K: 新的刚度矩阵
        """
        if M is not None:
            self.M = M
        if B is not None:
            self.B = B
        if K is not None:
            self.K = K

