"""
逆运动学求解器
支持PyBullet和IKFast
"""

import numpy as np
from typing import List, Optional, Dict
import pybullet as p


class IKSolver:
    """逆运动学求解器"""
    
    def __init__(self, robot_type: str = "ur5", use_pybullet: bool = True):
        """
        初始化IK求解器
        
        Args:
            robot_type: 机器人类型（"ur5", "ur5e"等）
            use_pybullet: 是否使用PyBullet求解器
        """
        self.robot_type = robot_type
        self.use_pybullet = use_pybullet
        
        # 关节限位（UR5，单位：弧度）
        self.joint_limits = {
            'ur5': {
                'lower': np.array([-np.pi, -np.pi, -np.pi, -np.pi, -np.pi, -np.pi]),
                'upper': np.array([np.pi, np.pi, np.pi, np.pi, np.pi, np.pi])
            }
        }
        
        # PyBullet连接（如果需要）
        self.physics_client = None
        self.robot_id = None
        
        if use_pybullet:
            self._init_pybullet()
    
    def _init_pybullet(self):
        """初始化PyBullet（用于IK求解）"""
        try:
            self.physics_client = p.connect(p.DIRECT)  # 无GUI模式
            # 加载机器人模型（需要URDF文件）
            # self.robot_id = p.loadURDF("path/to/ur5.urdf")
        except Exception as e:
            print(f"警告: PyBullet初始化失败: {e}")
            self.use_pybullet = False
    
    def solve_ik(self,
                  target_pose: Dict,
                  current_joints: Optional[np.ndarray] = None,
                  max_iterations: int = 100) -> List[np.ndarray]:
        """
        求解逆运动学
        
        Args:
            target_pose: 目标位姿 {'translation': (3,), 'rotation': (3,3)}
            current_joints: 当前关节角度（用于初始化，可选）
            max_iterations: 最大迭代次数
        
        Returns:
            IK解列表（可能有多个解）
        """
        if self.use_pybullet and self.robot_id is not None:
            return self._solve_ik_pybullet(target_pose, current_joints, max_iterations)
        else:
            # 使用数值优化方法（Levenberg-Marquardt）
            return self._solve_ik_numerical(target_pose, current_joints, max_iterations)
    
    def _solve_ik_pybullet(self,
                           target_pose: Dict,
                           current_joints: Optional[np.ndarray],
                           max_iterations: int) -> List[np.ndarray]:
        """使用PyBullet求解IK"""
        t = target_pose['translation']
        R = target_pose['rotation']
        
        # 转换为四元数
        from scipy.spatial.transform import Rotation
        rot = Rotation.from_matrix(R)
        quaternion = rot.as_quat()  # [x, y, z, w]
        
        # 求解IK
        if current_joints is not None:
            joint_positions = p.calculateInverseKinematics(
                self.robot_id,
                endEffectorLinkIndex=7,  # 末端执行器链接索引
                targetPosition=t,
                targetOrientation=quaternion,
                maxNumIterations=max_iterations,
                currentPositions=current_joints.tolist()
            )
        else:
            joint_positions = p.calculateInverseKinematics(
                self.robot_id,
                endEffectorLinkIndex=7,
                targetPosition=t,
                targetOrientation=quaternion,
                maxNumIterations=max_iterations
            )
        
        return [np.array(joint_positions)]
    
    def _solve_ik_numerical(self,
                           target_pose: Dict,
                           current_joints: Optional[np.ndarray],
                           max_iterations: int) -> List[np.ndarray]:
        """
        使用数值优化求解IK（简化实现）
        
        注意：这是一个简化实现，实际应使用更完善的IK求解器
        """
        # 这里提供一个占位实现
        # 实际应使用Levenberg-Marquardt等优化算法
        
        if current_joints is None:
            # 使用零位作为初始值
            current_joints = np.zeros(6)
        
        # 简化：返回一个近似解（实际需要完整的正向运动学和优化）
        # 这里仅作为示例
        solutions = []
        
        # 尝试多个初始值
        for seed in [current_joints, np.zeros(6), np.random.randn(6) * 0.1]:
            # 这里应实现完整的优化过程
            # solution = optimize_ik(target_pose, seed, max_iterations)
            # if solution is not None:
            #     solutions.append(solution)
            pass
        
        # 临时：返回一个示例解（实际应删除）
        if len(solutions) == 0:
            # 返回一个默认解（仅用于测试）
            solutions.append(current_joints)
        
        return solutions
    
    def check_joint_limits(self, joint_angles: np.ndarray) -> bool:
        """
        检查关节角度是否在限位内
        
        Args:
            joint_angles: 关节角度数组
        
        Returns:
            是否在限位内
        """
        if self.robot_type not in self.joint_limits:
            return True  # 未知机器人类型，默认通过
        
        limits = self.joint_limits[self.robot_type]
        lower = limits['lower']
        upper = limits['upper']
        
        return np.all(joint_angles >= lower) and np.all(joint_angles <= upper)
    
    def __del__(self):
        """析构函数"""
        if self.physics_client is not None:
            try:
                p.disconnect(self.physics_client)
            except:
                pass

