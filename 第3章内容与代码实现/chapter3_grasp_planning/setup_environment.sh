#!/bin/bash
# 第3章抓取规划系统环境配置脚本

echo "=== 第3章：电连接器自主抓取系统环境配置 ==="

# 创建必要的目录
mkdir -p data/grasp_dataset
mkdir -p weights
mkdir -p logs
mkdir -p results
mkdir -p external

# 安装Python依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 克隆Contact-GraspNet仓库
echo "克隆Contact-GraspNet仓库..."
if [ ! -d "external/contact_graspnet" ]; then
    git clone https://github.com/NVlabs/contact_graspnet.git external/contact_graspnet
    cd external/contact_graspnet
    pip install -e .
    cd ../..
fi

# 克隆PointNet++实现
echo "克隆PointNet++实现..."
if [ ! -d "external/Pointnet2_PyTorch" ]; then
    git clone https://github.com/erikwijmans/Pointnet2_PyTorch.git external/Pointnet2_PyTorch
    cd external/Pointnet2_PyTorch
    pip install -r requirements.txt
    pip install -e .
    cd ../..
fi

# 安装OctoMap（需要系统包管理器）
echo "安装OctoMap C++库..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y liboctomap-dev liboctomap1.9
elif command -v brew &> /dev/null; then
    brew install octomap
fi

# 尝试安装OctoMap Python绑定
echo "尝试安装OctoMap Python绑定..."
pip install octomap-python || echo "警告: octomap-python安装失败，将使用Open3D的Octomap接口"

# 安装OMPL（路径规划库）
echo "安装OMPL..."
pip install ompl || echo "警告: OMPL Python绑定安装失败，可能需要从源码编译"

# 下载预训练模型（可选）
echo "下载预训练模型..."
mkdir -p weights/pretrained
# Contact-GraspNet预训练模型需要从官方仓库下载
echo "请从 https://github.com/NVlabs/contact_graspnet 下载预训练模型"

echo "=== 环境配置完成 ==="
echo "下一步："
echo "1. 准备抓取数据集"
echo "2. 训练或加载Contact-GraspNet模型"
echo "3. 运行抓取规划: python pipeline/autonomous_grasp_pipeline.py"

