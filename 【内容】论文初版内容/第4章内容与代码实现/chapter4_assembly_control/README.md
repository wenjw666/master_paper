# 第4章：基于深度强化学习的电连接器装配方法代码实现

## 项目概述

本项目实现了面向航空电连接器装配的智能控制系统，融合力位混合控制与深度强化学习（SAC），解决刚柔耦合干扰下的精密轴孔装配难题。

## 核心功能模块

### 1. 力位混合控制 (`hybrid_force_position_control/`)
- **功能**：底层柔顺控制，解耦位置控制与力控制
- **核心组件**：
  1. **阻抗控制器**：内环柔顺性保证
  2. **视觉前馈补偿**：利用Ch2线缆方向向量计算前馈力
- **技术栈**：
  - 实时控制循环（500Hz）
  - 力传感器接口（ATI Gamma）
  - 重力补偿算法

### 2. 强化学习环境 (`rl_environment/`)
- **功能**：构建符合MDP的装配仿真环境
- **环境特性**：
  - 状态空间：位姿偏差、速度、力/力矩、线缆方向向量
  - 动作空间：连续6DOF位姿增量
  - 奖励函数：距离引导 + 力安全约束 + 稀疏完成奖励
- **技术栈**：
  - [Gymnasium](https://github.com/Farama-Foundation/Gymnasium) (原OpenAI Gym)
  - PyBullet物理引擎
  - 自定义环境封装

### 3. SAC算法实现 (`sac_algorithm/`)
- **功能**：Soft Actor-Critic策略学习
- **核心特性**：
  - 最大熵强化学习框架
  - 双Q网络（Clipped Double Q-Learning）
  - 重参数化技巧（Reparameterization Trick）
- **技术栈**：
  - PyTorch
  - [Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3) (可选，作为参考)

### 4. Sim-to-Real迁移 (`sim_to_real/`)
- **功能**：仿真训练到真机部署的迁移策略
- **核心方法**：
  - 域随机化（Domain Randomization）
  - 物理参数扰动（线缆刚度、摩擦系数、观测噪声）
- **技术栈**：
  - PyBullet域随机化
  - 模型导出与部署工具

### 5. 动力学建模 (`dynamics_modeling/`)
- **功能**：含柔性线缆干扰的动力学方程
- **理论模型**：
  - 刚柔耦合动力学
  - Kirchhoff弹性杆模型（线缆）
  - 接触力建模

## 依赖环境

### Python环境
- Python 3.8+
- PyTorch 1.12+ (CUDA 11.6+)
- NumPy, SciPy
- Matplotlib

### 强化学习库
- Gymnasium 0.28+
- Stable-Baselines3 (可选)

### 物理仿真
- PyBullet 3.2+

### 实时控制（真机）
- ROS Noetic (用于力传感器接口)
- ATI力传感器驱动

## 项目结构

```
chapter4_assembly_control/
├── README.md
├── requirements.txt
├── hybrid_force_position_control/
│   ├── impedance_controller.py      # 阻抗控制器
│   ├── visual_feedforward.py       # 视觉前馈补偿（使用Ch2线缆向量）
│   ├── force_position_hybrid.py    # 力位混合控制主模块
│   ├── gravity_compensation.py     # 重力补偿
│   └── ft_sensor_interface.py      # 力传感器接口（ATI Gamma）
├── rl_environment/
│   ├── connector_assembly_env.py   # 装配环境主类
│   ├── state_space.py              # 状态空间定义
│   ├── action_space.py             # 动作空间定义
│   ├── reward_function.py          # 奖励函数设计
│   └── observation_wrapper.py      # 观测包装器（归一化等）
├── sac_algorithm/
│   ├── sac.py                      # SAC算法核心实现
│   ├── actor.py                    # Actor网络（策略网络）
│   ├── critic.py                   # Critic网络（双Q网络）
│   ├── replay_buffer.py            # 经验回放缓冲区
│   └── utils/
│       ├── network_utils.py        # 网络工具函数
│       └── training_utils.py       # 训练辅助函数
├── sim_to_real/
│   ├── domain_randomization.py     # 域随机化策略
│   ├── model_export.py             # 模型导出（ONNX/TorchScript）
│   └── deployment_utils.py         # 真机部署工具
├── dynamics_modeling/
│   ├── cable_dynamics.py           # 线缆动力学模型（Kirchhoff）
│   ├── contact_dynamics.py         # 接触动力学
│   └── system_dynamics.py          # 完整系统动力学
├── training/
│   ├── train_sac.py                # SAC训练主脚本
│   ├── config/
│   │   └── sac_config.yaml         # 超参数配置
│   └── scripts/
│       ├── train_baseline.sh        # 训练脚本
│       └── evaluate_policy.py      # 策略评估
└── pipeline/
    └── assembly_control_pipeline.py # 完整装配控制流程
```

## 快速开始

### 1. 环境安装
```bash
pip install -r requirements.txt

# PyBullet
pip install pybullet

# Gymnasium
pip install gymnasium
```

### 2. 训练SAC策略（仿真环境）
```bash
python training/train_sac.py \
    --config config/sac_config.yaml \
    --total_steps 1000000 \
    --save_dir ./checkpoints
```

### 3. 评估训练好的策略
```python
from training.evaluate_policy import evaluate_policy

policy = load_policy("./checkpoints/sac_final.pt")
results = evaluate_policy(
    policy=policy,
    env=connector_assembly_env,
    n_episodes=50
)
# 输出：成功率、平均奖励、平均耗时等
```

### 4. 真机部署（力位混合控制 + SAC策略）
```python
from pipeline.assembly_control_pipeline import AssemblyControlPipeline

pipeline = AssemblyControlPipeline(
    sac_model_path="./checkpoints/sac_final.pt",
    cable_vector=cable_vector_from_ch2,  # 来自第2章
    target_pose=target_connector_pose,
    ft_sensor=ati_gamma_sensor
)

# 执行装配
result = pipeline.execute_assembly(
    start_pose=pre_assembly_pose,
    target_pose=final_assembly_pose
)
```

### 5. 单独测试力位混合控制
```python
from hybrid_force_position_control.force_position_hybrid import HybridController

controller = HybridController(
    impedance_params={'M': ..., 'B': ..., 'K': ...},
    visual_feedforward=True,
    cable_vector=cable_vector  # 来自Ch2
)

# 控制循环
while not assembly_complete:
    force_measured = ft_sensor.read()
    pose_error = compute_pose_error(current_pose, target_pose)
    
    # 计算前馈力（抵消线缆干扰）
    feedforward_force = controller.compute_feedforward(cable_vector)
    
    # 阻抗控制
    control_torque = controller.compute_control(
        pose_error=pose_error,
        force_measured=force_measured,
        feedforward=feedforward_force
    )
    
    robot.send_torque(control_torque)
```

## 开源算法与仓库参考

### 核心算法库
1. **SAC (Soft Actor-Critic)**:
   - 原始论文实现: https://github.com/rail-berkeley/softlearning
   - Stable-Baselines3实现: https://stable-baselines3.readthedocs.io/en/master/modules/sac.html
   - PyTorch参考: https://github.com/pranz24/pytorch-soft-actor-critic
2. **Gymnasium (原OpenAI Gym)**:
   - 官网: https://gymnasium.farama.org/
3. **PyBullet**:
   - 官网: https://pybullet.org/
   - 文档: https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA

### 力控相关
1. **ATI力传感器SDK**: 
   - 官方驱动: https://www.ati-ia.com/products/ft/ft_software.aspx
2. **ROS力控接口**:
   - `geometry_msgs/Wrench`消息类型
   - `force_torque_sensor`包

### 强化学习工具
1. **Stable-Baselines3**: 
   - 文档: https://stable-baselines3.readthedocs.io/
   - 包含SAC、PPO、DDPG等多种算法
2. **Weights & Biases (W&B)**: 训练可视化（可选）
   - https://wandb.ai/

## 关键算法实现细节

### 1. 力位混合控制律
```python
# 控制律公式
tau = M * (x_dd_desired - x_dd_current) + 
      B * (x_d_desired - x_d_current) + 
      K * (x_desired - x_current) - 
      F_ext + 
      F_feedforward  # 视觉前馈项
```

### 2. SAC最大熵目标函数
```python
J(π) = E[Q(s,a) - α * log π(a|s)]
# α: 温度系数（自动调节）
```

### 3. 奖励函数设计
```python
r_t = w1 * r_distance +      # 距离引导
      w2 * r_force_safety +   # 力安全约束
      w3 * r_completion       # 稀疏完成奖励
```

### 4. 域随机化参数
```python
cable_stiffness = uniform(0.5, 2.0)  # 线缆刚度随机化
friction_coeff = uniform(0.1, 0.5)   # 摩擦系数随机化
sensor_noise = N(0, 0.1)              # 观测噪声
```

## 与前后章节的接口

### 输入（来自第2、3章）
- **线缆方向向量** (`cable_vector`): 来自Ch2，用于前馈力计算
- **抓取位姿** (`grasp_pose`): 来自Ch3，作为装配起始点
- **目标插座位姿** (`target_socket_pose`): 装配终点

### 输出
- **装配成功标志** (`assembly_success`): 布尔值
- **接触力曲线** (`force_history`): 用于分析
- **装配轨迹** (`assembly_trajectory`): 位姿序列

## 评估指标

- **装配成功率**: 50次独立实验的成功率
- **平均装配耗时**: 从接触到锁紧的平均时间
- **最大接触力**: 装配过程中的峰值力（需<10N）
- **力峰值方差**: 力一致性指标（越小越好）

## 训练配置示例

```yaml
# sac_config.yaml
algorithm: "SAC"
total_steps: 1000000
batch_size: 256
learning_rate:
  actor: 3e-4
  critic: 3e-4
  alpha: 3e-4
replay_buffer_size: 1000000
gamma: 0.99
tau: 0.005  # 软更新系数
target_update_interval: 1
alpha_auto_tune: true
```

## 注意事项

1. **实时性要求**: 控制循环需在500Hz运行，SAC策略推理需<10ms
2. **力传感器校准**: ATI传感器需进行重力补偿，零漂控制在0.2N以内
3. **Sim-to-Real鸿沟**: 域随机化是关键，需覆盖真实物理参数分布
4. **安全性**: 装配过程中需设置力阈值急停（如>30N）

## 仿真环境配置

### PyBullet环境参数
- 控制频率: 30Hz
- 物理引擎频率: 240Hz
- 线缆模型: 离散化刚性连杆串联（Linked-Segment Model）
- 接触模型: 点接触 + 摩擦

### 真机环境
- UR5e机械臂
- ATI Gamma六维力/力矩传感器
- Robotiq 2F-85夹爪
- 控制频率: 500Hz

## 待实现功能

- [ ] 在线策略适应（Online Policy Adaptation）
- [ ] 多任务学习（Multi-task Learning）
- [ ] 不确定性估计（Uncertainty Estimation）
- [ ] 失败恢复策略（Error Recovery）

## 作者

哈尔滨工业大学机电工程学院

## 许可证

本项目为学术研究用途，遵循相关开源许可证。

