"""
任务相容性评分模块
评估抓取姿态是否有利于后续装配操作
"""

import numpy as np
from typing import Optional


class TaskCompatibilityScorer:
    """任务相容性评分器"""
    
    def __init__(self, assembly_direction: Optional[np.ndarray] = None):
        """
        初始化评分器
        
        Args:
            assembly_direction: 装配方向向量（插座轴线方向）
        """
        self.assembly_direction = assembly_direction
        if assembly_direction is not None:
            self.assembly_direction = assembly_direction / (np.linalg.norm(assembly_direction) + 1e-6)
    
    def compute_alignment_score(self,
                               grasp_direction: np.ndarray,
                               assembly_direction: Optional[np.ndarray] = None) -> float:
        """
        计算抓取方向与装配方向的对齐分数
        
        S_align = (v_grasp · v_assembly) / (||v_grasp|| ||v_assembly||)
        
        Args:
            grasp_direction: 抓取方向向量（夹爪Z轴）
            assembly_direction: 装配方向向量（如果为None，使用初始化时的值）
        
        Returns:
            对齐分数 [0, 1]（归一化后的余弦相似度）
        """
        if assembly_direction is None:
            assembly_direction = self.assembly_direction
        
        if assembly_direction is None:
            return 0.5  # 无装配方向信息，给中等分数
        
        # 归一化抓取方向
        grasp_direction = grasp_direction / (np.linalg.norm(grasp_direction) + 1e-6)
        
        # 计算余弦相似度
        cosine_sim = np.dot(grasp_direction, assembly_direction)
        
        # 归一化到[0, 1]
        align_score = (cosine_sim + 1.0) / 2.0
        
        return align_score
    
    def check_pin_occlusion(self,
                           grasp_pose: dict,
                           connector_pin_region: Optional[np.ndarray] = None) -> bool:
        """
        检查夹爪是否遮挡连接器针脚区域
        
        Args:
            grasp_pose: 抓取位姿
            connector_pin_region: 针脚区域点云（可选）
        
        Returns:
            是否遮挡（True表示遮挡，应避免）
        """
        # 简化实现：检查抓取位置是否在针脚区域上方
        # 实际应使用更精确的几何检查
        
        if connector_pin_region is None:
            return False  # 无针脚区域信息，假设不遮挡
        
        grasp_pos = grasp_pose['translation']
        
        # 检查抓取位置是否在针脚区域附近
        # 这里简化处理，实际应检查夹爪几何是否与针脚区域重叠
        return False  # 占位实现

