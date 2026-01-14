"""
多约束抓取点筛选
综合考虑运动学可行性、避障安全性和任务相容性
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
import sys
import os

# 导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from grasp_selection.ik_solver import IKSolver
from grasp_selection.collision_checker import CollisionChecker
from grasp_selection.task_compatibility import TaskCompatibilityScorer


class MultiConstraintFilter:
    """多约束抓取筛选器"""
    
    def __init__(self,
                 robot_type: str = "ur5",
                 cable_pointcloud: Optional[np.ndarray] = None,
                 assembly_direction: Optional[np.ndarray] = None,
                 weights: Optional[Dict[str, float]] = None):
        """
        初始化多约束筛选器
        
        Args:
            robot_type: 机器人类型（如"ur5"）
            cable_pointcloud: 线缆点云（来自Ch2，用于避障检测）
            assembly_direction: 装配方向向量（用于任务相容性）
            weights: 评分权重 {'quality': 0.4, 'clearance': 0.3, 'align': 0.3}
        """
        self.robot_type = robot_type
        self.cable_pointcloud = cable_pointcloud
        self.assembly_direction = assembly_direction
        
        # 默认权重
        self.weights = weights or {
            'quality': 0.4,
            'clearance': 0.3,
            'align': 0.3
        }
        
        # 初始化子模块
        self.ik_solver = IKSolver(robot_type=robot_type)
        self.collision_checker = CollisionChecker()
        self.task_scorer = TaskCompatibilityScorer()
        
        # 安全距离阈值（米）
        self.d_threshold = 0.02
    
    def filter_grasps(self,
                     candidate_grasps: List[Dict],
                     robot_current_joints: Optional[np.ndarray] = None) -> List[Dict]:
        """
        多约束筛选候选抓取
        
        Args:
            candidate_grasps: 候选抓取列表
            robot_current_joints: 机器人当前关节角度（可选）
        
        Returns:
            筛选后的抓取列表（按综合评分排序）
        """
        filtered_grasps = []
        
        for grasp in candidate_grasps:
            # 准则1: 运动学可行性
            if not self._check_kinematic_feasibility(grasp):
                continue
            
            # 准则2: 避障检测
            if not self._check_collision_avoidance(grasp):
                continue
            
            # 准则3: 任务相容性（计算评分）
            align_score = self._compute_task_compatibility(grasp)
            
            # 计算综合评分
            quality_score = grasp.get('score', 0.0)
            clearance_score = self._compute_clearance_score(grasp)
            
            total_score = (
                self.weights['quality'] * quality_score +
                self.weights['clearance'] * clearance_score +
                self.weights['align'] * align_score
            )
            
            grasp['total_score'] = total_score
            grasp['quality_score'] = quality_score
            grasp['clearance_score'] = clearance_score
            grasp['align_score'] = align_score
            
            filtered_grasps.append(grasp)
        
        # 按综合评分排序
        filtered_grasps.sort(key=lambda x: x['total_score'], reverse=True)
        
        return filtered_grasps
    
    def _check_kinematic_feasibility(self, grasp: Dict) -> bool:
        """
        检查运动学可行性
        
        Args:
            grasp: 抓取位姿
        
        Returns:
            是否可行
        """
        # 构建目标位姿（SE(3)）
        target_pose = {
            'translation': grasp['translation'],
            'rotation': grasp['rotation']
        }
        
        # 求解逆运动学
        ik_solutions = self.ik_solver.solve_ik(target_pose)
        
        # 检查是否有解且关节角度在限位内
        if len(ik_solutions) > 0:
            for solution in ik_solutions:
                if self.ik_solver.check_joint_limits(solution):
                    return True
        
        return False
    
    def _check_collision_avoidance(self, grasp: Dict) -> bool:
        """
        检查避障安全性
        
        Args:
            grasp: 抓取位姿
        
        Returns:
            是否安全（无碰撞）
        """
        if self.cable_pointcloud is None or len(self.cable_pointcloud) == 0:
            return True  # 没有障碍物，默认安全
        
        # 计算夹爪在该位姿下的占用体积
        gripper_points = self._get_gripper_points(grasp)
        
        # 与线缆点云进行碰撞检测
        min_distance = self.collision_checker.compute_min_distance(
            gripper_points,
            self.cable_pointcloud
        )
        
        # 安全距离检查
        return min_distance >= self.d_threshold
    
    def _compute_clearance_score(self, grasp: Dict) -> float:
        """
        计算避障安全分数
        
        S_clearance = d_min / d_threshold
        
        Args:
            grasp: 抓取位姿
        
        Returns:
            安全分数 [0, 1+]
        """
        if self.cable_pointcloud is None or len(self.cable_pointcloud) == 0:
            return 1.0  # 没有障碍物，满分
        
        gripper_points = self._get_gripper_points(grasp)
        min_distance = self.collision_checker.compute_min_distance(
            gripper_points,
            self.cable_pointcloud
        )
        
        # 归一化到[0, 1+]
        score = min(min_distance / self.d_threshold, 2.0) / 2.0
        return score
    
    def _compute_task_compatibility(self, grasp: Dict) -> float:
        """
        计算任务相容性分数
        
        S_align = (v_grasp · v_assembly) / (||v_grasp|| ||v_assembly||)
        
        Args:
            grasp: 抓取位姿
        
        Returns:
            对齐分数 [-1, 1]
        """
        if self.assembly_direction is None:
            return 0.5  # 无装配方向信息，给中等分数
        
        # 提取抓取方向（夹爪Z轴）
        R = grasp['rotation']
        grasp_direction = R[:, 2]  # Z轴方向
        
        # 归一化
        grasp_direction = grasp_direction / (np.linalg.norm(grasp_direction) + 1e-6)
        assembly_direction = self.assembly_direction / (np.linalg.norm(self.assembly_direction) + 1e-6)
        
        # 计算余弦相似度
        align_score = np.dot(grasp_direction, assembly_direction)
        
        # 归一化到[0, 1]
        align_score = (align_score + 1.0) / 2.0
        
        return align_score
    
    def _get_gripper_points(self, grasp: Dict) -> np.ndarray:
        """
        计算夹爪在给定位姿下的占用点云
        
        Args:
            grasp: 抓取位姿
        
        Returns:
            夹爪点云 (N, 3)
        """
        # 简化实现：使用夹爪的简化几何模型
        # 实际应使用真实的夹爪CAD模型
        
        R = grasp['rotation']
        t = grasp['translation']
        width = grasp.get('width', 0.05)
        
        # 定义夹爪的简化几何（两个手指）
        finger_length = 0.1  # 手指长度（米）
        finger_width = 0.02  # 手指宽度
        
        # 生成夹爪点云（简化：两个长方体）
        points = []
        
        # 左手指
        for x in np.linspace(-width/2 - finger_width, -width/2, 5):
            for y in np.linspace(0, finger_length, 5):
                for z in np.linspace(-finger_width/2, finger_width/2, 3):
                    points.append([x, y, z])
        
        # 右手指
        for x in np.linspace(width/2, width/2 + finger_width, 5):
            for y in np.linspace(0, finger_length, 5):
                for z in np.linspace(-finger_width/2, finger_width/2, 3):
                    points.append([x, y, z])
        
        points = np.array(points)
        
        # 变换到世界坐标系
        points_world = (R @ points.T).T + t
        
        return points_world
    
    def select_best_grasp(self, filtered_grasps: List[Dict]) -> Optional[Dict]:
        """
        选择最优抓取位姿
        
        Args:
            filtered_grasps: 筛选后的抓取列表（已按评分排序）
        
        Returns:
            最优抓取位姿，如果列表为空则返回None
        """
        if len(filtered_grasps) == 0:
            return None
        
        return filtered_grasps[0]  # 已按评分排序，第一个即最优

