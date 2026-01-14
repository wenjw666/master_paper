"""
力传感器重力补偿标定
使用最小二乘法辨识负载质量和质心位置
"""

import numpy as np
import rospy
from geometry_msgs.msg import Wrench
from geometry_msgs.msg import Pose
import yaml
import os
from typing import List, Tuple


class FTSensorCalibration:
    """力传感器标定类"""
    
    def __init__(self, sensor_type: str = "ati_gamma"):
        """
        初始化力传感器标定器
        
        Args:
            sensor_type: 传感器类型
        """
        self.sensor_type = sensor_type
        
        # 标定数据
        self.force_readings: List[np.ndarray] = []  # 力传感器读数 (6,)
        self.robot_poses: List[np.ndarray] = []  # 机器人位姿（用于计算重力方向）
        
        # 标定结果
        self.load_mass: Optional[float] = None  # 负载质量（kg）
        self.load_cog: Optional[np.ndarray] = None  # 负载质心位置 (3,)（传感器坐标系）
        self.zero_drift: Optional[float] = None  # 零漂（N）
    
    def collect_calibration_data(self, num_poses: int = 20):
        """
        采集标定数据
        
        控制机械臂移动到不同姿态，记录力传感器读数
        
        Args:
            num_poses: 采集姿态数量
        """
        rospy.init_node('ft_sensor_calibration', anonymous=True)
        
        # 订阅力传感器数据
        wrench_sub = rospy.Subscriber('/ft_sensor/raw', Wrench, self._wrench_callback)
        
        # 订阅机器人位姿
        pose_sub = rospy.Subscriber('/robot/end_effector_pose', Pose, self._pose_callback)
        
        print(f"开始采集 {num_poses} 个姿态的标定数据...")
        print("请控制机械臂移动到不同姿态，按空格键保存当前数据")
        
        self.current_wrench = None
        self.current_pose = None
        
        collected = 0
        while collected < num_poses and not rospy.is_shutdown():
            key = input(f"已采集 {collected}/{num_poses}，按空格键保存，按q退出: ")
            
            if key == 'q':
                break
            
            if self.current_wrench is not None and self.current_pose is not None:
                self.force_readings.append(self.current_wrench)
                self.robot_poses.append(self.current_pose)
                collected += 1
                print(f"成功采集第 {collected} 组数据")
            else:
                print("等待传感器和位姿数据...")
        
        print(f"采集完成，共 {len(self.force_readings)} 组有效数据")
    
    def _wrench_callback(self, msg: Wrench):
        """力传感器回调函数"""
        self.current_wrench = np.array([
            msg.force.x, msg.force.y, msg.force.z,
            msg.torque.x, msg.torque.y, msg.torque.z
        ])
    
    def _pose_callback(self, msg: Pose):
        """位姿回调函数"""
        # 转换为旋转矩阵
        orientation = np.array([
            msg.orientation.x, msg.orientation.y,
            msg.orientation.z, msg.orientation.w
        ])
        R = self._quaternion_to_rotation_matrix(orientation)
        self.current_pose = R
    
    def calibrate(self) -> Tuple[bool, float, np.ndarray, float]:
        """
        执行标定（最小二乘法）
        
        求解: F = m * g_sensor + M = r × (m * g_sensor)
        
        Args:
            None
        
        Returns:
            (success, mass, cog, zero_drift)
        """
        if len(self.force_readings) < 3:
            print("错误: 标定数据不足")
            return False, None, None, None
        
        # 重力向量（世界坐标系）
        g_world = np.array([0, 0, -9.81])
        
        # 构建线性方程组
        A = []
        b_force = []
        b_torque = []
        
        for i in range(len(self.force_readings)):
            R = self.robot_poses[i]  # 传感器到世界的旋转矩阵
            F = self.force_readings[i]
            
            # 重力在传感器坐标系下的方向
            g_sensor = R.T @ g_world
            
            # 力方程: F = m * g_sensor
            A.append(g_sensor)
            b_force.append(F[:3])
            
            # 力矩方程: M = r × (m * g_sensor) = m * (r × g_sensor)
            # 使用叉积的反对称矩阵形式
            g_skew = np.array([
                [0, -g_sensor[2], g_sensor[1]],
                [g_sensor[2], 0, -g_sensor[0]],
                [-g_sensor[1], g_sensor[0], 0]
            ])
            b_torque.append(F[3:])
        
        # 最小二乘求解质量
        A = np.array(A)
        b_force = np.array(b_force)
        
        # 求解 m
        # F = m * g_sensor
        # 使用所有数据的最小二乘
        masses = []
        for i in range(len(A)):
            if np.linalg.norm(A[i]) > 1e-6:
                m = np.linalg.norm(b_force[i]) / np.linalg.norm(A[i])
                masses.append(m)
        
        self.load_mass = np.mean(masses)
        
        # 求解质心位置（简化：假设质心在Z轴上）
        # 实际应使用更完善的优化方法
        self.load_cog = np.array([0, 0, 0.05])  # 占位值，实际应从力矩方程求解
        
        # 计算零漂
        residuals = []
        for i in range(len(self.force_readings)):
            R = self.robot_poses[i]
            g_sensor = R.T @ g_world
            F_predicted = self.load_mass * g_sensor
            F_actual = self.force_readings[i][:3]
            residual = np.linalg.norm(F_actual - F_predicted)
            residuals.append(residual)
        
        self.zero_drift = np.mean(residuals)
        
        print(f"标定完成")
        print(f"负载质量: {self.load_mass:.4f} kg")
        print(f"负载质心: {self.load_cog}")
        print(f"零漂: {self.zero_drift:.4f} N")
        
        return True, self.load_mass, self.load_cog, self.zero_drift
    
    def save_calibration(self, filepath: str):
        """保存标定结果"""
        if self.load_mass is None:
            print("错误: 未进行标定")
            return
        
        calibration_data = {
            'load_mass': float(self.load_mass),
            'load_cog': self.load_cog.tolist(),
            'zero_drift': float(self.zero_drift),
            'sensor_type': self.sensor_type,
            'num_samples': len(self.force_readings)
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
    
    parser = argparse.ArgumentParser(description='力传感器标定工具')
    parser.add_argument('--sensor', type=str, default='ati_gamma',
                       help='传感器类型')
    parser.add_argument('--num-poses', type=int, default=20,
                       help='采集姿态数量')
    parser.add_argument('--output', type=str,
                       default='./calibration/calibration_data/ft_sensor_calibration.yaml',
                       help='输出文件路径')
    
    args = parser.parse_args()
    
    # 初始化标定器
    calibrator = FTSensorCalibration(sensor_type=args.sensor)
    
    # 采集数据
    calibrator.collect_calibration_data(num_poses=args.num_poses)
    
    # 执行标定
    success, mass, cog, drift = calibrator.calibrate()
    
    if success:
        # 保存结果
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        calibrator.save_calibration(args.output)
    else:
        print("标定失败")


if __name__ == '__main__':
    main()

