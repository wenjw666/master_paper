@echo off
REM 第5章系统集成环境配置脚本 (Windows)
REM 注意: ROS主要在Linux上运行，Windows需要WSL或Docker

echo === 第5章：电连接器自主装配系统集成环境配置 ===
echo.
echo 注意: ROS系统主要在Linux环境下运行
echo Windows用户建议使用WSL2或Docker容器
echo.

REM 创建必要的目录
if not exist "calibration\calibration_data" mkdir calibration\calibration_data
if not exist "data_collection\experiments" mkdir data_collection\experiments
if not exist "logs" mkdir logs
if not exist "config" mkdir config

REM 安装Python依赖（非ROS部分）
echo 安装Python依赖...
pip install -r requirements.txt

echo.
echo === 环境配置完成（部分）===
echo.
echo 重要提示:
echo 1. ROS系统需要在Linux环境（Ubuntu 20.04 + ROS Noetic）下运行
echo 2. 建议使用WSL2或Docker容器
echo 3. 在Linux环境下运行setup_environment.sh完成完整配置
echo.

pause

