"""
RANSAC + EPnP 位姿解算
结合RANSAC外点剔除和EPnP算法，提高位姿估计鲁棒性
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List
import random


class RANSACPnPSolver:
    """RANSAC + EPnP位姿解算器"""
    
    def __init__(self, 
                 camera_matrix: np.ndarray,
                 dist_coeffs: Optional[np.ndarray] = None,
                 reprojection_threshold: float = 3.0,
                 max_iterations: int = 1000,
                 confidence: float = 0.99,
                 min_inliers: int = 4):
        """
        初始化RANSAC PnP求解器
        
        Args:
            camera_matrix: 相机内参矩阵 (3x3)
            dist_coeffs: 畸变系数 (可选)
            reprojection_threshold: 重投影误差阈值（像素）
            max_iterations: 最大迭代次数
            confidence: 置信度
            min_inliers: 最小内点数量
        """
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs if dist_coeffs is not None else np.zeros(5)
        self.reprojection_threshold = reprojection_threshold
        self.max_iterations = max_iterations
        self.confidence = confidence
        self.min_inliers = min_inliers
    
    def compute_reprojection_error(self, 
                                   object_points: np.ndarray,
                                   image_points: np.ndarray,
                                   rvec: np.ndarray,
                                   tvec: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        计算重投影误差
        
        Args:
            object_points: 3D点 (N, 3)
            image_points: 2D点 (N, 2)
            rvec: 旋转向量
            tvec: 平移向量
        
        Returns:
            重投影误差数组和平均误差
        """
        # 投影3D点到2D
        projected_points, _ = cv2.projectPoints(
            object_points, rvec, tvec, 
            self.camera_matrix, self.dist_coeffs
        )
        projected_points = projected_points.reshape(-1, 2)
        
        # 计算误差
        errors = np.linalg.norm(image_points - projected_points, axis=1)
        mean_error = np.mean(errors)
        
        return errors, mean_error
    
    def solve(self, 
              object_points: np.ndarray,
              image_points: np.ndarray) -> Tuple[bool, np.ndarray, np.ndarray, List[int]]:
        """
        使用RANSAC + EPnP解算位姿
        
        Args:
            object_points: 3D模型点 (N, 3)
            image_points: 2D图像点 (N, 2)
        
        Returns:
            (success, R, t, inliers)
            - success: 是否成功
            - R: 旋转矩阵 (3x3)
            - t: 平移向量 (3,)
            - inliers: 内点索引列表
        """
        n_points = len(object_points)
        
        if n_points < 4:
            return False, None, None, []
        
        best_inliers = []
        best_rvec = None
        best_tvec = None
        best_inlier_count = 0
        
        # RANSAC迭代
        for iteration in range(self.max_iterations):
            # 随机采样4个点（EPnP最小解集）
            if n_points == 4:
                sample_indices = list(range(4))
            else:
                sample_indices = random.sample(range(n_points), 4)
            
            sample_object_points = object_points[sample_indices]
            sample_image_points = image_points[sample_indices]
            
            # 使用EPnP解算
            success, rvec, tvec = cv2.solvePnP(
                sample_object_points,
                sample_image_points,
                self.camera_matrix,
                self.dist_coeffs,
                flags=cv2.SOLVEPNP_EPNP
            )
            
            if not success:
                continue
            
            # 计算所有点的重投影误差
            errors, _ = self.compute_reprojection_error(
                object_points, image_points, rvec, tvec
            )
            
            # 判定内点
            inliers = np.where(errors < self.reprojection_threshold)[0].tolist()
            inlier_count = len(inliers)
            
            # 更新最佳模型
            if inlier_count > best_inlier_count:
                best_inlier_count = inlier_count
                best_inliers = inliers
                best_rvec = rvec
                best_tvec = tvec
        
        # 检查是否找到足够的内点
        if best_inlier_count < self.min_inliers:
            return False, None, None, []
        
        # 使用所有内点重新解算（提高精度）
        if len(best_inliers) > 4:
            inlier_object_points = object_points[best_inliers]
            inlier_image_points = image_points[best_inliers]
            
            success, rvec_refined, tvec_refined = cv2.solvePnP(
                inlier_object_points,
                inlier_image_points,
                self.camera_matrix,
                self.dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE,
                useExtrinsicGuess=True,
                rvec=best_rvec,
                tvec=best_tvec
            )
            
            if success:
                best_rvec = rvec_refined
                best_tvec = tvec_refined
        
        # 转换为旋转矩阵
        R, _ = cv2.Rodrigues(best_rvec)
        
        return True, R, best_tvec.reshape(3,), best_inliers
    
    def solve_refined(self,
                     object_points: np.ndarray,
                     image_points: np.ndarray) -> Tuple[bool, np.ndarray, np.ndarray, float]:
        """
        解算位姿并进行非线性优化
        
        Args:
            object_points: 3D模型点
            image_points: 2D图像点
        
        Returns:
            (success, R, t, reprojection_error)
        """
        success, R, t, inliers = self.solve(object_points, image_points)
        
        if not success:
            return False, None, None, float('inf')
        
        # 使用内点进行优化
        if len(inliers) > 0:
            inlier_object_points = object_points[inliers]
            inlier_image_points = image_points[inliers]
            
            # 转换为旋转向量
            rvec, _ = cv2.Rodrigues(R)
            
            # 非线性优化（Levenberg-Marquardt）
            rvec_opt, tvec_opt = cv2.solvePnPRefineLM(
                inlier_object_points,
                inlier_image_points,
                self.camera_matrix,
                self.dist_coeffs,
                rvec,
                t.reshape(3, 1)
            )
            
            # 转换回旋转矩阵
            R_opt, _ = cv2.Rodrigues(rvec_opt)
            t_opt = tvec_opt.reshape(3,)
            
            # 计算最终重投影误差
            _, mean_error = self.compute_reprojection_error(
                inlier_object_points, inlier_image_points, rvec_opt, tvec_opt
            )
            
            return True, R_opt, t_opt, mean_error
        
        return success, R, t, 0.0

