"""
完整装配控制流程
整合力位混合控制和SAC策略
"""

import numpy as np
import torch
from typing import Dict, Optional, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from hybrid_force_position_control.force_position_hybrid import HybridController
from sac_algorithm.sac import SAC


class AssemblyControlPipeline:
    """装配控制流水线"""
    
    def __init__(self,
                 sac_model_path: str,
                 cable_vector: Optional[np.ndarray] = None,
                 target_pose: Optional[np.ndarray] = None,
                 impedance_params: Optional[Dict] = None,
                 device: str = 'cuda'):
        """
        初始化装配控制流水线
        
        Args:
            sac_model_path: SAC模型路径
            cable_vector: Ch2输出的线缆方向向量
            target_pose: 目标装配位姿
            impedance_params: 阻抗参数
            device: 计算设备
        """
        self.cable_vector = cable_vector
        self.target_pose = target_pose
        self.device = device
        
        # 加载SAC模型
        # 需要知道状态和动作维度（从配置文件或模型元数据获取）
        state_dim = 18  # 从state_space定义
        action_dim = 6
        action_range = (-0.01, 0.01)  # 位置增量限制
        
        self.sac = SAC(
            state_dim=state_dim,
            action_dim=action_dim,
            action_range=action_range,
            device=device
        )
        self.sac.load(sac_model_path)
        self.sac.actor.eval()  # 设置为评估模式
        
        # 初始化力位混合控制器
        if impedance_params is None:
            impedance_params = {
                'M': np.eye(6) * 1.0,
                'B': np.eye(6) * 50.0,
                'K': np.eye(6) * 500.0
            }
        
        self.hybrid_controller = HybridController(
            impedance_params=impedance_params,
            visual_feedforward=True,
            cable_vector=cable_vector,
            cable_stiffness=1.0
        )
        
        # 状态变量
        self.current_pose = None
        self.current_velocity = None
        self.force_measured = None
    
    def execute_assembly(self,
                        start_pose: np.ndarray,
                        target_pose: Optional[np.ndarray] = None,
                        max_steps: int = 1000,
                        force_threshold: float = 30.0) -> Dict:
        """
        执行装配任务
        
        Args:
            start_pose: 起始位姿
            target_pose: 目标位姿（如果为None，使用初始化时的值）
            max_steps: 最大步数
            force_threshold: 力阈值（超过此值急停）
        
        Returns:
            执行结果 {
                'success': bool,
                'steps': int,
                'force_history': [...],
                'trajectory': [...]
            }
        """
        if target_pose is None:
            target_pose = self.target_pose
        
        if target_pose is None:
            return {
                'success': False,
                'steps': 0,
                'force_history': [],
                'trajectory': [],
                'message': '未指定目标位姿'
            }
        
        # 初始化状态
        self.current_pose = start_pose.copy()
        self.current_velocity = np.zeros(6)
        self.force_measured = np.zeros(6)
        
        # 记录
        force_history = []
        trajectory = [start_pose.copy()]
        
        success = False
        
        for step in range(max_steps):
            # 计算状态（需要state_space模块）
            from rl_environment.state_space import StateSpace
            state_space = StateSpace()
            
            state = state_space.encode(
                current_pose=self.current_pose,
                target_pose=target_pose,
                velocity=self.current_velocity,
                force_measured=self.force_measured,
                cable_vector=self.cable_vector
            )
            
            # SAC策略选择动作
            action = self.sac.select_action(state, deterministic=True)
            
            # 更新目标位姿（动作是增量）
            target_pose_updated = self.current_pose + action
            
            # 计算位姿误差和速度误差
            pose_error = target_pose_updated - self.current_pose
            velocity_error = -self.current_velocity  # 期望速度为0
            
            # 力位混合控制
            control_output = self.hybrid_controller.compute_control(
                pose_error=pose_error,
                velocity_error=velocity_error,
                force_measured=self.force_measured,
                cable_vector=self.cable_vector
            )
            
            # 执行控制（实际应发送到机器人）
            # robot.send_torque(control_output)
            
            # 更新状态（实际应从机器人反馈获取）
            # 这里简化处理
            self.current_pose = target_pose_updated
            self.current_velocity = action * 30.0  # 假设控制频率30Hz
            
            # 记录
            force_history.append(self.force_measured.copy())
            trajectory.append(self.current_pose.copy())
            
            # 检查完成条件
            position_error = np.linalg.norm(self.current_pose[:3] - target_pose[:3])
            if position_error < 0.001:  # 1mm阈值
                success = True
                break
            
            # 检查力阈值（安全保护）
            force_magnitude = np.linalg.norm(self.force_measured[:3])
            if force_magnitude > force_threshold:
                return {
                    'success': False,
                    'steps': step + 1,
                    'force_history': force_history,
                    'trajectory': trajectory,
                    'message': f'力超限: {force_magnitude:.2f}N > {force_threshold}N'
                }
        
        return {
            'success': success,
            'steps': step + 1,
            'force_history': force_history,
            'trajectory': trajectory,
            'message': '装配完成' if success else '达到最大步数'
        }
    
    def update_cable_vector(self, new_cable_vector: np.ndarray):
        """更新线缆方向向量（实时更新）"""
        self.cable_vector = new_cable_vector
        self.hybrid_controller.update_cable_vector(new_cable_vector)

