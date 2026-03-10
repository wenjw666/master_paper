@echo off
REM 第2章视觉感知系统环境配置脚本 (Windows)

echo === 第2章：电连接器视觉感知系统环境配置 ===

REM 创建必要的目录
if not exist "data\real" mkdir data\real
if not exist "data\synthetic" mkdir data\synthetic
if not exist "data\augmented" mkdir data\augmented
if not exist "weights" mkdir weights
if not exist "logs" mkdir logs
if not exist "results" mkdir results
if not exist "external" mkdir external

REM 安装Python依赖
echo 安装Python依赖...
pip install -r requirements.txt

REM 克隆YOLOv8仓库
echo 克隆YOLOv8仓库...
if not exist "external\ultralytics" (
    git clone https://github.com/ultralytics/ultralytics.git external\ultralytics
    cd external\ultralytics
    pip install -e .
    cd ..\..
)

REM 克隆DeepLabV3+ PyTorch版本
echo 克隆DeepLabV3+ PyTorch版本...
if not exist "external\DeepLabV3Plus-Pytorch" (
    git clone https://github.com/VainF/DeepLabV3Plus-Pytorch.git external\DeepLabV3Plus-Pytorch
    cd external\DeepLabV3Plus-Pytorch
    pip install -r requirements.txt
    cd ..\..
)

REM 克隆EPnP独立实现（可选）
echo 克隆EPnP独立实现（可选）...
if not exist "external\EPnP" (
    git clone https://github.com/jessecw/EPnP.git external\EPnP
)

echo === 环境配置完成 ===
echo 下一步：
echo 1. 运行相机标定: python calibration\camera_calibration.py
echo 2. 采集数据: python dataset\data_collection.py
echo 3. 开始训练: python yolov8_seg\train.py

pause

