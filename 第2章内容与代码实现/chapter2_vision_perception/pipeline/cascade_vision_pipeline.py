"""
级联式视觉感知完整流程
整合YOLOv8-seg、DeepLabV3+和位姿估计模块
"""

import numpy as np
import cv2
from typing import Dict, Optional, Tuple
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yolov8_seg.inference import YOLOv8SegInference
# from deeplabv3_keypoints.inference import DeepLabV3KeypointInference  # 待实现
from pose_estimation.ransac_pnp import RANSACPnPSolver


class CascadeVisionPipeline:
    """级联式视觉感知流水线"""
    
    def __init__(self,
                 yolov8_model_path: str,
                 deeplab_model_path: Optional[str] = None,
                 camera_intrinsic: Optional[str] = None,
                 camera_matrix: Optional[np.ndarray] = None,
                 model_points_3d: Optional[np.ndarray] = None):
        """
        初始化流水线
        
        Args:
            yolov8_model_path: YOLOv8-seg模型路径
            deeplab_model_path: DeepLabV3+模型路径（可选）
            camera_intrinsic: 相机内参文件路径（YAML格式）
            camera_matrix: 相机内参矩阵（3x3），如果提供了camera_intrinsic则忽略
            model_points_3d: 3D模型关键点（物体坐标系）
        """
        # 初始化YOLOv8
        self.yolo = YOLOv8SegInference(yolov8_model_path)
        
        # 初始化DeepLabV3+（待实现）
        self.deeplab = None
        if deeplab_model_path:
            # self.deeplab = DeepLabV3KeypointInference(deeplab_model_path)
            pass
        
        # 加载相机内参
        if camera_intrinsic:
            import yaml
            with open(camera_intrinsic, 'r') as f:
                cam_data = yaml.safe_load(f)
            self.camera_matrix = np.array(cam_data['camera_matrix'])
            self.dist_coeffs = np.array(cam_data.get('dist_coeffs', [0]*5))
        elif camera_matrix is not None:
            self.camera_matrix = camera_matrix
            self.dist_coeffs = np.zeros(5)
        else:
            raise ValueError("必须提供camera_intrinsic或camera_matrix")
        
        # 3D模型关键点
        self.model_points_3d = model_points_3d
        if model_points_3d is None:
            # 默认关键点（需根据实际CAD模型修改）
            self.model_points_3d = np.array([
                [0, 0, 0],      # 定位孔1
                [10, 0, 0],     # 定位孔2
                [5, 10, 0],     # 定位孔3
                [5, 5, -5],     # 线缆根部
            ], dtype=np.float32)
        
        # 初始化位姿解算器
        self.pose_solver = RANSACPnPSolver(
            camera_matrix=self.camera_matrix,
            dist_coeffs=self.dist_coeffs,
            reprojection_threshold=3.0
        )
    
    def inference(self, 
                 rgb_image: np.ndarray,
                 depth_image: Optional[np.ndarray] = None,
                 target_tag_id: Optional[str] = None) -> Dict:
        """
        完整推理流程
        
        Args:
            rgb_image: RGB图像 (H, W, 3)
            depth_image: 深度图像 (可选)
            target_tag_id: 目标标签ID（可选）
        
        Returns:
            结果字典：
            {
                'tag_id': str,              # 标签ID
                'pose_6d': {                # 6D位姿
                    'R': np.array(3x3),     # 旋转矩阵
                    't': np.array(3,)       # 平移向量
                },
                'cable_mask': np.array,     # 线缆掩膜
                'cable_vector': np.array(3,), # 线缆方向向量
                'keypoints_2d': [...],      # 2D关键点坐标
                'confidence': float         # 整体置信度
            }
        """
        # 第一步：YOLOv8-seg检测
        yolo_results = self.yolo.predict(rgb_image, target_tag_id=target_tag_id)
        
        if len(yolo_results['boxes']) == 0:
            return {
                'tag_id': None,
                'pose_6d': None,
                'cable_mask': None,
                'cable_vector': None,
                'keypoints_2d': None,
                'confidence': 0.0
            }
        
        # 选择置信度最高的检测结果
        best_idx = np.argmax(yolo_results['scores'])
        best_box = yolo_results['boxes'][best_idx]
        best_tag_id = yolo_results['tag_ids'][best_idx]
        cable_mask = yolo_results['cable_mask']
        
        # 提取ROI
        roi_image, crop_coords = self.yolo.extract_roi(rgb_image, best_box, margin=50)
        
        # 第二步：DeepLabV3+关键点提取（待实现）
        keypoints_2d = None
        if self.deeplab is not None:
            # keypoints_2d, cable_mask_roi = self.deeplab.predict(roi_image)
            # 将ROI坐标转换回原图坐标
            # keypoints_2d[:, 0] += crop_coords[0]  # x坐标
            # keypoints_2d[:, 1] += crop_coords[1]  # y坐标
            pass
        else:
            # 临时：使用边界框中心作为关键点（实际应使用DeepLabV3+）
            x1, y1, x2, y2 = best_box.astype(int)
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            keypoints_2d = np.array([
                [center_x - 5, center_y - 5],  # 定位孔1（临时）
                [center_x + 5, center_y - 5],  # 定位孔2（临时）
                [center_x, center_y + 5],      # 定位孔3（临时）
                [center_x, center_y]           # 线缆根部（临时）
            ], dtype=np.float32)
        
        # 第三步：位姿解算
        success, R, t, inliers = self.pose_solver.solve(
            self.model_points_3d,
            keypoints_2d
        )
        
        if not success:
            return {
                'tag_id': best_tag_id,
                'pose_6d': None,
                'cable_mask': cable_mask,
                'cable_vector': None,
                'keypoints_2d': keypoints_2d,
                'confidence': yolo_results['scores'][best_idx]
            }
        
        # 第四步：计算线缆方向向量
        cable_vector = self._compute_cable_vector(cable_mask)
        
        return {
            'tag_id': best_tag_id,
            'pose_6d': {
                'R': R,
                't': t,
                'inliers': inliers
            },
            'cable_mask': cable_mask,
            'cable_vector': cable_vector,
            'keypoints_2d': keypoints_2d,
            'confidence': yolo_results['scores'][best_idx]
        }
    
    def _compute_cable_vector(self, cable_mask: np.ndarray) -> np.ndarray:
        """
        从线缆掩膜计算方向向量
        
        Args:
            cable_mask: 线缆二值掩膜
        
        Returns:
            线缆方向向量 (3,)
        """
        if cable_mask is None or cable_mask.sum() == 0:
            return np.array([0, 0, 1], dtype=np.float32)  # 默认向下
        
        # 找到线缆骨架或主方向
        # 简化实现：计算掩膜的主轴方向
        coords = np.where(cable_mask > 0)
        if len(coords[0]) == 0:
            return np.array([0, 0, 1], dtype=np.float32)
        
        y_coords = coords[0]
        x_coords = coords[1]
        
        # 使用PCA找到主方向
        points = np.column_stack([x_coords, y_coords])
        mean = np.mean(points, axis=0)
        points_centered = points - mean
        
        if len(points_centered) < 2:
            return np.array([0, 0, 1], dtype=np.float32)
        
        # SVD分解
        U, S, Vt = np.linalg.svd(points_centered, full_matrices=False)
        direction_2d = Vt[0]  # 第一主成分
        
        # 转换为3D方向向量（假设线缆在XY平面内）
        # 这里简化处理，实际应根据线缆根部位置和延伸方向计算
        cable_vector = np.array([direction_2d[0], direction_2d[1], 0], dtype=np.float32)
        cable_vector = cable_vector / (np.linalg.norm(cable_vector) + 1e-6)
        
        return cable_vector

