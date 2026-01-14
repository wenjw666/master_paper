# 端到端6D抓取生成模块

## 功能概述

本模块实现基于Contact-GraspNet的端到端6D抓取位姿生成，从点云直接预测候选抓取位姿。

## 开源库引用

### Contact-GraspNet
- **GitHub**: https://github.com/NVlabs/contact_graspnet
- **论文**: "Contact-GraspNet: Efficient 6-DoF Grasp Generation in Cluttered Scenarios"
- **安装命令**:
  ```bash
  git clone https://github.com/NVlabs/contact_graspnet.git
  cd contact_graspnet
  pip install -e .
  ```

### PointNet++
- **GitHub**: https://github.com/erikwijmans/Pointnet2_PyTorch
- **安装命令**:
  ```bash
  git clone https://github.com/erikwijmans/Pointnet2_PyTorch.git
  cd Pointnet2_PyTorch
  pip install -r requirements.txt
  pip install -e .
  ```

## 目录结构

```
grasp_generation/
├── README.md                    # 本文件
├── inference.py                # 抓取生成推理接口
├── utils/
│   ├── pointcloud_utils.py     # 点云预处理工具 ✅
│   └── grasp_visualization.py  # 抓取位姿可视化
└── contact_graspnet/           # Contact-GraspNet实现（从开源仓库集成）
    ├── model.py
    ├── train.py
    └── inference.py
```

## 核心功能

### 1. 点云预处理
- **RGB-D融合**: 将RGB图像和深度图像转换为点云
- **背景去除**: 利用Ch2输出的连接器掩膜去除无关背景
- **体素下采样**: 将点云密度降至0.005m

### 2. 抓取位姿数学建模
在SE(3)空间中，抓取位姿 $g$ 表示为：
$$g = \{t, R, w\}$$

其中：
- $t \in \mathbb{R}^3$: 抓取点位置（平移向量）
- $R \in SO(3)$: 抓取姿态（旋转矩阵）
- $w \in \mathbb{R}$: 夹爪张开宽度

### 3. 损失函数
$$L_{grasp} = L_{score} + \lambda L_{width} + \gamma L_{add-s}$$

- $L_{score}$: 抓取置信度损失（BCE）
- $L_{width}$: 夹爪宽度回归损失（L2）
- $L_{add-s}$: 位姿精度损失（ADD-S度量）
- $\lambda=0.1, \gamma=0.5$

### 4. 基于位姿先验的加速策略
将Ch2输出的6D位姿作为种子点，优先在连接器表面附近采样候选抓取点。

## 使用方法

### 1. 点云预处理
```python
from utils.pointcloud_utils import preprocess_pointcloud

# 使用Ch2的掩膜进行背景去除
pcd = preprocess_pointcloud(
    rgb_image=rgb_image,
    depth_image=depth_image,
    camera_intrinsic=K,
    connector_mask=connector_mask_from_ch2,  # 来自第2章
    voxel_size=0.005
)
```

### 2. 抓取生成（使用预训练模型）
```python
from inference import GraspGenerator

generator = GraspGenerator(
    model_path="./weights/contact_graspnet.pt",
    device="cuda"
)

# 生成候选抓取位姿
candidate_grasps = generator.generate_grasps(
    pointcloud=pcd,
    connector_pose=pose_6d_from_ch2  # 来自Ch2，作为种子点
)

# 输出: List of {
#     'translation': np.array(3,),
#     'rotation': np.array(3x3),
#     'width': float,
#     'score': float
# }
```

### 3. 可视化抓取位姿
```python
from utils.grasp_visualization import visualize_grasps

visualize_grasps(
    pointcloud=pcd,
    grasps=candidate_grasps,
    top_k=10  # 显示置信度最高的10个
)
```

## 输出接口

### 到抓取筛选模块
- **候选抓取位姿列表**: 包含位置、姿态、宽度和置信度
- **点云信息**: 用于碰撞检测

## 注意事项

1. **点云质量**: 预处理后的点云需保证足够的点密度
2. **位姿先验**: Ch2的位姿估计精度直接影响抓取生成质量
3. **实时性**: 抓取生成需在1秒内完成

