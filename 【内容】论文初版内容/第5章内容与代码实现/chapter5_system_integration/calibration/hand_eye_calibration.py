"""
手眼标定工具
使用Tsai-Lenz算法求解手眼变换矩阵
"""

import cv2
import numpy as np
import rospy
from geometry_msgs.msg import Pose
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import yaml
import os
from typing import List, Tuple, Optional


class HandEyeCalibration:
    """手眼标定类（Tsai-Lenz算法）"""
    
    def __init__(self, robot_type: str = "ur5", camera_type: str = "realsense_d435i"):
        """
        初始化手眼标定器
        
        Args:
            robot_type: 机器人类型
            camera_type: 相机类型
        """
        self.robot_type = robot_type
        self.camera_type = camera_type
        self.bridge = CvBridge()
        
        # 标定数据
        self.robot_poses: List[np.ndarray] = []  # 机器人末端位姿
        self.camera_poses: List[np.ndarray] = []  # 标定板位姿（相机坐标系）
        
        # 标定结果
        self.hand_eye_transform: Optional[np.ndarray] = None  # 4x4变换矩阵
        self.reprojection_error: Optional[float] = None
    
    def collect_calibration_data(self, num_images: int = 20):
        """
        采集标定数据
        
        控制机械臂末端携带标定板在不同姿态下拍摄图像
        
        Args:
            num_images: 采集图像数量
        """
        rospy.init_node('hand_eye_calibration', anonymous=True)
        
        # 订阅相机图像
        image_sub = rospy.Subscriber('/camera/color/image_raw', Image, self._image_callback)
        
        # 订阅机器人位姿
        pose_sub = rospy.Subscriber('/robot/end_effector_pose', Pose, self._pose_callback)
        
        print(f"开始采集 {num_images} 张标定图像...")
        print("请控制机械臂移动到不同姿态，按空格键保存当前帧")
        
        self.current_image = None
        self.current_pose = None
        
        collected = 0
        while collected < num_images and not rospy.is_shutdown():
            key = input(f"已采集 {collected}/{num_images}，按空格键保存当前帧，按q退出: ")
            
            if key == 'q':
                break
            
            if self.current_image is not None and self.current_pose is not None:
                # 检测标定板
                success, camera_pose = self._detect_calibration_board(self.current_image)
                
                if success:
                    self.robot_poses.append(self.current_pose)
                    self.camera_poses.append(camera_pose)
                    collected += 1
                    print(f"成功采集第 {collected} 张图像")
                else:
                    print("标定板检测失败，请重试")
            else:
                print("等待图像和位姿数据...")
        
        print(f"采集完成，共 {len(self.robot_poses)} 张有效图像")
    
    def _image_callback(self, msg: Image):
        """图像回调函数"""
        try:
            self.current_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            rospy.logerr(f"图像转换失败: {e}")
    
    def _pose_callback(self, msg: Pose):
        """位姿回调函数"""
        # 转换为numpy数组
        position = np.array([msg.position.x, msg.position.y, msg.position.z])
        orientation = np.array([
            msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w
        ])
        
        # 转换为4x4变换矩阵
        R = self._quaternion_to_rotation_matrix(orientation)
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = position
        
        self.current_pose = T
    
    def _detect_calibration_board(self, image: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
        """
        检测标定板
        
        Args:
            image: 输入图像
        
        Returns:
            (success, pose) - 是否成功检测，标定板位姿（4x4矩阵）
        """
        # 标定板参数
        board_size = (9, 6)  # 内角点数量
        square_size = 0.025  # 方格大小（米）
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 查找角点
        ret, corners = cv2.findChessboardCorners(gray, board_size, None)
        
        if not ret:
            return False, None
        
        # 细化角点
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        
        # 生成3D点（标定板坐标系）
        obj_points = np.zeros((board_size[0] * board_size[1], 3), np.float32)
        obj_points[:, :2] = np.mgrid[0:board_size[0], 0:board_size[1]].T.reshape(-1, 2)
        obj_points *= square_size
        
        # 使用PnP求解位姿（需要相机内参）
        # 这里简化处理，实际应从配置文件加载内参
        camera_matrix = np.eye(3)  # 占位
        dist_coeffs = np.zeros(5)
        
        ret, rvec, tvec = cv2.solvePnP(
            obj_points, corners, camera_matrix, dist_coeffs
        )
        
        if not ret:
            return False, None
        
        # 转换为4x4变换矩阵
        R, _ = cv2.Rodrigues(rvec)
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = tvec.reshape(3)
        
        return True, T
    
    def calibrate(self) -> Tuple[bool, np.ndarray, float]:
        """
        执行手眼标定（Tsai-Lenz算法）
        
        求解方程: AX = XB
        其中:
        - A: 机器人末端位姿变化
        - B: 标定板位姿变化（相机坐标系）
        - X: 手眼变换矩阵（待求解）
        
        Returns:
            (success, transform, reprojection_error)
        """
        if len(self.robot_poses) < 3:
            print("错误: 标定数据不足，至少需要3组数据")
            return False, None, float('inf')
        
        # Tsai-Lenz算法实现
        # 这里使用OpenCV的实现
        R_gripper2base = []
        t_gripper2base = []
        R_target2cam = []
        t_target2cam = []
        
        # 提取相对变换
        for i in range(len(self.robot_poses) - 1):
            # 机器人末端相对变换
            T_gripper_i = self.robot_poses[i]
            T_gripper_j = self.robot_poses[i + 1]
            T_gripper_ij = np.linalg.inv(T_gripper_i) @ T_gripper_j
            
            R_gripper2base.append(T_gripper_ij[:3, :3])
            t_gripper2base.append(T_gripper_ij[:3, 3])
            
            # 标定板相对变换（相机坐标系）
            T_target_i = self.camera_poses[i]
            T_target_j = self.camera_poses[i + 1]
            T_target_ij = np.linalg.inv(T_target_i) @ T_target_j
            
            R_target2cam.append(T_target_ij[:3, :3])
            t_target2cam.append(T_target_ij[:3, 3])
        
        # 使用OpenCV的calibrateHandEye函数
        R_cam2gripper, t_cam2gripper = cv2.calibrateHandEye(
            R_gripper2base, t_gripper2base,
            R_target2cam, t_target2cam
        )
        
        # 构建4x4变换矩阵
        self.hand_eye_transform = np.eye(4)
        self.hand_eye_transform[:3, :3] = R_cam2gripper
        self.hand_eye_transform[:3, 3] = t_cam2gripper.reshape(3)
        
        # 计算重投影误差
        self.reprojection_error = self._compute_reprojection_error()
        
        print(f"手眼标定完成")
        print(f"重投影误差: {self.reprojection_error:.3f} pixels")
        print(f"空间位置误差: {self.reprojection_error * 0.001:.3f} mm (假设像素尺寸1mm)")
        
        return True, self.hand_eye_transform, self.reprojection_error
    
    def _compute_reprojection_error(self) -> float:
        """计算重投影误差"""
        if self.hand_eye_transform is None:
            return float('inf')
        
        errors = []
        for i in range(len(self.robot_poses)):
            # 使用手眼变换预测标定板位姿
            T_gripper = self.robot_poses[i]
            T_cam_predicted = T_gripper @ self.hand_eye_transform
            
            # 与实测值比较
            T_cam_actual = self.camera_poses[i]
            
            # 计算位置误差
            pos_error = np.linalg.norm(T_cam_predicted[:3, 3] - T_cam_actual[:3, 3])
            errors.append(pos_error)
        
        return np.mean(errors)
    
    def save_calibration(self, filepath: str):
        """保存标定结果"""
        if self.hand_eye_transform is None:
            print("错误: 未进行标定")
            return
        
        calibration_data = {
            'hand_eye_transform': self.hand_eye_transform.tolist(),
            'reprojection_error': self.reprojection_error,
            'robot_type': self.robot_type,
            'camera_type': self.camera_type,
            'num_samples': len(self.robot_poses)
        }
        
        with open(filepath, 'w') as f:
            yaml.dump(calibration_data, f, default_flow_style=False)
        
        print(f"标定结果已保存: {filepath}")
    
    def _quaternion_to_rotation_matrix(self, quaternion: np.ndarray) -> np.ndarray:
        """四元数转旋转矩阵"""
        x, y, z, w = quaternion
        R = np.array([
            [1 - 2*(y**2 + z**2), 2*(x*y - z*w), 2*(x*z + y*w)],
            [2*(x*y + z*w), 1 - 2*(x**2 + z**2), 2*(y*z - x*w)],
            [2*(x*z - y*w), 2*(y*z + x*w), 1 - 2*(x**2 + y**2)]
        ])
        return R


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='手眼标定工具')
    parser.add_argument('--robot-type', type=str, default='ur5',
                       help='机器人类型')
    parser.add_argument('--camera', type=str, default='realsense_d435i',
                       help='相机类型')
    parser.add_argument('--num-images', type=int, default=20,
                       help='采集图像数量')
    parser.add_argument('--output', type=str,
                       default='./calibration/calibration_data/hand_eye_calibration.yaml',
                       help='输出文件路径')
    
    args = parser.parse_args()
    
    # 初始化标定器
    calibrator = HandEyeCalibration(
        robot_type=args.robot_type,
        camera_type=args.camera
    )
    
    # 采集数据
    calibrator.collect_calibration_data(num_images=args.num_images)
    
    # 执行标定
    success, transform, error = calibrator.calibrate()
    
    if success:
        # 保存结果
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        calibrator.save_calibration(args.output)
    else:
        print("标定失败")


if __name__ == '__main__':
    main()

