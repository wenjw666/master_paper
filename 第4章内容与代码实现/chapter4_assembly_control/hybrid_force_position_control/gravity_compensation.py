"""
重力补偿模块
用于力传感器的重力补偿
"""

import numpy as np
from typing import Optional, Tuple


class GravityCompensator:
    """重力补偿器"""
    
    def __init__(self,
                 load_mass: float,
                 load_cog: np.ndarray,
                 gravity: np.ndarray = np.array([0, 0, -9.81])):
        """
        初始化重力补偿器
        
        Args:
            load_mass: 负载质量（kg）（夹爪+连接器）
            load_cog: 负载质心位置（相对于传感器坐标系）(3,)
            gravity: 重力加速度向量 (3,)，默认[0, 0, -9.81]
        """
        self.load_mass = load_mass
        self.load_cog = load_cog
        self.gravity = gravity
    
    def compute_gravity_force(self, rotation_matrix: np.ndarray) -> np.ndarray:
        """
        计算重力在传感器坐标系下的力/力矩
        
        Args:
            rotation_matrix: 传感器坐标系到世界坐标系的旋转矩阵 (3x3)
        
        Returns:
            重力产生的力/力矩 (6,) [Fx, Fy, Fz, Mx, My, Mz]
        """
        # 重力在世界坐标系下
        gravity_world = self.load_mass * self.gravity
        
        # 转换到传感器坐标系
        gravity_sensor = rotation_matrix.T @ gravity_world
        
        # 计算重力产生的力矩
        # M = r × F
        moment_sensor = np.cross(self.load_cog, gravity_sensor)
        
        # 组合力/力矩
        gravity_wrench = np.concatenate([gravity_sensor, moment_sensor])
        
        return gravity_wrench
    
    def compensate(self,
                  force_raw: np.ndarray,
                  rotation_matrix: np.ndarray) -> np.ndarray:
        """
        对原始力传感器读数进行重力补偿
        
        Args:
            force_raw: 原始力/力矩读数 (6,)
            rotation_matrix: 传感器坐标系旋转矩阵 (3x3)
        
        Returns:
            补偿后的力/力矩 (6,)
        """
        gravity_wrench = self.compute_gravity_force(rotation_matrix)
        compensated_force = force_raw - gravity_wrench
        
        return compensated_force
    
    def calibrate(self,
                 force_readings: np.ndarray,
                 rotation_matrices: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        标定负载质量和质心位置
        
        使用最小二乘法拟合
        
        Args:
            force_readings: 多个姿态下的力传感器读数 (N, 6)
            rotation_matrices: 对应的旋转矩阵 (N, 3, 3)
        
        Returns:
            (estimated_mass, estimated_cog) - 估计的质量和质心
        """
        # 简化实现：使用最小二乘法
        # 实际应使用更完善的标定方法
        
        # 构建线性方程组
        A = []
        b = []
        
        for i in range(len(force_readings)):
            R = rotation_matrices[i]
            F = force_readings[i][:3]  # 力分量
            
            # 重力在传感器坐标系下的方向
            g_sensor = R.T @ self.gravity
            
            # 构建方程：F = m * g_sensor
            A.append(g_sensor)
            b.append(F)
        
        A = np.array(A)
        b = np.array(b)
        
        # 最小二乘求解
        # 简化：仅估计质量（质心估计更复杂）
        estimated_mass = np.mean(np.linalg.norm(b, axis=1) / np.linalg.norm(self.gravity))
        estimated_cog = self.load_cog  # 占位，实际需要更复杂的估计
        
        return estimated_mass, estimated_cog

