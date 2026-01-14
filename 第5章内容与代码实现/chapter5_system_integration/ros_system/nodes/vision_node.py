"""
视觉感知节点（第2章）
ROS节点，封装级联视觉感知流程
"""

#!/usr/bin/env python3

import rospy
import numpy as np
from sensor_msgs.msg import Image, PointCloud2
from geometry_msgs.msg import PoseStamped, Vector3
from std_msgs.msg import String
from cv_bridge import CvBridge
import sys
import os

# 添加第2章路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../第2章内容与代码实现/chapter2_vision_perception'))
from pipeline.cascade_vision_pipeline import CascadeVisionPipeline


class VisionNode:
    """视觉感知ROS节点"""
    
    def __init__(self):
        """初始化视觉节点"""
        rospy.init_node('vision_node', anonymous=True)
        
        # 参数
        self.yolov8_model_path = rospy.get_param('~yolov8_model_path', 
                                                 './weights/yolov8_seg.pt')
        self.deeplab_model_path = rospy.get_param('~deeplab_model_path', 
                                                   './weights/deeplabv3_keypoints.pt')
        self.camera_intrinsic_path = rospy.get_param('~camera_intrinsic_path',
                                                     './calibration/camera_params.yaml')
        
        # 初始化视觉流水线
        self.vision_pipeline = self._init_vision_pipeline()
        
        # 图像桥接
        self.bridge = CvBridge()
        
        # 订阅者
        self.rgb_sub = rospy.Subscriber('/camera/color/image_raw', Image, 
                                        self._rgb_callback, queue_size=1)
        self.depth_sub = rospy.Subscriber('/camera/aligned_depth_to_color', Image,
                                         self._depth_callback, queue_size=1)
        
        # 发布者
        self.pose_pub = rospy.Publisher('/connector/pose', PoseStamped, queue_size=1)
        self.cable_vector_pub = rospy.Publisher('/cable/vector', Vector3, queue_size=1)
        self.tag_id_pub = rospy.Publisher('/connector/tag_id', String, queue_size=1)
        
        # 服务
        from std_srvs.srv import Trigger, TriggerResponse
        self.perception_service = rospy.Service('/vision_node/trigger_perception',
                                               Trigger,
                                               self._handle_perception_service)
        
        # 状态
        self.current_rgb = None
        self.current_depth = None
        self.target_tag_id = None
        
        rospy.loginfo("视觉感知节点已启动")
    
    def _init_vision_pipeline(self) -> CascadeVisionPipeline:
        """初始化视觉流水线"""
        # 加载相机内参
        import yaml
        with open(self.camera_intrinsic_path, 'r') as f:
            cam_data = yaml.safe_load(f)
        camera_matrix = np.array(cam_data['camera_matrix'])
        
        # 加载3D模型关键点（需要从配置文件加载）
        model_points_3d = np.array([
            [0, 0, 0],      # 定位孔1
            [10, 0, 0],     # 定位孔2
            [5, 10, 0],     # 定位孔3
            [5, 5, -5],     # 线缆根部
        ], dtype=np.float32)
        
        pipeline = CascadeVisionPipeline(
            yolov8_model_path=self.yolov8_model_path,
            deeplab_model_path=self.deeplab_model_path,
            camera_matrix=camera_matrix,
            model_points_3d=model_points_3d
        )
        
        return pipeline
    
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
    
    def _handle_perception_service(self, req):
        """
        处理感知服务请求
        
        Args:
            req: 服务请求
        
        Returns:
            服务响应
        """
        from std_srvs.srv import TriggerResponse
        
        if self.current_rgb is None or self.current_depth is None:
            rospy.logwarn("图像数据未就绪")
            return TriggerResponse(success=False, message="图像数据未就绪")
        
        # 获取目标标签ID（从参数或话题）
        target_tag_id = rospy.get_param('~target_tag_id', None)
        
        # 执行视觉感知
        result = self.vision_pipeline.inference(
            rgb_image=self.current_rgb,
            depth_image=self.current_depth,
            target_tag_id=target_tag_id
        )
        
        # 发布结果
        if result['tag_id'] is not None:
            # 发布位姿
            pose_msg = PoseStamped()
            pose_msg.header.stamp = rospy.Time.now()
            pose_msg.header.frame_id = "camera_frame"
            
            if result['pose_6d'] is not None:
                R = result['pose_6d']['R']
                t = result['pose_6d']['t']
                
                # 旋转矩阵转四元数
                from scipy.spatial.transform import Rotation
                rot = Rotation.from_matrix(R)
                quat = rot.as_quat()  # [x, y, z, w]
                
                pose_msg.pose.position.x = t[0]
                pose_msg.pose.position.y = t[1]
                pose_msg.pose.position.z = t[2]
                pose_msg.pose.orientation.x = quat[0]
                pose_msg.pose.orientation.y = quat[1]
                pose_msg.pose.orientation.z = quat[2]
                pose_msg.pose.orientation.w = quat[3]
                
                self.pose_pub.publish(pose_msg)
            
            # 发布线缆方向向量
            if result['cable_vector'] is not None:
                cable_msg = Vector3()
                cable_msg.x = result['cable_vector'][0]
                cable_msg.y = result['cable_vector'][1]
                cable_msg.z = result['cable_vector'][2]
                self.cable_vector_pub.publish(cable_msg)
            
            # 发布标签ID
            tag_msg = String()
            tag_msg.data = result['tag_id']
            self.tag_id_pub.publish(tag_msg)
            
            rospy.loginfo(f"视觉感知完成: Tag ID={result['tag_id']}, 置信度={result['confidence']:.2f}")
            return TriggerResponse(success=True, message="感知成功")
        else:
            rospy.logwarn("未检测到目标连接器")
            return TriggerResponse(success=False, message="未检测到目标")
    
    def run(self):
        """运行节点"""
        rospy.spin()


if __name__ == '__main__':
    try:
        node = VisionNode()
        node.run()
    except rospy.ROSInterruptException:
        pass

