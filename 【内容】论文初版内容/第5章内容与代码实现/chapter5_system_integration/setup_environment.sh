#!/bin/bash
# 第5章系统集成环境配置脚本

echo "=== 第5章：电连接器自主装配系统集成环境配置 ==="

# 检查ROS环境
if [ -z "$ROS_DISTRO" ]; then
    echo "警告: ROS环境未检测到，请先source ROS setup.bash"
    echo "例如: source /opt/ros/noetic/setup.bash"
fi

# 创建必要的目录
mkdir -p calibration/calibration_data
mkdir -p data_collection/experiments
mkdir -p logs
mkdir -p config

# 安装Python依赖（非ROS部分）
echo "安装Python依赖..."
pip install -r requirements.txt

# 安装ROS依赖（需要ROS环境）
if [ ! -z "$ROS_DISTRO" ]; then
    echo "安装ROS依赖..."
    
    # 检查并安装必要的ROS包
    echo "检查MoveIt!..."
    rospack find moveit_core > /dev/null 2>&1 || echo "警告: MoveIt!未安装"
    
    echo "检查SMACH..."
    rospack find smach > /dev/null 2>&1 || echo "警告: SMACH未安装，运行: sudo apt-get install ros-$ROS_DISTRO-executive-smach"
    
    echo "检查UR机器人驱动..."
    rospack find ur_robot_driver > /dev/null 2>&1 || echo "警告: UR机器人驱动未安装"
    
    echo "检查RealSense驱动..."
    rospack find realsense2_camera > /dev/null 2>&1 || echo "警告: RealSense驱动未安装"
fi

# 安装easy_handeye（手眼标定工具）
echo "安装easy_handeye（手眼标定工具）..."
if [ ! -z "$ROS_DISTRO" ]; then
    cd ~/catkin_ws/src 2>/dev/null || cd ~/connector_assembly_ws/src 2>/dev/null || echo "请创建工作空间"
    if [ -d "easy_handeye" ]; then
        echo "easy_handeye已存在"
    else
        git clone https://github.com/marcoesposito1988/easy_handeye.git
        cd ..
        catkin_make
        source devel/setup.bash
    fi
fi

echo "=== 环境配置完成 ==="
echo "下一步："
echo "1. 确保ROS环境已配置: source /opt/ros/noetic/setup.bash"
echo "2. 创建工作空间并编译: catkin_make"
echo "3. 运行系统标定: rosrun chapter5_system_integration hand_eye_calibration.py"
echo "4. 启动系统: roslaunch chapter5_system_integration system.launch"

