"""
电连接器装配强化学习环境
基于Gymnasium接口
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pybullet as p
import pybullet_data
from typing import Dict, Optional, Tuple
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from rl_environment.state_space import StateSpace
from rl_environment.action_space import ActionSpace
from rl_environment.reward_function import RewardFunction


class ConnectorAssemblyEnv(gym.Env):
    """电连接器装配环境"""
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}
    
    def __init__(self,
                 render_mode: Optional[str] = None,
                 control_frequency: int = 30,
                 physics_frequency: int = 240,
                 use_domain_randomization: bool = True):
        """
        初始化装配环境
        
        Args:
            render_mode: 渲染模式
            control_frequency: 控制频率（Hz）
            physics_frequency: 物理引擎频率（Hz）
            use_domain_randomization: 是否使用域随机化
        """
        super().__init__()
        
        self.control_frequency = control_frequency
        self.physics_frequency = physics_frequency
        self.use_domain_randomization = use_domain_randomization
        
        # 初始化状态空间、动作空间和奖励函数
        self.state_space = StateSpace()
        self.action_space = ActionSpace()
        self.reward_function = RewardFunction()
        
        # Gymnasium接口
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.state_space.dim,),
            dtype=np.float32
        )
        
        self.action_space_gym = spaces.Box(
            low=self.action_space.low,
            high=self.action_space.high,
            shape=(self.action_space.dim,),
            dtype=np.float32
        )
        
        # PyBullet连接
        self.physics_client = None
        self.robot_id = None
        self.connector_id = None
        self.socket_id = None
        self.cable_id = None
        
        # 状态变量
        self.current_pose = None
        self.target_pose = None
        self.cable_vector = None
        self.force_measured = None
        
        # 域随机化参数
        self.cable_stiffness = 1.0
        self.friction_coeff = 0.3
        self.sensor_noise_std = 0.0
        
        self.render_mode = render_mode
    
    def reset(self,
              seed: Optional[int] = None,
              options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """
        重置环境
        
        Returns:
            (observation, info)
        """
        super().reset(seed=seed)
        
        # 连接PyBullet
        if self.physics_client is None:
            if self.render_mode == "human":
                self.physics_client = p.connect(p.GUI)
            else:
                self.physics_client = p.connect(p.DIRECT)
            
            p.setAdditionalSearchPath(pybullet_data.getDataPath())
            p.setGravity(0, 0, -9.81)
            p.setTimeStep(1.0 / self.physics_frequency)
        
        # 域随机化
        if self.use_domain_randomization:
            self._randomize_domain()
        
        # 加载场景（UR5机械臂、连接器、插座、线缆）
        self._load_scene()
        
        # 初始化状态
        self.current_pose = self._get_end_effector_pose()
        self.target_pose = self._get_target_pose()
        self.cable_vector = self._get_cable_vector()
        self.force_measured = np.zeros(6)
        
        # 获取初始观测
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        执行一步动作
        
        Args:
            action: 动作向量 (6,)
        
        Returns:
            (observation, reward, terminated, truncated, info)
        """
        # 应用动作（更新目标位姿）
        self._apply_action(action)
        
        # 执行控制循环（多个物理步）
        steps_per_control = self.physics_frequency // self.control_frequency
        for _ in range(steps_per_control):
            p.stepSimulation()
        
        # 更新状态
        self.current_pose = self._get_end_effector_pose()
        self.force_measured = self._get_force_measurement()
        self.cable_vector = self._get_cable_vector()
        
        # 计算奖励
        reward = self.reward_function.compute(
            current_pose=self.current_pose,
            target_pose=self.target_pose,
            force_measured=self.force_measured,
            cable_vector=self.cable_vector
        )
        
        # 检查终止条件
        terminated = self._check_assembly_complete()
        truncated = self._check_timeout()
        
        # 获取观测和信息
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, reward, terminated, truncated, info
    
    def _load_scene(self):
        """加载仿真场景"""
        # 加载地面
        p.loadURDF("plane.urdf")
        
        # 加载UR5机械臂（需要URDF文件）
        # self.robot_id = p.loadURDF("ur5.urdf", basePosition=[0, 0, 0])
        
        # 加载连接器和插座（需要CAD模型）
        # self.connector_id = p.loadURDF("connector.urdf", ...)
        # self.socket_id = p.loadURDF("socket.urdf", ...)
        
        # 加载线缆（使用离散化连杆模型）
        # self.cable_id = self._load_cable_model()
        
        pass  # 占位实现
    
    def _randomize_domain(self):
        """域随机化"""
        # 线缆刚度随机化
        self.cable_stiffness = np.random.uniform(0.5, 2.0)
        
        # 摩擦系数随机化
        self.friction_coeff = np.random.uniform(0.1, 0.5)
        
        # 观测噪声
        self.sensor_noise_std = np.random.uniform(0.0, 0.1)
    
    def _apply_action(self, action: np.ndarray):
        """应用动作到环境"""
        # 动作是位姿增量，叠加到当前目标位姿
        # 实际应通过力位混合控制器执行
        pass  # 占位实现
    
    def _get_observation(self) -> np.ndarray:
        """获取当前观测"""
        return self.state_space.encode(
            current_pose=self.current_pose,
            target_pose=self.target_pose,
            velocity=self._get_velocity(),
            force_measured=self.force_measured,
            cable_vector=self.cable_vector
        )
    
    def _get_reward(self) -> float:
        """计算奖励（已移至reward_function）"""
        return 0.0
    
    def _check_assembly_complete(self) -> bool:
        """检查装配是否完成"""
        # 检查连接器是否成功插入插座
        # 简化：检查位置和力
        position_error = np.linalg.norm(self.current_pose[:3] - self.target_pose[:3])
        return position_error < 0.001  # 1mm阈值
    
    def _check_timeout(self) -> bool:
        """检查是否超时"""
        # 应在环境中维护步数计数器
        return False  # 占位实现
    
    def _get_end_effector_pose(self) -> np.ndarray:
        """获取末端执行器位姿"""
        # 从PyBullet获取
        return np.zeros(6)  # 占位实现
    
    def _get_target_pose(self) -> np.ndarray:
        """获取目标位姿"""
        return np.array([0, 0, 0.1, 0, 0, 0])  # 占位实现
    
    def _get_velocity(self) -> np.ndarray:
        """获取末端速度"""
        return np.zeros(6)  # 占位实现
    
    def _get_force_measurement(self) -> np.ndarray:
        """获取力传感器读数（带噪声）"""
        # 从PyBullet获取接触力
        force = np.zeros(6)  # 占位实现
        
        # 添加观测噪声
        if self.sensor_noise_std > 0:
            noise = np.random.normal(0, self.sensor_noise_std, 6)
            force += noise
        
        return force
    
    def _get_cable_vector(self) -> np.ndarray:
        """获取线缆方向向量（来自Ch2或仿真）"""
        return np.array([0, 0, 1])  # 占位实现
    
    def _get_info(self) -> Dict:
        """获取额外信息"""
        return {
            'position_error': np.linalg.norm(self.current_pose[:3] - self.target_pose[:3]),
            'force_magnitude': np.linalg.norm(self.force_measured[:3])
        }
    
    def render(self):
        """渲染环境"""
        if self.render_mode == "human":
            # PyBullet GUI自动渲染
            pass
    
    def close(self):
        """关闭环境"""
        if self.physics_client is not None:
            p.disconnect(self.physics_client)
            self.physics_client = None

