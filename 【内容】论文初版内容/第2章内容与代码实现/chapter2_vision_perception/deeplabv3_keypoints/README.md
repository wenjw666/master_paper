# DeepLabV3+ 关键点特征提取模块

## 功能概述

本模块实现第二级视觉感知网络，基于DeepLabV3+在局部ROI中提取被遮挡关键点，输出高斯热力图和线缆分割掩膜。

## 开源库引用

### DeepLabV3+ PyTorch实现
- **GitHub**: https://github.com/VainF/DeepLabV3Plus-Pytorch
- **安装命令**:
  ```bash
  git clone https://github.com/VainF/DeepLabV3Plus-Pytorch.git
  cd DeepLabV3Plus-Pytorch
  pip install -r requirements.txt
  ```

### 替代方案（TensorFlow版本）
- **GitHub**: https://github.com/tensorflow/models/tree/master/research/deeplab
- 注意：本实现推荐使用PyTorch版本，便于与YOLOv8集成

## 目录结构

```
deeplabv3_keypoints/
├── README.md                    # 本文件
├── train.py                    # 训练脚本
├── inference.py                # 推理接口
├── models/
│   └── deeplabv3_keypoint.py   # 改进的输出头（热力图+分割）
└── utils/
    ├── __init__.py
    ├── heatmap_generator.py    # 高斯热力图生成
    └── keypoint_extractor.py    # 热力图峰值提取
```

## 核心功能

### 1. 改进的网络架构
- **Backbone**: ResNet101（或ResNet50）
- **ASPP模块**: 空洞空间金字塔池化，扩大感受野
- **双输出头**:
  - 关键点检测分支：输出N个热力图（N=关键点数量）
  - 线缆分割分支：输出线缆二值掩膜

### 2. 高斯热力图生成
对于关键点 $(x_k, y_k)$，生成目标热力图：
$$H_k(x,y) = \exp \left( - \frac{(x-x_k)^2 + (y-y_k)^2}{2\sigma^2} \right)$$

其中 $\sigma=2$ 控制扩散程度。

### 3. 损失函数
- **关键点损失**: MSE Loss（预测热力图 vs 真实热力图）
- **分割损失**: BCE Loss + Dice Loss

## 关键点定义

本研究中定义4个关键点：
1. **定位孔1** (hole_1)
2. **定位孔2** (hole_2)
3. **定位孔3** (hole_3)
4. **线缆根部** (cable_root)

## 使用方法

### 1. 准备ROI数据集
从YOLOv8检测结果中裁剪ROI区域：
```python
from yolov8_seg.inference import YOLOv8SegInference

yolo = YOLOv8SegInference("./weights/yolov8_seg.pt")
results = yolo.predict(rgb_image, target_tag_id="tag_A")
roi, coords = yolo.extract_roi(rgb_image, results['boxes'][0])
```

### 2. 训练模型
```bash
python train.py \
    --data_dir ./data/roi_cropped \
    --epochs 200 \
    --batch-size 8 \
    --backbone resnet101
```

### 3. 推理
```python
from inference import DeepLabV3KeypointInference

inference = DeepLabV3KeypointInference(
    model_path="./weights/deeplabv3_keypoints.pt"
)

keypoints, cable_mask = inference.predict(roi_image)
# keypoints: [(x1, y1), (x2, y2), ...]  # 4个关键点坐标
# cable_mask: 二值掩膜
```

## 输出接口

### 到位姿估计模块
- **关键点坐标**: 4个关键点的2D像素坐标
- **线缆掩膜**: 用于后续线缆方向向量计算

### 到第4章（装配控制）
- **线缆方向向量**: 从线缆掩膜提取的方向向量

## 评估指标

- **PCK (Percentage of Correct Keypoints)**: 关键点检测准确率
  - 阈值: 2mm, 5mm
- **mIoU**: 线缆分割的平均交并比

## 注意事项

1. **遮挡鲁棒性**: 网络需在关键点被遮挡时仍能预测（利用上下文信息）
2. **ROI尺寸**: 建议ROI尺寸为640x640或更大，保证关键点细节
3. **热力图精度**: σ值影响热力图精度，需根据关键点大小调整

