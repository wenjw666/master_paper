#!/bin/bash
# 第4章装配控制系统环境配置脚本

echo "=== 第4章：电连接器装配控制系统环境配置 ==="

# 创建必要的目录
mkdir -p checkpoints
mkdir -p logs
mkdir -p results
mkdir -p data/training
mkdir -p external

# 安装Python依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 克隆SAC参考实现（可选）
echo "克隆SAC参考实现..."
if [ ! -d "external/pytorch-soft-actor-critic" ]; then
    git clone https://github.com/pranz24/pytorch-soft-actor-critic.git external/pytorch-soft-actor-critic
fi

# 安装PyBullet
echo "安装PyBullet..."
pip install pybullet

# 安装Gymnasium
echo "安装Gymnasium..."
pip install gymnasium[all]

# 安装Stable-Baselines3（可选）
echo "安装Stable-Baselines3（可选）..."
pip install stable-baselines3[extra] || echo "警告: Stable-Baselines3安装失败"

# 下载预训练模型（如果有）
echo "下载预训练模型..."
mkdir -p checkpoints/pretrained
# 预训练模型需要从训练结果中获取

echo "=== 环境配置完成 ==="
echo "下一步："
echo "1. 配置PyBullet仿真环境"
echo "2. 开始训练: python training/train_sac.py"
echo "3. 评估策略: python training/evaluate_policy.py"

