@echo off
REM 第3章抓取规划系统环境配置脚本 (Windows)

echo === 第3章：电连接器自主抓取系统环境配置 ===

REM 创建必要的目录
if not exist "data\grasp_dataset" mkdir data\grasp_dataset
if not exist "weights" mkdir weights
if not exist "logs" mkdir logs
if not exist "results" mkdir results
if not exist "external" mkdir external

REM 安装Python依赖
echo 安装Python依赖...
pip install -r requirements.txt

REM 克隆Contact-GraspNet仓库
echo 克隆Contact-GraspNet仓库...
if not exist "external\contact_graspnet" (
    git clone https://github.com/NVlabs/contact_graspnet.git external\contact_graspnet
    cd external\contact_graspnet
    pip install -e .
    cd ..\..
)

REM 克隆PointNet++实现
echo 克隆PointNet++实现...
if not exist "external\Pointnet2_PyTorch" (
    git clone https://github.com/erikwijmans/Pointnet2_PyTorch.git external\Pointnet2_PyTorch
    cd external\Pointnet2_PyTorch
    pip install -r requirements.txt
    pip install -e .
    cd ..\..
)

REM 安装OctoMap Python绑定（Windows上可能需要预编译的wheel）
echo 尝试安装OctoMap Python绑定...
pip install octomap-python || echo 警告: octomap-python安装失败，将使用Open3D的Octomap接口

REM 安装OMPL（路径规划库）
echo 安装OMPL...
pip install ompl || echo 警告: OMPL Python绑定安装失败，可能需要从源码编译

echo === 环境配置完成 ===
echo 下一步：
echo 1. 准备抓取数据集
echo 2. 训练或加载Contact-GraspNet模型
echo 3. 运行抓取规划: python pipeline\autonomous_grasp_pipeline.py

pause

