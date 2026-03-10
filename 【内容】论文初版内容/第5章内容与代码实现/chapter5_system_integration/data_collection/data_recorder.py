"""
实验数据记录工具
使用ROS Bag录制实验数据
"""

import rospy
import rosbag
import argparse
from datetime import datetime
import os


class DataRecorder:
    """数据记录器"""
    
    def __init__(self, output_bag: str, topics: list = None, duration: float = None):
        """
        初始化数据记录器
        
        Args:
            output_bag: 输出Bag文件路径
            topics: 要录制的话题列表（如果为None，录制所有话题）
            duration: 录制时长（秒），如果为None则手动停止
        """
        self.output_bag = output_bag
        self.topics = topics
        self.duration = duration
        
        # 默认话题列表
        if topics is None:
            self.topics = [
                '/camera/color/image_raw',
                '/camera/aligned_depth_to_color',
                '/connector/pose',
                '/cable/vector',
                '/ft_sensor/raw',
                '/joint_states',
                '/assembly/status'
            ]
    
    def record(self):
        """开始录制"""
        rospy.init_node('data_recorder', anonymous=True)
        
        # 创建Bag文件
        os.makedirs(os.path.dirname(self.output_bag), exist_ok=True)
        bag = rosbag.Bag(self.output_bag, 'w')
        
        print(f"开始录制数据到: {self.output_bag}")
        print(f"录制话题: {self.topics}")
        
        if self.duration:
            print(f"录制时长: {self.duration} 秒")
            start_time = rospy.Time.now()
            end_time = start_time + rospy.Duration(self.duration)
        else:
            print("按Ctrl+C停止录制")
            end_time = None
        
        try:
            # 订阅所有话题
            subscribers = []
            for topic in self.topics:
                try:
                    # 获取话题类型
                    topic_type, _, _ = rospy.get_topic_type(topic)
                    if topic_type:
                        sub = rospy.Subscriber(topic, rospy.AnyMsg, 
                                             lambda msg, t=topic: self._callback(msg, t, bag))
                        subscribers.append(sub)
                        print(f"已订阅: {topic}")
                    else:
                        print(f"警告: 话题 {topic} 不存在")
                except Exception as e:
                    print(f"警告: 无法订阅 {topic}: {e}")
            
            # 等待录制
            if end_time:
                while rospy.Time.now() < end_time:
                    rospy.sleep(0.1)
            else:
                rospy.spin()
        
        except KeyboardInterrupt:
            print("\n录制中断")
        
        finally:
            bag.close()
            print(f"录制完成，数据已保存: {self.output_bag}")
    
    def _callback(self, msg, topic, bag):
        """话题回调函数"""
        try:
            bag.write(topic, msg)
        except Exception as e:
            rospy.logerr(f"写入Bag失败: {e}")


def main():
    parser = argparse.ArgumentParser(description='ROS数据记录工具')
    parser.add_argument('--output-bag', type=str, required=True,
                       help='输出Bag文件路径')
    parser.add_argument('--topics', type=str, nargs='+', default=None,
                       help='要录制的话题列表')
    parser.add_argument('--duration', type=float, default=None,
                       help='录制时长（秒）')
    
    args = parser.parse_args()
    
    recorder = DataRecorder(
        output_bag=args.output_bag,
        topics=args.topics,
        duration=args.duration
    )
    
    recorder.record()


if __name__ == '__main__':
    main()

