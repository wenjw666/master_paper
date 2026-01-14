# YOLOv8-seg 目标检测与实例分割模块

## 功能概述

本模块实现第一级视觉感知网络，基于YOLOv8-seg进行多实例快速筛选、连接器检测、线缆分割和标签ID识别。

## 开源库引用

### Ultralytics YOLOv8
- **GitHub**: https://github.com/ultralytics/ultralytics
- **安装命令**:
  ```bash
  pip install ultralytics
  # 或从源码安装（用于自定义修改）
  git clone https://github.com/ultralytics/ultralytics.git
  cd ultralytics
  pip install -e .
  ```

## 目录结构

```
yolov8_seg/
├── README.md                    # 本文件
├── train.py                    # 训练脚本
├── inference.py                # 推理接口
├── evaluate.py                 # 评估脚本
├── config/
│   └── connector_config.yaml   # 数据集配置文件
├── models/
│   └── custom_yolov8_seg.py   # 自定义网络结构（可选）
└── utils/
    ├── __init__.py
    ├── dataset_utils.py        # 数据集工具函数
    └── visualization.py        # 可视化工具
```

## 核心功能

### 1. 多任务输出
- **目标检测**: 连接器边界框
- **实例分割**: 连接器壳体和线缆掩膜
- **分类识别**: 标签ID识别

### 2. 损失函数
按照论文要求，使用多任务联合损失：
$$L_{total} = \lambda_{box} L_{box} + \lambda_{cls} L_{cls} + \lambda_{seg} L_{seg}$$

- $L_{box}$: CIoU Loss（边界框回归）
- $L_{cls}$: BCE Loss（分类）
- $L_{seg}$: BCE Loss（分割掩膜）

### 3. 网络配置
- **Backbone**: CSPDarknet53
- **Input Size**: 640x640
- **Batch Size**: 16
- **Epochs**: 300
- **Optimizer**: SGD (momentum=0.937)
- **Learning Rate**: 0.01 → 0.001 (Cosine Annealing)

## 使用方法

### 1. 准备数据集
确保数据集格式符合YOLO要求：
```
data/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    ├── val/
    └── test/
```

### 2. 配置数据集文件
编辑 `config/connector_config.yaml`:
```yaml
path: ./data
train: images/train
val: images/val
test: images/test

nc: 4  # 类别数：连接器壳体、线缆、标签A、标签B等
names:
  0: connector_shell
  1: cable
  2: tag_A
  3: tag_B
```

### 3. 训练模型
```bash
python train.py \
    --data config/connector_config.yaml \
    --epochs 300 \
    --batch-size 16 \
    --img-size 640 \
    --device 0
```

### 4. 推理
```python
from inference import YOLOv8SegInference

inference = YOLOv8SegInference(
    model_path="./weights/yolov8_seg.pt",
    conf_threshold=0.5
)

results = inference.predict(rgb_image)
# 输出：
# {
#   'boxes': [...],      # 边界框
#   'masks': [...],      # 分割掩膜
#   'class_ids': [...],  # 类别ID
#   'scores': [...],     # 置信度
#   'tag_ids': [...]     # 标签ID（从class_ids映射）
# }
```

### 5. 评估
```bash
python evaluate.py \
    --model ./weights/yolov8_seg.pt \
    --data config/connector_config.yaml \
    --output_dir ./results
```

## 输出接口

### 到DeepLabV3+模块（第2级网络）
- **ROI图像**: 根据检测到的边界框裁剪的高分辨率区域
- **目标掩膜**: 连接器掩膜（用于背景去除）

### 到位姿估计模块
- **标签ID**: 确定目标连接器
- **边界框**: 用于ROI裁剪

### 到第3章（抓取规划）
- **线缆掩膜**: 用于构建3D障碍物地图
- **标签ID**: 确定抓取目标

## 评估指标

- **mAP@0.5**: 平均精度（IoU阈值0.5）
- **mAP@0.5:0.95**: 平均精度（IoU阈值0.5-0.95）
- **mIoU**: 平均交并比（分割任务）

## 注意事项

1. **实时性**: 推理速度需<50ms（20fps以上）
2. **遮挡鲁棒性**: 模型需在10%-50%遮挡率下保持高精度
3. **多实例区分**: 需准确区分堆叠中的不同连接器实例

