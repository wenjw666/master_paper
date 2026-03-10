"""
电连接器装配状态机
基于SMACH实现任务流程调度
"""

import rospy
import smach
import smach_ros
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from std_srvs.srv import Trigger, TriggerResponse


# 定义状态
class IdleState(smach.State):
    """待机状态"""
    def __init__(self):
        smach.State.__init__(self,
                            outcomes=['perception_requested', 'shutdown'],
                            input_keys=['task_command'],
                            output_keys=[])
    
    def execute(self, userdata):
        rospy.loginfo("状态: IDLE - 等待任务")
        
        # 等待任务指令
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            if userdata.task_command == 'start_assembly':
                return 'perception_requested'
            rate.sleep()
        
        return 'shutdown'


class PerceptionState(smach.State):
    """视觉感知状态（Ch2）"""
    def __init__(self):
        smach.State.__init__(self,
                            outcomes=['perception_success', 'perception_failed', 'retry'],
                            input_keys=['target_tag_id'],
                            output_keys=['connector_pose', 'cable_vector', 'tag_id'],
                            io_keys=['retry_count'])
    
    def execute(self, userdata):
        rospy.loginfo(f"状态: PERCEPTION - 视觉感知 (Tag ID: {userdata.target_tag_id})")
        
        # 调用视觉感知服务
        try:
            # 注意：需要先定义srv文件并编译ROS包
            # from chapter5_system_integration.srv import TriggerPerception
            # 临时使用标准服务
            from std_srvs.srv import Trigger
            rospy.wait_for_service('/vision_node/trigger_perception', timeout=5.0)
            perception_service = rospy.ServiceProxy('/vision_node/trigger_perception', Trigger)
            
            response = perception_service()
            
            if response.success:
                # 从话题获取结果
                from geometry_msgs.msg import PoseStamped, Vector3
                from std_msgs.msg import String
                pose_msg = rospy.wait_for_message('/connector/pose', PoseStamped, timeout=2.0)
                cable_msg = rospy.wait_for_message('/cable/vector', Vector3, timeout=2.0)
                tag_msg = rospy.wait_for_message('/connector/tag_id', String, timeout=2.0)
                
                # 存储结果
                userdata.connector_pose = pose_msg
                userdata.cable_vector = cable_msg
                userdata.tag_id = tag_msg.data
                
                rospy.loginfo("视觉感知成功")
                return 'perception_success'
            else:
                rospy.logwarn(f"视觉感知失败: {response.message}")
                userdata.retry_count = userdata.retry_count.get('count', 0) + 1
                
                if userdata.retry_count.get('count', 0) < 3:
                    return 'retry'
                else:
                    return 'perception_failed'
        
        except Exception as e:
            rospy.logerr(f"视觉感知异常: {e}")
            return 'perception_failed'


class ApproachState(smach.State):
    """接近目标状态（Ch3路径规划）"""
    def __init__(self):
        smach.State.__init__(self,
                            outcomes=['approach_success', 'approach_failed'],
                            input_keys=['connector_pose', 'cable_vector'],
                            output_keys=['grasp_pose', 'path'])
    
    def execute(self, userdata):
        rospy.loginfo("状态: APPROACH - 路径规划与接近")
        
        # 调用规划服务
        try:
            # 注意：需要先定义srv文件并编译ROS包
            # from chapter5_system_integration.srv import PlanGrasp
            # 临时使用标准服务
            from std_srvs.srv import Trigger
            rospy.wait_for_service('/planning_node/plan_grasp', timeout=5.0)
            planning_service = rospy.ServiceProxy('/planning_node/plan_grasp', Trigger)
            
            response = planning_service()
            
            if response.success:
                userdata.grasp_pose = response.grasp_pose
                userdata.path = response.path
                rospy.loginfo("路径规划成功")
                return 'approach_success'
            else:
                rospy.logwarn(f"路径规划失败: {response.message}")
                return 'approach_failed'
        
        except Exception as e:
            rospy.logerr(f"路径规划异常: {e}")
            return 'approach_failed'


class GraspState(smach.State):
    """抓取执行状态"""
    def __init__(self):
        smach.State.__init__(self,
                            outcomes=['grasp_success', 'grasp_failed'],
                            input_keys=['grasp_pose', 'path'],
                            output_keys=[])
    
    def execute(self, userdata):
        rospy.loginfo("状态: GRASP - 执行抓取")
        
        # 执行抓取动作
        # 1. 移动到抓取位姿
        # 2. 闭合夹爪
        # 3. 验证抓取成功
        
        rospy.sleep(2.0)  # 模拟抓取时间
        
        # 简化：假设抓取成功
        rospy.loginfo("抓取完成")
        return 'grasp_success'


class TransportState(smach.State):
    """搬运状态"""
    def __init__(self):
        smach.State.__init__(self,
                            outcomes=['transport_success', 'transport_failed'],
                            input_keys=[],
                            output_keys=[])
    
    def execute(self, userdata):
        rospy.loginfo("状态: TRANSPORT - 搬运至装配区")
        
        # 移动到预装配位置
        rospy.sleep(3.0)  # 模拟搬运时间
        
        rospy.loginfo("搬运完成")
        return 'transport_success'


class AssemblyState(smach.State):
    """装配状态（Ch4力控）"""
    def __init__(self):
        smach.State.__init__(self,
                            outcomes=['assembly_success', 'assembly_failed', 'force_overflow'],
                            input_keys=['cable_vector'],
                            output_keys=['assembly_result'])
    
    def execute(self, userdata):
        rospy.loginfo("状态: ASSEMBLY - 柔顺装配")
        
        # 调用装配控制服务
        try:
            # 注意：需要先定义srv文件并编译ROS包
            # from chapter5_system_integration.srv import ExecuteAssembly
            # 临时使用标准服务
            from std_srvs.srv import Trigger
            rospy.wait_for_service('/control_node/execute_assembly', timeout=5.0)
            assembly_service = rospy.ServiceProxy('/control_node/execute_assembly', Trigger)
            
            response = assembly_service()
            
            if response.success:
                userdata.assembly_result = response
                rospy.loginfo("装配成功")
                return 'assembly_success'
            elif response.error_code == 'FORCE_OVERFLOW':
                rospy.logwarn("力超限，触发安全保护")
                return 'force_overflow'
            else:
                rospy.logwarn(f"装配失败: {response.message}")
                return 'assembly_failed'
        
        except Exception as e:
            rospy.logerr(f"装配异常: {e}")
            return 'assembly_failed'


class ErrorRecoveryState(smach.State):
    """异常恢复状态"""
    def __init__(self):
        smach.State.__init__(self,
                            outcomes=['recovery_success', 'recovery_failed', 'abort'],
                            input_keys=['error_type'],
                            output_keys=[])
    
    def execute(self, userdata):
        rospy.logwarn(f"状态: ERROR_RECOVERY - 异常类型: {userdata.error_type}")
        
        # 根据错误类型执行恢复策略
        error_type = userdata.error_type
        
        if error_type == 'perception_failed':
            # 视觉失败：变换视角重试
            rospy.loginfo("执行视角变换重试...")
            rospy.sleep(1.0)
            return 'recovery_success'
        
        elif error_type == 'grasp_failed':
            # 抓取失败：重新规划
            rospy.loginfo("执行重新规划...")
            return 'recovery_success'
        
        elif error_type == 'force_overflow':
            # 力超限：回退-螺旋搜索
            rospy.loginfo("执行回退-螺旋搜索...")
            rospy.sleep(2.0)
            return 'recovery_success'
        
        else:
            rospy.logerr("未知错误类型，终止任务")
            return 'abort'


def create_assembly_state_machine():
    """创建装配状态机"""
    sm = smach.StateMachine(outcomes=['task_complete', 'task_failed', 'task_aborted'])
    
    # 定义用户数据
    sm.userdata.target_tag_id = 'A'
    sm.userdata.task_command = ''
    sm.userdata.connector_pose = None
    sm.userdata.cable_vector = None
    sm.userdata.tag_id = None
    sm.userdata.grasp_pose = None
    sm.userdata.path = None
    sm.userdata.assembly_result = None
    sm.userdata.error_type = None
    sm.userdata.retry_count = {'count': 0}
    
    with sm:
        # 添加状态
        smach.StateMachine.add('IDLE', IdleState(),
                              transitions={'perception_requested': 'PERCEPTION',
                                          'shutdown': 'task_aborted'})
        
        smach.StateMachine.add('PERCEPTION', PerceptionState(),
                              transitions={'perception_success': 'APPROACH',
                                          'perception_failed': 'ERROR_RECOVERY',
                                          'retry': 'PERCEPTION'})
        
        smach.StateMachine.add('APPROACH', ApproachState(),
                              transitions={'approach_success': 'GRASP',
                                          'approach_failed': 'ERROR_RECOVERY'})
        
        smach.StateMachine.add('GRASP', GraspState(),
                              transitions={'grasp_success': 'TRANSPORT',
                                          'grasp_failed': 'ERROR_RECOVERY'})
        
        smach.StateMachine.add('TRANSPORT', TransportState(),
                              transitions={'transport_success': 'ASSEMBLY',
                                          'transport_failed': 'ERROR_RECOVERY'})
        
        smach.StateMachine.add('ASSEMBLY', AssemblyState(),
                              transitions={'assembly_success': 'task_complete',
                                          'assembly_failed': 'ERROR_RECOVERY',
                                          'force_overflow': 'ERROR_RECOVERY'})
        
        smach.StateMachine.add('ERROR_RECOVERY', ErrorRecoveryState(),
                              transitions={'recovery_success': 'PERCEPTION',  # 重试感知
                                          'recovery_failed': 'task_failed',
                                          'abort': 'task_aborted'})
    
    return sm


def main():
    """主函数"""
    rospy.init_node('connector_assembly_state_machine')
    
    # 创建状态机
    sm = create_assembly_state_machine()
    
    # 创建状态机服务器（用于可视化）
    sis = smach_ros.IntrospectionServer('assembly_smach_server', sm, '/SM_ROOT')
    sis.start()
    
    # 执行状态机
    outcome = sm.execute()
    
    rospy.loginfo(f"状态机执行完成，结果: {outcome}")
    
    sis.stop()


if __name__ == '__main__':
    main()

