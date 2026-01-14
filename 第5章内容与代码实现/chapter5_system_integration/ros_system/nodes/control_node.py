"""
装配控制节点（第4章）
ROS节点，封装力位混合控制和SAC策略
"""

#!/usr/bin/env python3

import rospy
import numpy as np
from geometry_msgs.msg import Wrench, Vector3, Twist
from std_msgs.msg import String
import sys
import os

# 添加第4章路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../第4章内容与代码实现/chapter4_assembly_control'))
from pipeline.assembly_control_pipeline import AssemblyControlPipeline


class ControlNode:
    """装配控制ROS节点"""
    
    def __init__(self):
        """初始化控制节点"""
        rospy.init_node('control_node', anonymous=True)
        
        # 参数
        self.sac_model_path = rospy.get_param('~sac_model_path',
                                              './checkpoints/sac_final.pt')
        self.robot_type = rospy.get_param('~robot_type', 'ur5')
        self.control_frequency = rospy.get_param('~control_frequency', 500)  # Hz
        
        # 初始化控制流水线
        self.control_pipeline = self._init_control_pipeline()
        
        # 订阅者
        self.cable_vector_sub = rospy.Subscriber('/cable/vector', Vector3,
                                                 self._cable_vector_callback, queue_size=1)
        self.ft_sub = rospy.Subscriber('/ft_sensor/raw', Wrench,
                                       self._ft_callback, queue_size=1)
        
        # 发布者
        self.velocity_pub = rospy.Publisher('/joint_group_vel_controller/command',
                                           Twist, queue_size=1)
        self.status_pub = rospy.Publisher('/assembly/status', String, queue_size=1)
        
        # 服务
        from std_srvs.srv import Trigger, TriggerResponse
        self.assembly_service = rospy.Service('/control_node/execute_assembly',
                                             Trigger,
                                             self._handle_assembly_service)
        
        # 状态
        self.current_cable_vector = None
        self.current_wrench = None
        self.assembly_active = False
        
        rospy.loginfo("装配控制节点已启动")
    
    def _init_control_pipeline(self) -> AssemblyControlPipeline:
        """初始化控制流水线"""
        pipeline = AssemblyControlPipeline(
            sac_model_path=self.sac_model_path,
            cable_vector=None,  # 将从话题获取
            target_pose=None,   # 将从服务请求获取
            device='cuda'
        )
        
        return pipeline
    
    def _cable_vector_callback(self, msg: Vector3):
        """线缆向量回调"""
        self.current_cable_vector = np.array([msg.x, msg.y, msg.z])
        if self.control_pipeline is not None:
            self.control_pipeline.update_cable_vector(self.current_cable_vector)
    
    def _ft_callback(self, msg: Wrench):
        """力传感器回调"""
        self.current_wrench = np.array([
            msg.force.x, msg.force.y, msg.force.z,
            msg.torque.x, msg.torque.y, msg.torque.z
        ])
    
    def _handle_assembly_service(self, req):
        """
        处理装配服务请求
        
        Args:
            req: 服务请求
        
        Returns:
            服务响应
        """
        from std_srvs.srv import TriggerResponse
        
        if self.current_cable_vector is None:
            rospy.logwarn("线缆向量未就绪")
            return TriggerResponse(success=False, message="线缆向量未就绪")
        
        # 获取起始和目标位姿（从参数或话题）
        start_pose = self._get_current_pose()
        target_pose = self._get_target_pose(None)
        
        if target_pose is None:
            return TriggerResponse(success=False, message="目标位姿未指定")
        
        # 执行装配
        rospy.loginfo("开始执行装配任务")
        self.assembly_active = True
        
        result = self.control_pipeline.execute_assembly(
            start_pose=start_pose,
            target_pose=target_pose,
            max_steps=1000,
            force_threshold=30.0
        )
        
        self.assembly_active = False
        
        if result['success']:
            rospy.loginfo("装配成功")
            return TriggerResponse(success=True, message="装配成功")
        else:
            rospy.logwarn(f"装配失败: {result['message']}")
            return TriggerResponse(success=False, message=result['message'])
    
    def _get_current_pose(self) -> np.ndarray:
        """获取当前位姿"""
        # 从机器人状态获取
        # 简化：返回零位姿
        return np.zeros(6)
    
    def _get_target_pose(self, req) -> Optional[np.ndarray]:
        """获取目标位姿"""
        # 从服务请求或配置文件获取
        # 简化：返回默认目标位姿
        return np.array([0, 0, 0.1, 0, 0, 0])
    
    def run(self):
        """运行节点"""
        rate = rospy.Rate(self.control_frequency)
        
        while not rospy.is_shutdown():
            if self.assembly_active:
                # 控制循环（实际应在服务中执行）
                pass
            
            rate.sleep()


if __name__ == '__main__':
    try:
        node = ControlNode()
        node.run()
    except rospy.ROSInterruptException:
        pass

