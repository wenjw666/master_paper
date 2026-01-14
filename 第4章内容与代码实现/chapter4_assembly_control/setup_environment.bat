@echo off
REM 第4章装配控制系统环境配置脚本 (Windows)

echo === 第4章：电连接器装配控制系统环境配置 ===

REM 创建必要的目录
if not exist "checkpoints" mkdir checkpoints
if not exist "logs" mkdir logs
if not exist "results" mkdir results
if not exist "data\training" mkdir data\training
if not exist "external" mkdir external

REM 安装Python依赖
echo 安装Python依赖...
pip install -r requirements.txt

REM 克隆SAC参考实现（可选）
echo 克隆SAC参考实现...
if not exist "external\pytorch-soft-actor-critic" (
    git clone https://github.com/pranz24/pytorch-soft-actor-critic.git external\pytorch-soft-actor-critic
)

REM 安装PyBullet
echo 安装PyBullet...
pip install pybullet

REM 安装Gymnasium
echo 安装Gymnasium...
pip install gymnasium[all]

REM 安装Stable-Baselines3（可选）
echo 安装Stable-Baselines3（可选）...
pip install stable-baselines3[extra] || echo 警告: Stable-Baselines3安装失败

echo === 环境配置完成 ===
echo 下一步：
echo 1. 配置PyBullet仿真环境
echo 2. 开始训练: python training\train_sac.py
echo 3. 评估策略: python training\evaluate_policy.py

pause

