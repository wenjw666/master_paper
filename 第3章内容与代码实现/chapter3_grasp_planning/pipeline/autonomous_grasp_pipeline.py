"""
自主抓取完整流程
整合抓取生成、多约束筛选和路径规划
"""

import numpy as np
import sys
import os
from typing import Dict, Optional, List

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grasp_generation.inference import GraspGenerator
from grasp_generation.utils.pointcloud_utils import preprocess_pointcloud
from grasp_selection.multi_constraint_filter import MultiConstraintFilter
from path_planning.grrt_connect import GRRTConnect
from path_planning.hybrid_obstacle_map import HybridObstacleMap
from obstacle_mapping.cable_mask_to_octomap import cable_mask_to_octomap


class AutonomousGraspPipeline:
    """自主抓取流水线"""
    
    def __init__(self,
                 grasp_model_path: str,
                 robot_type: str = "ur5",
                 camera_intrinsic: Optional[np.ndarray] = None,
                 assembly_direction: Optional[np.ndarray] = None):
        """
        初始化抓取流水线
        
        Args:
            grasp_model_path: Contact-GraspNet模型路径
            robot_type: 机器人类型
            camera_intrinsic: 相机内参矩阵
            assembly_direction: 装配方向向量（用于任务相容性）
        """
        self.robot_type = robot_type
        self.camera_intrinsic = camera_intrinsic
        self.assembly_direction = assembly_direction
        
        # 初始化各模块
        self.grasp_generator = GraspGenerator(
            model_path=grasp_model_path,
            num_grasps=100
        )
        
        self.grasp_filter = MultiConstraintFilter(
            robot_type=robot_type,
            assembly_direction=assembly_direction
        )
    
    def execute_grasp(self,
                     rgb_image: np.ndarray,
                     depth_image: np.ndarray,
                     connector_pose: Dict,
                     cable_mask: np.ndarray,
                     start_config: np.ndarray,
                     target_tag_id: Optional[str] = None) -> Dict:
        """
        执行完整抓取流程
        
        Args:
            rgb_image: RGB图像
            depth_image: 深度图像
            connector_pose: Ch2输出的6D位姿
            cable_mask: Ch2输出的线缆掩膜
            start_config: 机器人当前关节配置
            target_tag_id: 目标标签ID（可选）
        
        Returns:
            抓取结果 {
                'success': bool,
                'grasp_pose': {...},
                'path': [...],
                'message': str
            }
        """
        try:
            # 1. 点云预处理
            pcd = preprocess_pointcloud(
                rgb_image=rgb_image,
                depth_image=depth_image,
                camera_intrinsic=self.camera_intrinsic,
                connector_mask=None,  # 可选：使用连接器掩膜
                voxel_size=0.005
            )
            
            # 2. 生成候选抓取位姿
            candidate_grasps = self.grasp_generator.generate_grasps(
                pointcloud=pcd,
                connector_pose=connector_pose
            )
            
            if len(candidate_grasps) == 0:
                return {
                    'success': False,
                    'grasp_pose': None,
                    'path': None,
                    'message': '未生成候选抓取位姿'
                }
            
            # 3. 构建障碍物地图
            obstacle_map = self._build_obstacle_map(cable_mask, depth_image)
            
            # 4. 多约束筛选
            self.grasp_filter.cable_pointcloud = self._mask_to_pointcloud(
                cable_mask, depth_image
            )
            
            filtered_grasps = self.grasp_filter.filter_grasps(
                candidate_grasps,
                robot_current_joints=start_config
            )
            
            if len(filtered_grasps) == 0:
                return {
                    'success': False,
                    'grasp_pose': None,
                    'path': None,
                    'message': '所有候选抓取均未通过约束筛选'
                }
            
            # 5. 选择最优抓取
            best_grasp = self.grasp_filter.select_best_grasp(filtered_grasps)
            
            # 6. 路径规划
            goal_config = self._grasp_pose_to_joint_config(best_grasp)
            
            planner = GRRTConnect(
                obstacle_map=obstacle_map,
                goal_bias=0.3,
                step_size=0.05
            )
            
            path = planner.plan(
                start=start_config,
                goal=goal_config,
                joint_limits=self._get_joint_limits()
            )
            
            if path is None:
                return {
                    'success': False,
                    'grasp_pose': best_grasp,
                    'path': None,
                    'message': '路径规划失败'
                }
            
            return {
                'success': True,
                'grasp_pose': best_grasp,
                'path': path,
                'message': '抓取规划成功'
            }
            
        except Exception as e:
            return {
                'success': False,
                'grasp_pose': None,
                'path': None,
                'message': f'执行错误: {str(e)}'
            }
    
    def _build_obstacle_map(self,
                           cable_mask: np.ndarray,
                           depth_image: np.ndarray) -> HybridObstacleMap:
        """构建混合障碍物地图"""
        obstacle_map = HybridObstacleMap()
        
        # 添加刚性障碍物（示例：机舱壁）
        # 实际应从环境配置中读取
        obstacle_map.add_rigid_obstacle(
            min_bound=np.array([-0.5, -0.5, -0.5]),
            max_bound=np.array([0.5, 0.5, 0.5])
        )
        
        # 添加线缆Octomap
        if cable_mask is not None and self.camera_intrinsic is not None:
            octomap = cable_mask_to_octomap(
                cable_mask,
                depth_image,
                self.camera_intrinsic,
                resolution=0.01
            )
            if octomap is not None:
                obstacle_map.set_cable_octomap(octomap)
        
        return obstacle_map
    
    def _mask_to_pointcloud(self,
                           mask: np.ndarray,
                           depth_image: np.ndarray) -> np.ndarray:
        """将掩膜转换为点云（用于碰撞检测）"""
        from obstacle_mapping.cable_mask_to_octomap import cable_mask_to_pointcloud
        
        pcd = cable_mask_to_pointcloud(
            mask, depth_image, self.camera_intrinsic
        )
        
        if len(pcd.points) == 0:
            return np.array([])
        
        return np.asarray(pcd.points)
    
    def _grasp_pose_to_joint_config(self, grasp_pose: Dict) -> np.ndarray:
        """将抓取位姿转换为关节配置（使用IK）"""
        from grasp_selection.ik_solver import IKSolver
        
        ik_solver = IKSolver(robot_type=self.robot_type)
        target_pose = {
            'translation': grasp_pose['translation'],
            'rotation': grasp_pose['rotation']
        }
        
        solutions = ik_solver.solve_ik(target_pose)
        if len(solutions) > 0:
            return solutions[0]
        else:
            # 返回默认配置（应处理错误）
            return np.zeros(6)
    
    def _get_joint_limits(self) -> Dict:
        """获取关节限位"""
        return {
            'lower': np.array([-np.pi] * 6),
            'upper': np.array([np.pi] * 6)
        }

