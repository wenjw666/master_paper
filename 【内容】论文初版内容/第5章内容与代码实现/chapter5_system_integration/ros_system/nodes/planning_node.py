"""
抓取规划节点（第3章）
ROS节点，封装抓取规划流程
"""

#!/usr/bin/env python3

import rospy
import numpy as np
from sensor_msgs.msg import Image, PointCloud2
from geometry_msgs.msg import PoseStamped, Vector3
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import String
from cv_bridge import CvBridge
import sys
import os

# 添加第3章路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../第3章内容与代码实现/chapter3_grasp_planning'))
from pipeline.autonomous_grasp_pipeline import AutonomousGraspPipeline


class PlanningNode:
    """抓取规划ROS节点"""
    
    def __init__(self):
        """初始化规划节点"""
        rospy.init_node('planning_node', anonymous=True)
        
        # 参数
        self.grasp_model_path = rospy.get_param('~grasp_model_path',
                                                './weights/contact_graspnet.pt')
        self.robot_type = rospy.get_param('~robot_type', 'ur5')
        
        # 初始化规划流水线
        self.planning_pipeline = self._init_planning_pipeline()
        
        # 图像桥接
        self.bridge = CvBridge()
        
        # 订阅者
        self.pose_sub = rospy.Subscriber('/connector/pose', PoseStamped,
                                        self._pose_callback, queue_size=1)
        self.cable_vector_sub = rospy.Subscriber('/cable/vector', Vector3,
                                                 self._cable_vector_callback, queue_size=1)
        self.rgb_sub = rospy.Subscriber('/camera/color/image_raw', Image,
                                        self._rgb_callback, queue_size=1)
        self.depth_sub = rospy.Subscriber('/camera/aligned_depth_to_color', Image,
                                         self._depth_callback, queue_size=1)
        
        # 发布者
        self.trajectory_pub = rospy.Publisher('/joint_trajectory', JointTrajectory,
                                             queue_size=1)
        
        # 服务
        from std_srvs.srv import Trigger, TriggerResponse
        self.planning_service = rospy.Service('/planning_node/plan_grasp',
                                              Trigger,
                                              self._handle_planning_service)
        
        # 状态
        self.current_pose = None
        self.current_cable_vector = None
        self.current_rgb = None
        self.current_depth = None
        
        rospy.loginfo("抓取规划节点已启动")
    
    def _init_planning_pipeline(self) -> AutonomousGraspPipeline:
        """初始化规划流水线"""
        # 加载相机内参
        camera_intrinsic_path = rospy.get_param('~camera_intrinsic_path',
                                                './calibration/camera_params.yaml')
        import yaml
        with open(camera_intrinsic_path, 'r') as f:
            cam_data = yaml.safe_load(f)
        camera_matrix = np.array(cam_data['camera_matrix'])
        
        pipeline = AutonomousGraspPipeline(
            grasp_model_path=self.grasp_model_path,
            robot_type=self.robot_type,
            camera_intrinsic=camera_matrix
        )
        
        return pipeline
    
    def _pose_callback(self, msg: PoseStamped):
        """位姿回调"""
        # 转换为numpy数组
        from scipy.spatial.transform import Rotation
        position = np.array([msg.pose.position.x, msg.pose.position.y, msg.pose.position.z])
        orientation = np.array([
            msg.pose.orientation.x, msg.pose.orientation.y,
            msg.pose.orientation.z, msg.pose.orientation.w
        ])
        R = Rotation.from_quat(orientation).as_matrix()
        
        # 构建位姿字典
        self.current_pose = {
            'R': R,
            't': position
        }
    
    def _cable_vector_callback(self, msg: Vector3):
        """线缆向量回调"""
        self.current_cable_vector = np.array([msg.x, msg.y, msg.z])
    
    def _rgb_callback(self, msg: Image):
        """RGB图像回调"""
        try:
            self.current_rgb = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            rospy.logerr(f"RGB图像转换失败: {e}")
    
    def _depth_callback(self, msg: Image):
        """深度图像回调"""
        try:
            self.current_depth = self.bridge.imgmsg_to_cv2(msg, "16UC1")
        except Exception as e:
            rospy.logerr(f"深度图像转换失败: {e}")
    
    def _handle_planning_service(self, req):
        """
        处理规划服务请求
        
        Args:
            req: 服务请求
        
        Returns:
            服务响应
        """
        from std_srvs.srv import TriggerResponse
        
        if self.current_pose is None or self.current_rgb is None or self.current_depth is None:
            rospy.logwarn("规划所需数据未就绪")
            return TriggerResponse(success=False, message="数据未就绪")
        
        # 获取当前关节状态
        from sensor_msgs.msg import JointState
        try:
            joint_state = rospy.wait_for_message('/joint_states', JointState, timeout=2.0)
            current_joints = np.array(joint_state.position)
        except:
            rospy.logwarn("无法获取关节状态，使用默认值")
            current_joints = np.zeros(6)
        
        # 获取目标标签ID
        target_tag_id = rospy.get_param('~target_tag_id', None)
        
        # 执行抓取规划
        result = self.planning_pipeline.execute_grasp(
            rgb_image=self.current_rgb,
            depth_image=self.current_depth,
            connector_pose=self.current_pose,
            cable_mask=None,  # 需要从Ch2获取掩膜
            start_config=current_joints,
            target_tag_id=target_tag_id
        )
        
        if result['success']:
            # 发布轨迹
            trajectory = self._grasp_result_to_trajectory(result['path'])
            self.trajectory_pub.publish(trajectory)
            
            rospy.loginfo("抓取规划成功")
            return TriggerResponse(success=True, message="规划成功")
        else:
            rospy.logwarn(f"抓取规划失败: {result['message']}")
            return TriggerResponse(success=False, message=result['message'])
    
    def _grasp_result_to_trajectory(self, path: List[np.ndarray]) -> JointTrajectory:
        """
        将规划路径转换为ROS轨迹消息
        
        Args:
            path: 关节空间路径
        
        Returns:
            JointTrajectory消息
        """
        trajectory = JointTrajectory()
        trajectory.joint_names = [
            "shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint",
            "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"
        ]
        
        for i, joint_config in enumerate(path):
            point = JointTrajectoryPoint()
            point.positions = joint_config.tolist()
            point.time_from_start = rospy.Duration(i * 0.1)  # 假设每点0.1秒
            trajectory.points.append(point)
        
        return trajectory
    
    def run(self):
        """运行节点"""
        rospy.spin()


if __name__ == '__main__':
    try:
        node = PlanningNode()
        node.run()
    except rospy.ROSInterruptException:
        pass

