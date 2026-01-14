"""
力位混合控制器
整合阻抗控制和视觉前馈补偿
"""

import numpy as np
from typing import Dict, Optional
from .impedance_controller import ImpedanceController
from .visual_feedforward import VisualFeedforward


class HybridController:
    """力位混合控制器"""
    
    def __init__(self,
                 impedance_params: Dict,
                 visual_feedforward: bool = True,
                 cable_vector: Optional[np.ndarray] = None,
                 cable_stiffness: float = 1.0):
        """
        初始化力位混合控制器
        
        Args:
            impedance_params: 阻抗参数 {'M': ..., 'B': ..., 'K': ...}
            visual_feedforward: 是否启用视觉前馈
            cable_vector: Ch2输出的线缆方向向量
            cable_stiffness: 线缆刚度系数
        """
        # 初始化阻抗控制器
        self.impedance_controller = ImpedanceController(
            M=impedance_params.get('M'),
            B=impedance_params.get('B'),
            K=impedance_params.get('K')
        )
        
        # 初始化视觉前馈补偿器
        self.visual_feedforward_enabled = visual_feedforward
        if visual_feedforward:
            self.feedforward_compensator = VisualFeedforward(
                cable_stiffness=cable_stiffness
            )
            self.cable_vector = cable_vector
        else:
            self.feedforward_compensator = None
            self.cable_vector = None
    
    def compute_control(self,
                       pose_error: np.ndarray,
                       velocity_error: np.ndarray,
                       force_measured: np.ndarray,
                       acceleration_desired: Optional[np.ndarray] = None,
                       cable_vector: Optional[np.ndarray] = None) -> np.ndarray:
        """
        计算力位混合控制输出
        
        控制律：
        tau = M * (x_dd_desired - x_dd_current) + 
              B * (x_d_desired - x_d_current) + 
              K * (x_desired - x_current) - 
              F_ext + 
              F_feedforward  # 视觉前馈项
        
        Args:
            pose_error: 位姿误差 (6,)
            velocity_error: 速度误差 (6,)
            force_measured: 测量力/力矩 (6,)
            acceleration_desired: 期望加速度 (6,)，可选
            cable_vector: 线缆方向向量（如果与初始化时不同，可在此更新）
        
        Returns:
            控制力矩/力 (6,)
        """
        # 阻抗控制输出
        impedance_output = self.impedance_controller.compute_control(
            pose_error=pose_error,
            velocity_error=velocity_error,
            force_measured=force_measured,
            acceleration_desired=acceleration_desired
        )
        
        # 视觉前馈补偿
        feedforward_output = np.zeros(6)
        if self.visual_feedforward_enabled and self.feedforward_compensator is not None:
            # 使用提供的cable_vector或初始化时的cable_vector
            current_cable_vector = cable_vector if cable_vector is not None else self.cable_vector
            if current_cable_vector is not None:
                feedforward_output = self.feedforward_compensator.compute_feedforward_force(
                    cable_vector=current_cable_vector
                )
        
        # 总控制输出
        total_control = impedance_output + feedforward_output
        
        return total_control
    
    def update_cable_vector(self, new_cable_vector: np.ndarray):
        """
        更新线缆方向向量（实时更新）
        
        Args:
            new_cable_vector: 新的线缆方向向量（来自Ch2）
        """
        self.cable_vector = new_cable_vector
    
    def update_impedance_params(self, **kwargs):
        """更新阻抗参数"""
        self.impedance_controller.update_impedance_params(**kwargs)
    
    def update_cable_stiffness(self, new_stiffness: float):
        """更新线缆刚度系数"""
        if self.feedforward_compensator is not None:
            self.feedforward_compensator.update_stiffness(new_stiffness)

