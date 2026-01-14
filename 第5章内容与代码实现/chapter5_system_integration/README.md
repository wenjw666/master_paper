# 第5章：电连接器机器人自主装配系统集成与综合实验代码实现

## 项目概述

本项目实现了面向航空制造的电连接器自主抓取与装配系统的完整集成，基于ROS构建分布式软件架构，整合第2-4章的所有功能模块，实现端到端的自主作业流程。

## 核心功能模块

### 1. ROS系统架构 (`ros_system/`)
- **功能**：基于ROS Noetic的分布式节点系统
- **核心节点**：
  1. `/vision_node` (Ch2): 视觉感知节点
  2. `/planning_node` (Ch3): 抓取规划节点
  3. `/control_node` (Ch4): 装配控制节点
  4. `/state_manager`: 状态机调度节点
- **技术栈**：
  - ROS Noetic
  - SMACH (状态机库)
  - MoveIt! (运动规划)

### 2. 系统标定工具 (`calibration/`)
- **功能**：多坐标系统一标定
- **标定内容**：
  1. 手眼标定（Hand-Eye Calibration）
  2. 力传感器重力补偿标定
  3. 相机内参标定
- **技术栈**：
  - OpenCV标定工具
  - Tsai-Lenz算法
  - 最小二乘法

### 3. 状态机与任务调度 (`state_machine/`)
- **功能**：实现"感知-接近-抓取-搬运-装配"的完整任务流程
- **状态定义**：
  - `IDLE`: 待机
  - `PERCEPTION`: 视觉感知
  - `APPROACH`: 接近目标
  - `GRASP`: 抓取执行
  - `TRANSPORT`: 搬运至装配区
  - `ASSEMBLY`: 柔顺装配
  - `ERROR_RECOVERY`: 异常恢复
- **技术栈**：
  - SMACH (ROS状态机库)

### 4. 数据采集与分析 (`data_collection/`)
- **功能**：实验数据记录、可视化与分析
- **数据类型**：
  - 图像序列（RGB-D）
  - 力/力矩曲线
  - 关节轨迹
  - 系统日志
- **技术栈**：
  - ROS Bag
  - Matplotlib
  - Pandas

### 5. 异常处理与恢复 (`error_recovery/`)
- **功能**：系统异常检测与自动恢复
- **恢复策略**：
  - 视觉识别失败 → 变换视角重试
  - 抓取失败 → 重新规划
  - 装配力超限 → 回退-螺旋搜索
- **技术栈**：
  - ROS Action Server/Client

## 依赖环境

### ROS环境
- ROS Noetic (Ubuntu 20.04) 或 ROS2 Foxy/Humble
- 必需ROS包：
  - `moveit`
  - `universal_robots` (UR机械臂驱动)
  - `realsense2_camera` (RealSense相机驱动)
  - `geometry_msgs`, `sensor_msgs`, `std_msgs`

### Python环境
- Python 3.8+
- ROS Python接口 (`rospy`)
- NumPy, SciPy, Matplotlib, Pandas

### 硬件接口
- UR机器人SDK
- RealSense SDK
- ATI力传感器驱动

## 项目结构

```
chapter5_system_integration/
├── README.md
├── requirements.txt
├── ros_system/
│   ├── launch/
│   │   ├── system.launch            # 系统总启动文件
│   │   ├── vision.launch           # 视觉节点启动
│   │   ├── planning.launch          # 规划节点启动
│   │   └── control.launch          # 控制节点启动
│   ├── nodes/
│   │   ├── vision_node.py          # Ch2视觉感知节点
│   │   ├── planning_node.py        # Ch3规划节点
│   │   ├── control_node.py        # Ch4控制节点
│   │   └── state_manager_node.py   # 状态机节点
│   ├── msg/                         # 自定义消息类型
│   │   ├── ConnectorPose.msg
│   │   ├── CableVector.msg
│   │   └── AssemblyStatus.msg
│   └── srv/                         # 自定义服务
│       ├── TriggerPerception.srv
│       └── ExecuteAssembly.srv
├── calibration/
│   ├── hand_eye_calibration.py     # 手眼标定工具
│   ├── ft_sensor_calibration.py    # 力传感器标定
│   ├── camera_calibration.py       # 相机标定
│   └── calibration_data/           # 标定数据存储
├── state_machine/
│   ├── connector_assembly_smach.py  # SMACH状态机定义
│   ├── states/
│   │   ├── perception_state.py
│   │   ├── grasp_state.py
│   │   ├── assembly_state.py
│   │   └── error_recovery_state.py
│   └── utils/
│       └── state_transitions.py
├── data_collection/
│   ├── data_recorder.py             # ROS Bag录制
│   ├── data_analyzer.py             # 数据分析脚本
│   ├── visualization.py             # 结果可视化
│   └── experiments/                 # 实验数据存储
├── error_recovery/
│   ├── error_detector.py           # 异常检测
│   ├── recovery_strategies.py      # 恢复策略
│   └── recovery_actions.py         # 恢复动作执行
└── config/
    ├── system_config.yaml          # 系统配置文件
    ├── robot_config.yaml           # 机器人参数
    └── sensor_config.yaml          # 传感器参数
```

## 快速开始

### 1. ROS环境配置
```bash
# 创建工作空间
mkdir -p ~/connector_assembly_ws/src
cd ~/connector_assembly_ws/src

# 克隆本项目
git clone <repository_url> chapter5_system_integration

# 安装依赖
cd ~/connector_assembly_ws
rosdep install --from-paths src --ignore-src -r -y

# 编译
catkin_make
source devel/setup.bash
```

### 2. 系统标定
```bash
# 手眼标定
rosrun chapter5_system_integration hand_eye_calibration.py \
    --robot_type ur5 \
    --camera realsense_d435i \
    --num_images 20

# 力传感器标定
rosrun chapter5_system_integration ft_sensor_calibration.py \
    --sensor ati_gamma
```

### 3. 启动完整系统
```bash
# 启动所有节点
roslaunch chapter5_system_integration system.launch

# 或分步启动
roslaunch chapter5_system_integration vision.launch
roslaunch chapter5_system_integration planning.launch
roslaunch chapter5_system_integration control.launch
```

### 4. 执行完整装配任务
```python
# 通过ROS服务触发
rosservice call /state_manager/execute_assembly \
    "target_tag_id: 'A'"

# 或通过Python脚本
import rospy
from chapter5_system_integration.srv import ExecuteAssembly

rospy.wait_for_service('/state_manager/execute_assembly')
execute = rospy.ServiceProxy('/state_manager/execute_assembly', ExecuteAssembly)
result = execute(target_tag_id='A')
```

### 5. 数据采集与分析
```bash
# 录制实验数据
rosrun chapter5_system_integration data_recorder.py \
    --output_bag ./experiments/exp_001.bag \
    --duration 300  # 5分钟

# 分析数据
python data_collection/data_analyzer.py \
    --bag_file ./experiments/exp_001.bag \
    --output_dir ./experiments/exp_001_analysis
```

## ROS话题与服务

### 主要话题 (Topics)
- `/camera/color/image_raw`: RGB图像
- `/camera/aligned_depth_to_color`: 对齐的深度图像
- `/connector/pose`: 连接器6D位姿 (Ch2输出)
- `/cable/vector`: 线缆方向向量 (Ch2输出)
- `/joint_trajectory`: 关节轨迹 (Ch3输出)
- `/ft_sensor/raw`: 力/力矩传感器原始数据
- `/assembly/status`: 装配状态反馈

### 主要服务 (Services)
- `/vision_node/trigger_perception`: 触发视觉感知
- `/planning_node/plan_grasp`: 请求抓取规划
- `/control_node/execute_assembly`: 执行装配
- `/state_manager/execute_assembly`: 完整任务执行

## 开源算法与仓库参考

### ROS核心
1. **ROS Noetic**: http://wiki.ros.org/noetic
2. **MoveIt!**: https://moveit.ros.org/
3. **SMACH**: http://wiki.ros.org/smach
4. **UR机器人ROS驱动**: 
   - https://github.com/UniversalRobots/Universal_Robots_ROS_Driver

### 传感器驱动
1. **RealSense ROS包**: 
   - https://github.com/IntelRealSense/realsense-ros
2. **ATI力传感器ROS接口**: 
   - 需根据具体型号查找对应驱动

### 标定工具
1. **OpenCV标定**: `cv2.calibrateCamera()`
2. **手眼标定**: 
   - `easy_handeye` ROS包: https://github.com/marcoesposito1988/easy_handeye

### 数据分析
1. **ROS Bag工具**: `rosbag record/play`
2. **rqt工具**: ROS可视化工具集

## 系统集成流程

### 完整任务流程
```
1. IDLE → 等待任务
2. PERCEPTION → Ch2视觉感知
   ├─ YOLOv8-seg检测
   ├─ DeepLabV3+关键点提取
   └─ EPnP+RANSAC位姿解算
3. APPROACH → Ch3路径规划
   ├─ Contact-GraspNet抓取生成
   ├─ 多约束筛选
   └─ GRRT-Connect规划
4. GRASP → 执行抓取
5. TRANSPORT → 搬运至装配区
6. ASSEMBLY → Ch4柔顺装配
   ├─ 力位混合控制
   └─ SAC策略执行
7. COMPLETE → 任务完成
```

### 异常恢复流程
```
ERROR_DETECTED → ERROR_RECOVERY
├─ 视觉失败 → 变换视角重试
├─ 抓取失败 → 重新规划
├─ 装配超时 → 回退-螺旋搜索
└─ 力超限 → 急停并报警
```

## 实验验证

### 实验类型
1. **感知-规划子系统验证** (5.3节)
   - 不同遮挡率下的识别与规划成功率
   - 碰撞统计
   - 规划耗时

2. **力控装配子系统验证** (5.4节)
   - 消融实验（Baseline vs Ours）
   - 接触力曲线分析
   - 装配成功率统计

3. **全系统综合验证** (5.5节)
   - 连续作业测试
   - 节拍时间统计
   - 长期稳定性测试

### 数据记录格式
```yaml
experiment_metadata:
  experiment_id: "exp_001"
  date: "2024-XX-XX"
  operator: "XXX"
  robot_type: "UR5e"
  
results:
  perception:
    recognition_success_rate: 0.95
    pose_accuracy_add_s: 2.1  # mm
    
  planning:
    planning_time_mean: 3.28  # s
    collision_count: 0
    
  assembly:
    success_rate: 0.96
    avg_cycle_time: 22.8  # s
    max_contact_force: 6.8  # N
```

## 注意事项

1. **实时性要求**: 
   - 视觉节点: <100ms
   - 规划节点: <5s
   - 控制节点: 500Hz

2. **坐标系统一**: 所有标定必须在实验前完成，确保坐标系精度

3. **安全性**: 
   - 力阈值急停: >30N
   - 关节限位保护
   - 紧急停止按钮

4. **数据备份**: 实验数据需及时备份，ROS Bag文件较大

## 待实现功能

- [ ] Web界面监控（ROS Web Tools）
- [ ] 远程监控与调试
- [ ] 自动化实验脚本
- [ ] 性能分析工具（Profiling）

## 作者

哈尔滨工业大学机电工程学院

## 许可证

本项目为学术研究用途，遵循相关开源许可证。

