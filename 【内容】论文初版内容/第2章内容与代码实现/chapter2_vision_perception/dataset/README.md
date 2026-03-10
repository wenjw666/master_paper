# 数据集制作与标注工具模块

## 功能概述

本模块负责构建面向航空电连接器装配场景的高质量数据集，包括真实数据采集、合成数据生成、数据标注和数据增强等功能。

## 目录结构

```
dataset/
├── README.md                    # 本文件
├── data_collection.py          # RealSense D435i数据采集脚本
├── annotation_tool.py          # 标注工具（基于LabelMe扩展）
├── blender_synthesis.py        # Blender合成数据生成
├── data_augmentation.py        # 数据增强工具
├── dataset_converter.py        # 数据集格式转换（YOLO/COCO等）
└── utils/
    ├── __init__.py
    ├── realsense_utils.py      # RealSense相机工具函数
    └── annotation_utils.py     # 标注工具函数
```

## 模块说明

### 1. data_collection.py - 真实数据采集

**功能**：使用RealSense D435i深度相机采集RGB-D图像数据

**主要特性**：
- 支持RGB (1920x1080) 和深度图像同步采集
- 自动保存图像对和时间戳
- 支持不同线缆形态场景采集（自然下垂、缠绕、弯折）
- 支持不同遮挡程度场景（轻度、中度、重度）

**使用方法**：
```bash
python data_collection.py \
    --output_dir ./data/real \
    --num_images 2500 \
    --resolution 1920 1080 \
    --fps 30
```

**依赖**：
- pyrealsense2
- OpenCV

### 2. annotation_tool.py - 标注工具

**功能**：基于LabelMe扩展的分层标注工具

**标注类别**：
1. **连接器壳体 (connector_shell)**: 边界框 + 像素级掩膜
2. **线缆 (cable)**: 像素级掩膜
3. **标签ID (tag_id)**: 文本标注（如"A", "B", "C"）

**使用方法**：
```bash
# 启动标注工具
python annotation_tool.py --input_dir ./data/real/images

# 标注完成后，转换为YOLO格式
python dataset_converter.py \
    --input_format labelme \
    --output_format yolo \
    --input_dir ./data/real/annotations \
    --output_dir ./data/real/yolo_format
```

**依赖**：
- labelme
- OpenCV

### 3. blender_synthesis.py - Blender合成数据生成

**功能**：使用Blender生成高保真合成数据，通过域随机化增加数据多样性

**域随机化参数**：
- 光源位置与强度
- 背景纹理
- 线缆物理属性（刚度、长度、弯曲形态）
- 相机视角
- 材质属性

**使用方法**：
```bash
python blender_synthesis.py \
    --output_dir ./data/synthetic \
    --num_images 5000 \
    --connector_model ./models/connector.blend \
    --cable_model ./models/cable.blend
```

**依赖**：
- Blender (需要安装bpy模块)
- NumPy

**注意**：需要先准备Blender模型文件（.blend格式）

### 4. data_augmentation.py - 数据增强

**功能**：对训练集实施在线数据增强，提升模型泛化能力

**增强策略**：
1. **高斯噪声**：概率0.5，标准差σ=0.1
2. **随机旋转**：±180度
3. **色彩抖动**：亮度(Brightness=0.5)、对比度(Contrast=0.5)、饱和度(Saturation=0.5)
4. **随机翻转**：水平/垂直翻转
5. **随机裁剪与缩放**

**使用方法**：
```bash
python data_augmentation.py \
    --input_dir ./data/real \
    --output_dir ./data/augmented \
    --augment_config ./config/augmentation.yaml
```

**依赖**：
- albumentations
- OpenCV

### 5. dataset_converter.py - 数据集格式转换

**功能**：在不同数据集格式间转换（LabelMe ↔ YOLO ↔ COCO）

**支持的格式**：
- LabelMe JSON
- YOLO格式（.txt标注文件）
- COCO格式（JSON）

**使用方法**：
```bash
# LabelMe转YOLO
python dataset_converter.py \
    --input_format labelme \
    --output_format yolo \
    --input_dir ./data/annotations \
    --output_dir ./data/yolo

# YOLO转COCO
python dataset_converter.py \
    --input_format yolo \
    --output_format coco \
    --input_dir ./data/yolo \
    --output_dir ./data/coco
```

## 数据集组织规范

### 目录结构
```
data/
├── real/                        # 真实采集数据
│   ├── images/                  # RGB图像
│   ├── depth/                   # 深度图像
│   ├── annotations/             # 标注文件（LabelMe格式）
│   └── yolo_format/            # YOLO格式（转换后）
├── synthetic/                   # Blender合成数据
│   ├── images/
│   ├── depth/
│   └── annotations/
└── augmented/                   # 增强后数据
    ├── train/
    ├── val/
    └── test/
```

### 数据集划分
- 训练集：70% (3675张)
- 验证集：20% (1050张)
- 测试集：10% (525张)

## 标注规范

### 连接器壳体标注
- 类型：边界框 + 分割掩膜
- 格式：多边形点集或RLE编码

### 线缆标注
- 类型：分割掩膜（像素级）
- 要求：精确标注线缆轮廓，包括被遮挡部分

### 标签ID标注
- 类型：文本标注
- 格式：字符串（如"A", "B", "C"）
- 位置：标签所在区域中心点

## 数据质量检查

运行数据质量检查脚本：
```bash
python utils/check_dataset_quality.py \
    --data_dir ./data \
    --output_report ./reports/dataset_quality.html
```

检查项：
- 图像完整性
- 标注完整性
- 类别分布平衡性
- 遮挡率统计

## 注意事项

1. **标注精度**：线缆掩膜的标注精度直接影响后续障碍物地图的准确性
2. **数据平衡**：确保不同ID的连接器样本数量均衡
3. **遮挡多样性**：确保训练集包含10%-50%遮挡率的样本
4. **存储空间**：完整数据集（含深度图）约需50GB存储空间

## 待实现功能

- [ ] 自动标注工具（基于预训练模型辅助标注）
- [ ] 在线数据采集与标注一体化工具
- [ ] 数据质量自动评估与报告生成

