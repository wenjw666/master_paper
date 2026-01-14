"""
状态机管理节点
启动和管理SMACH状态机
"""

#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from std_srvs.srv import Trigger, TriggerResponse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from state_machine.connector_assembly_smach import create_assembly_state_machine
import smach_ros


class StateManagerNode:
    """状态机管理节点"""
    
    def __init__(self):
        """初始化状态机节点"""
        rospy.init_node('state_manager', anonymous=True)
        
        # 创建状态机
        self.sm = create_assembly_state_machine()
        
        # 状态机服务器（用于可视化）
        self.sis = smach_ros.IntrospectionServer('assembly_smach_server', self.sm, '/SM_ROOT')
        self.sis.start()
        
        # 服务
        from std_srvs.srv import Trigger, TriggerResponse
        self.execute_service = rospy.Service('/state_manager/execute_assembly',
                                            Trigger,
                                            self._handle_execute_service)
        
        # 订阅任务指令
        self.task_sub = rospy.Subscriber('/task_command', String,
                                        self._task_command_callback, queue_size=1)
        
        rospy.loginfo("状态机管理节点已启动")
    
    def _task_command_callback(self, msg: String):
        """任务指令回调"""
        self.sm.userdata.task_command = msg.data
    
    def _handle_execute_service(self, req):
        """
        处理执行装配服务请求
        
        Args:
            req: 服务请求（包含target_tag_id）
        
        Returns:
            服务响应
        """
        # 设置目标标签ID
        if hasattr(req, 'target_tag_id'):
            self.sm.userdata.target_tag_id = req.target_tag_id
        else:
            self.sm.userdata.target_tag_id = 'A'  # 默认
        
        # 触发任务
        self.sm.userdata.task_command = 'start_assembly'
        
        # 执行状态机（在后台线程）
        import threading
        thread = threading.Thread(target=self._execute_state_machine)
        thread.start()
        
        return TriggerResponse(success=True, message="任务已启动")
    
    def _execute_state_machine(self):
        """执行状态机"""
        outcome = self.sm.execute()
        rospy.loginfo(f"状态机执行完成，结果: {outcome}")
    
    def run(self):
        """运行节点"""
        rospy.spin()
        self.sis.stop()


if __name__ == '__main__':
    try:
        node = StateManagerNode()
        node.run()
    except rospy.ROSInterruptException:
        pass

