# 第3章：电连接器自主抓取方法代码实现

## 项目概述

本项目实现了面向航空狭窄空间环境的电连接器自主抓取系统，集成了端到端抓取生成、多约束优化筛选和引导式路径规划，解决柔性线缆障碍下的安全抓取难题。

## 核心功能模块

### 1. 端到端6D抓取生成 (`grasp_generation/`)
- **功能**：从点云直接预测候选抓取位姿
- **技术栈**：
  - [Contact-GraspNet](https://github.com/NVlabs/contact_graspnet) 架构
  - PointNet++ 骨干网络
  - SE(3)空间抓取位姿预测
- **输入**：RGB-D点云（经Ch2掩膜裁剪）
- **输出**：候选抓取位姿集合 {g_i = (t, R, w, s)}，包含位置、姿态、宽度和置信度

### 2. 多约束抓取点筛选 (`grasp_selection/`)
- **功能**：从候选抓取中筛选最优解
- **约束条件**：
  1. **运动学可行性**：逆运动学（IK）求解
  2. **避障检测**：利用Ch2线缆掩膜构建3D障碍物，碰撞检测
  3. **任务相容性**：抓取方向与装配方向对齐
- **技术栈**：
  - PyBullet IK求解器
  - FCL (Flexible Collision Library) 或 Open3D碰撞检测
  - 综合评分函数优化

### 3. GRRT-Connect路径规划 (`path_planning/`)
- **功能**：改进的引导式RRT-Connect算法，在狭窄空间内规划无碰撞路径
- **核心改进**：
  1. **目标偏置采样**：概率性向目标配置采样
  2. **混合障碍物地图**：AABB（刚性舱壁）+ Octomap（柔性线缆）
- **技术栈**：
  - [OMPL](https://ompl.kavrakilab.org/) (Open Motion Planning Library)
  - [OctoMap](https://octomap.github.io/) 动态地图
  - MoveIt! 集成接口

### 4. 线缆障碍物地图构建 (`obstacle_mapping/`)
- **功能**：将Ch2输出的线缆掩膜映射为3D Octomap
- **技术栈**：
  - Open3D点云处理
  - OctoMap库
  - 深度图像反投影

## 依赖环境

### Python环境
- Python 3.8+
- PyTorch 1.12+ (CUDA 11.6+)
- Open3D 0.15+
- NumPy, SciPy

### ROS环境（可选，用于MoveIt!集成）
- ROS Noetic / ROS2 Foxy
- MoveIt! Noetic / MoveIt2

### C++依赖（OctoMap）
- Eigen3
- OctoMap库

### 物理仿真（训练与测试）
- PyBullet 3.2+

## 项目结构

```
chapter3_grasp_planning/
├── README.md
├── requirements.txt
├── grasp_generation/
│   ├── contact_graspnet/
│   │   ├── model.py                 # Contact-GraspNet网络定义
│   │   ├── train.py                 # 训练脚本
│   │   └── inference.py             # 推理接口
│   ├── pointnet2/                   # PointNet++实现
│   └── utils/
│       ├── pointcloud_utils.py      # 点云预处理（下采样、背景去除）
│       └── grasp_visualization.py   # 抓取位姿可视化
├── grasp_selection/
│   ├── ik_solver.py                 # 逆运动学求解（PyBullet/IKFast）
│   ├── collision_checker.py         # 碰撞检测（FCL/Open3D）
│   ├── task_compatibility.py       # 任务相容性评分
│   └── multi_constraint_filter.py  # 多约束综合筛选
├── path_planning/
│   ├── grrt_connect.py              # GRRT-Connect算法实现
│   ├── goal_biased_sampler.py       # 目标偏置采样器
│   ├── hybrid_obstacle_map.py       # 混合障碍物地图（AABB+Octomap）
│   └── path_optimizer.py            # 路径平滑优化
├── obstacle_mapping/
│   ├── cable_mask_to_octomap.py     # 线缆掩膜→Octomap转换
│   ├── pointcloud_to_octomap.py     # 点云→Octomap构建
│   └── dynamic_map_update.py        # 动态地图更新
├── robot_interface/
│   ├── ur5_interface.py             # UR5机械臂接口（URScript/ROS）
│   └── moveit_wrapper.py             # MoveIt!封装
└── pipeline/
    └── autonomous_grasp_pipeline.py # 完整抓取流程
```

## 快速开始

### 1. 环境安装
```bash
# Python依赖
pip install -r requirements.txt

# OctoMap C++库（Ubuntu）
sudo apt-get install liboctomap-dev

# PyBullet
pip install pybullet
```

### 2. 训练Contact-GraspNet（可选，可使用预训练模型）
```bash
python grasp_generation/contact_graspnet/train.py \
    --data_dir ./data/grasp_dataset \
    --epochs 100 \
    --batch_size 32
```

### 3. 运行完整抓取流程
```python
from pipeline.autonomous_grasp_pipeline import AutonomousGraspPipeline

# 初始化（需要Ch2的视觉输出）
pipeline = AutonomousGraspPipeline(
    grasp_model_path="./weights/contact_graspnet.pt",
    robot_type="ur5",
    cable_mask=cable_mask_from_ch2,  # 来自第2章
    connector_pose=pose_6d_from_ch2  # 来自第2章
)

# 执行抓取
result = pipeline.execute_grasp(
    start_config=robot_current_joints,
    target_tag_id="A"
)

# 输出：{
#   'grasp_pose': {'t': ..., 'R': ..., 'w': ...},
#   'path': [...],  # 关节空间轨迹
#   'success': True
# }
```

### 4. 单独测试GRRT-Connect规划
```python
from path_planning.grrt_connect import GRRTConnect

planner = GRRTConnect(
    obstacle_map=hybrid_map,  # AABB + Octomap
    goal_bias=0.3,
    step_size=0.05
)

path = planner.plan(
    start=start_config,
    goal=goal_config,
    max_iterations=10000
)
```

## 开源算法与仓库参考

### 核心算法库
1. **Contact-GraspNet**: 
   - 原始仓库: https://github.com/NVlabs/contact_graspnet
   - 论文: "Contact-GraspNet: Efficient 6-DoF Grasp Generation in Cluttered Scenarios"
2. **PointNet++**: 
   - PyTorch实现: https://github.com/erikwijmans/Pointnet2_PyTorch
3. **OMPL (路径规划)**:
   - 官网: https://ompl.kavrakilab.org/
   - Python绑定: `pip install ompl`
4. **OctoMap**:
   - C++库: https://octomap.github.io/
   - Python绑定: `pip install octomap-python` 或使用Open3D的Octomap接口

### 机器人接口
1. **MoveIt!**: https://moveit.ros.org/
2. **PyBullet**: https://pybullet.org/ (物理仿真与IK求解)
3. **UR机器人SDK**: 
   - URScript: https://www.universal-robots.com/products/ur-software/urscript/
   - ROS驱动: `universal_robots`包

### 碰撞检测
1. **FCL (Flexible Collision Library)**: https://github.com/flexible-collision-library/fcl
2. **Open3D碰撞检测**: 内置碰撞检测功能

## 关键算法实现细节

### 1. 抓取位姿数学建模
```python
# SE(3)空间抓取位姿
g = {
    'translation': t,      # R^3
    'rotation': R,        # SO(3)
    'width': w,           # 夹爪张开宽度
    'score': s            # 置信度 [0, 1]
}
```

### 2. 多约束评分函数
```python
S_total(g_i) = w1 * S_quality(g_i) + 
                w2 * S_clearance(g_i) + 
                w3 * S_align(g_i)
```

### 3. GRRT-Connect目标偏置采样
```python
if random() < P_goal:
    q_rand = q_goal  # 直接向目标采样
else:
    q_rand = random_sample(C_free)  # 随机采样
```

## 与前后章节的接口

### 输入（来自第2章）
- **6D位姿** (`pose_6d`): 作为抓取生成的种子点
- **线缆掩膜** (`cable_mask`): 映射为3D障碍物地图
- **标签ID** (`tag_id`): 确定抓取目标

### 输出（到第4章）
- **抓取位姿** (`grasp_pose`): 机械臂执行抓取的目标配置
- **规划路径** (`path`): 无碰撞关节轨迹
- **线缆形态信息** (`cable_state`): 抓取后的线缆状态（用于装配阶段）

## 评估指标

- **抓取成功率**: 50次独立实验的成功率
- **规划时间**: 从接收到任务到完成规划的平均耗时
- **路径长度**: 配置空间中的总路径长度
- **碰撞次数**: 与线缆/舱壁的碰撞统计

## 注意事项

1. **实时性要求**: 完整抓取流程（生成+筛选+规划）需在5秒内完成
2. **线缆动态性**: 抓取过程中线缆形态会变化，需实时更新Octomap
3. **狭窄空间**: 机舱环境空间受限，规划算法需高效处理局部极小值
4. **任务相容性**: 抓取姿态必须考虑后续装配方向，避免二次调整

## 仿真环境

### PyBullet仿真场景
- 6自由度UR5机械臂模型
- 模拟航空机舱环境（刚性舱壁+柔性线缆）
- 物理引擎精度: 240Hz

### 真机部署
- UR5e机械臂
- Robotiq 2F-85夹爪
- RealSense D435i相机（手眼配置）

## 待实现功能

- [ ] 动态障碍物预测（线缆运动预测）
- [ ] 多目标抓取优化（同时抓取多个连接器）
- [ ] 抓取失败恢复策略
- [ ] 在线学习抓取策略优化

## 作者

哈尔滨工业大学机电工程学院

## 许可证

本项目为学术研究用途，遵循相关开源许可证。

