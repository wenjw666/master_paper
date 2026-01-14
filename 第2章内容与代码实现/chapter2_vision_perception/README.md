# 第2章：基于深度学习的电连接器识别与位姿估计代码实现

## 项目概述

本项目实现了面向航空制造场景的电连接器视觉感知系统，采用"由粗到精"的级联式架构，解决线缆遮挡下的目标识别、位姿估计和线缆形态提取问题。

## 核心功能模块

### 1. 数据集制作与标注工具 (`dataset/`)
- **功能**：构建包含真实采集与仿真合成的混合数据集
- **主要组件**：
  - 数据采集脚本（RealSense D435i相机接口）
  - 标注工具（支持连接器壳体、线缆、标签ID的分层标注）
  - Blender合成数据生成脚本（域随机化）
  - 数据增强工具（高斯噪声、随机旋转、色彩抖动）

### 2. YOLOv8-seg 目标检测与实例分割 (`yolov8_seg/`)
- **功能**：第一级网络，实现多实例快速筛选、连接器检测、线缆分割和标签ID识别
- **技术栈**：
  - 基于 [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
  - CSPDarknet53 Backbone
  - 多任务损失函数（CIoU Loss + BCE Loss）
- **输出**：边界框、分割掩膜、分类ID、ROI裁剪

### 3. DeepLabV3+ 关键点特征提取 (`deeplabv3_keypoints/`)
- **功能**：第二级网络，在局部ROI中提取被遮挡关键点
- **技术栈**：
  - 基于 [DeepLabV3+](https://github.com/tensorflow/models/tree/master/research/deeplab)
  - ASPP（空洞空间金字塔池化）模块
  - 高斯热力图预测（替代直接坐标回归）
- **输出**：
  - 关键点热力图（3个定位孔 + 1个线缆根部）
  - 线缆分割掩膜

### 4. EPnP + RANSAC 位姿解算 (`pose_estimation/`)
- **功能**：从2D关键点解算6D位姿，抗外点干扰
- **技术栈**：
  - EPnP算法（Efficient Perspective-n-Point）
  - RANSAC外点剔除
  - Levenberg-Marquardt非线性优化
- **输入**：3D模型关键点（CAD已知）+ 2D图像关键点（DeepLabV3+预测）
- **输出**：6D位姿（旋转矩阵R + 平移向量t）

### 5. 相机标定工具 (`calibration/`)
- **功能**：相机内参标定、手眼标定
- **技术栈**：
  - OpenCV相机标定
  - Tsai-Lenz手眼标定算法

## 依赖环境

### Python环境
- Python 3.8+
- PyTorch 1.12+ (CUDA 11.6+)
- OpenCV 4.5+
- NumPy, SciPy
- Matplotlib, Open3D

### 深度学习框架
- Ultralytics YOLOv8
- TensorFlow 2.x 或 PyTorch (DeepLabV3+)

### 硬件要求
- NVIDIA GPU (推荐RTX 3090或以上，用于训练)
- Intel RealSense D435i深度相机
- 至少16GB RAM

## 项目结构

```
chapter2_vision_perception/
├── README.md
├── requirements.txt
├── dataset/
│   ├── data_collection.py          # RealSense数据采集
│   ├── annotation_tool.py          # 标注工具（LabelMe/自定义）
│   ├── blender_synthesis.py        # Blender合成数据生成
│   └── data_augmentation.py        # 数据增强
├── yolov8_seg/
│   ├── train.py                    # YOLOv8-seg训练脚本
│   ├── inference.py                # 推理接口
│   ├── config/
│   │   └── connector_config.yaml   # 数据集配置
│   └── models/
│       └── custom_yolov8_seg.py    # 自定义网络结构
├── deeplabv3_keypoints/
│   ├── train.py                    # DeepLabV3+训练脚本
│   ├── inference.py                 # 关键点预测
│   ├── models/
│   │   └── deeplabv3_keypoint.py   # 改进的输出头（热力图+分割）
│   └── utils/
│       ├── heatmap_generator.py    # 高斯热力图生成
│       └── keypoint_extractor.py   # 热力图峰值提取
├── pose_estimation/
│   ├── epnp_solver.py              # EPnP算法实现
│   ├── ransac_pnp.py               # RANSAC+PnP组合
│   ├── refine_pose.py              # LM优化
│   └── utils/
│       └── projection_utils.py     # 投影与重投影误差计算
├── calibration/
│   ├── camera_calibration.py       # 相机内参标定
│   └── hand_eye_calibration.py     # 手眼标定
└── pipeline/
    └── cascade_vision_pipeline.py  # 级联感知完整流程
```

## 快速开始

### 1. 环境安装
```bash
pip install -r requirements.txt
```

### 2. 数据集准备
```bash
# 采集真实数据
python dataset/data_collection.py --output_dir ./data/real

# 生成合成数据（需要Blender环境）
python dataset/blender_synthesis.py --output_dir ./data/synthetic

# 数据增强
python dataset/data_augmentation.py --input_dir ./data --output_dir ./data/augmented
```

### 3. 训练YOLOv8-seg
```bash
python yolov8_seg/train.py \
    --data ./data/dataset.yaml \
    --epochs 300 \
    --batch-size 16 \
    --img-size 640
```

### 4. 训练DeepLabV3+
```bash
python deeplabv3_keypoints/train.py \
    --data_dir ./data/roi_cropped \
    --epochs 200 \
    --batch-size 8
```

### 5. 运行完整推理流程
```python
from pipeline.cascade_vision_pipeline import CascadeVisionPipeline

pipeline = CascadeVisionPipeline(
    yolov8_model_path="./weights/yolov8_seg.pt",
    deeplab_model_path="./weights/deeplabv3_keypoints.pt",
    camera_intrinsic="./calibration/camera_params.yaml"
)

# 输入RGB-D图像
result = pipeline.inference(rgb_image, depth_image)
# 输出：{
#   'tag_id': 'A',
#   'pose_6d': {'R': ..., 't': ...},
#   'cable_mask': ...,
#   'cable_vector': ...
# }
```

## 开源算法与仓库参考

### 核心算法库
1. **YOLOv8**: https://github.com/ultralytics/ultralytics
2. **DeepLabV3+**: 
   - TensorFlow版本: https://github.com/tensorflow/models/tree/master/research/deeplab
   - PyTorch版本: https://github.com/VainF/DeepLabV3Plus-Pytorch
3. **EPnP算法**: 
   - OpenCV实现: `cv2.solvePnP()` (EPnP模式)
   - 独立实现: https://github.com/jessecw/EPnP
4. **RANSAC**: 
   - scikit-learn: `sklearn.linear_model.RANSACRegressor`
   - OpenCV: `cv2.findHomography()` (RANSAC模式)

### 辅助工具库
1. **RealSense SDK**: https://github.com/IntelRealSense/librealsense
2. **Open3D**: 点云处理 (https://www.open3d.org/)
3. **LabelMe**: 图像标注工具 (https://github.com/wkentaro/labelme)
4. **Blender Python API**: 合成数据生成

## 评估指标

- **目标检测**: mAP@0.5, mAP@0.5:0.95
- **实例分割**: mIoU (Mean Intersection over Union)
- **位姿估计**: ADD-S (Average Distance of Model Points for Symmetric Object)
  - 阈值: 2mm (高精度), 5mm (抓取容许)
- **关键点检测**: PCK (Percentage of Correct Keypoints)

## 与后续章节的接口

### 输出到第3章（抓取规划）
- **6D位姿** (`pose_6d`): 作为GRRT-Connect的目标终点
- **线缆掩膜** (`cable_mask`): 映射为3D点云，构建Octomap障碍物地图
- **标签ID** (`tag_id`): 确定抓取目标

### 输出到第4章（装配控制）
- **线缆方向向量** (`cable_vector`): 用于力位混合控制的前馈补偿

## 注意事项

1. **数据标注质量**：线缆掩膜的标注精度直接影响后续障碍物地图的准确性
2. **相机标定精度**：手眼标定误差需控制在0.5mm以内，否则位姿解算会累积误差
3. **遮挡率适应性**：模型需在10%-50%遮挡率范围内保持鲁棒性
4. **实时性要求**：完整推理流程需在100ms内完成（30fps相机）

## 待实现功能

- [ ] 在线学习与模型微调
- [ ] 多相机融合（全局+手眼）
- [ ] 时序信息融合（Kalman滤波）
- [ ] 模型量化与部署优化

## 作者

哈尔滨工业大学机电工程学院

## 许可证

本项目为学术研究用途，遵循相关开源许可证。

