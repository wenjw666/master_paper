#!/bin/bash
# 第2章视觉感知系统环境配置脚本

echo "=== 第2章：电连接器视觉感知系统环境配置 ==="

# 创建必要的目录
mkdir -p data/real
mkdir -p data/synthetic
mkdir -p data/augmented
mkdir -p weights
mkdir -p logs
mkdir -p results

# 安装Python依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 克隆YOLOv8仓库（如果需要自定义修改）
echo "克隆YOLOv8仓库..."
if [ ! -d "external/ultralytics" ]; then
    git clone https://github.com/ultralytics/ultralytics.git external/ultralytics
    cd external/ultralytics
    pip install -e .
    cd ../..
fi

# 克隆DeepLabV3+ PyTorch版本（推荐使用PyTorch版本，更易集成）
echo "克隆DeepLabV3+ PyTorch版本..."
if [ ! -d "external/DeepLabV3Plus-Pytorch" ]; then
    git clone https://github.com/VainF/DeepLabV3Plus-Pytorch.git external/DeepLabV3Plus-Pytorch
    cd external/DeepLabV3Plus-Pytorch
    pip install -r requirements.txt
    cd ../..
fi

# 克隆EPnP独立实现（可选，OpenCV已包含）
echo "克隆EPnP独立实现（可选）..."
if [ ! -d "external/EPnP" ]; then
    git clone https://github.com/jessecw/EPnP.git external/EPnP
fi

# 下载预训练模型（可选）
echo "下载预训练模型..."
mkdir -p weights/pretrained
# YOLOv8预训练模型会在首次使用时自动下载
# DeepLabV3+预训练模型需要手动下载

echo "=== 环境配置完成 ==="
echo "下一步："
echo "1. 运行相机标定: python calibration/camera_calibration.py"
echo "2. 采集数据: python dataset/data_collection.py"
echo "3. 开始训练: python yolov8_seg/train.py"

