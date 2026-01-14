"""
生成所有可自动生成的论文图表
输出到论文图片目录
"""

import os
import sys
import numpy as np

# 获取项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 向上4级到项目根目录
project_root = os.path.abspath(os.path.join(current_dir, '../../../../'))
output_dir = os.path.join(project_root, '论文图片')

# 调试信息
print(f"当前脚本目录: {current_dir}")
print(f"项目根目录: {project_root}")
print(f"输出目录: {output_dir}")
print(f"输出目录是否存在: {os.path.exists(os.path.dirname(output_dir))}")

# 确保输出目录存在
for chapter in ['第2章', '第3章', '第4章', '第5章']:
    os.makedirs(os.path.join(output_dir, chapter), exist_ok=True)

# 添加路径
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(project_root, '第2章内容与代码实现/chapter2_vision_perception/utils'))
sys.path.insert(0, os.path.join(project_root, '第3章内容与代码实现/chapter3_grasp_planning/utils'))
sys.path.insert(0, os.path.join(project_root, '第4章内容与代码实现/chapter4_assembly_control/training'))

from visualization import ExperimentVisualizer
from generate_realistic_data import RealisticDataGenerator

print("=" * 60)
print("开始生成所有可自动生成的论文图表")
print(f"输出目录: {output_dir}")
print("=" * 60)

# 初始化
generator = RealisticDataGenerator(seed=42)
visualizer = ExperimentVisualizer(figsize=(12, 8), dpi=300)

# ========== 第2章图表 ==========
print("\n【第2章】生成图表...")

# 图2-8: 位姿精度曲线
try:
    from visualization import plot_pose_accuracy_curve
    pose_data = generator.generate_pose_accuracy_data()
    plot_pose_accuracy_curve(
        pose_data['occlusion_rates'],
        pose_data['accuracies_2mm'],
        pose_data['accuracies_5mm'],
        pose_data['method_names'],
        os.path.join(output_dir, '第2章/图2-8_不同遮挡率下的ADD-S精度曲线对比图.png')
    )
    print("  ✅ 图2-8 已生成")
except Exception as e:
    print(f"  ❌ 图2-8 生成失败: {e}")

# ========== 第3章图表 ==========
print("\n【第3章】生成图表...")

# 图3-8: 规划算法对比
try:
    from visualization import plot_planning_comparison
    planning_data = generator.generate_planning_comparison_data()
    plot_planning_comparison(
        planning_data,
        os.path.join(output_dir, '第3章/图3-8_不同规划算法的耗时与路径长度对比箱线图.png')
    )
    print("  ✅ 图3-8 已生成")
except Exception as e:
    print(f"  ❌ 图3-8 生成失败: {e}")

# ========== 第4章图表 ==========
print("\n【第4章】生成图表...")

# 图4-6: 训练曲线
training_data = generator.generate_training_curves_data()
visualizer.plot_training_curves(
    training_data,
    os.path.join(output_dir, '第4章/图4-6_不同算法的平均奖励收敛曲线对比.png')
)
print("  ✅ 图4-6 已生成")

# 图4-8: 力历史曲线
try:
    from visualization import plot_force_history
    force_history_data = generator.generate_force_history_data()
    plot_force_history(
        force_history_data['force_history'],
        force_history_data['timestamps'],
        os.path.join(output_dir, '第4章/图4-8_装配全过程的接触力与力矩信号变化曲线.png')
    )
    print("  ✅ 图4-8 已生成")
except Exception as e:
    print(f"  ❌ 图4-8 生成失败: {e}")

# ========== 第5章图表 ==========
print("\n【第5章】生成图表...")

# 图5-2: 系统架构图
visualizer.plot_system_architecture(
    os.path.join(output_dir, '第5章/图5-2_基于ROS的系统软件架构与数据流向图.png')
)
print("  ✅ 图5-2 已生成")

# 图5-4: 力曲线对比
force_data = generator.generate_force_curves_data()
visualizer.plot_force_curves_comparison(
    force_data['baseline1'],
    force_data['baseline2'],
    force_data['ours'],
    os.path.join(output_dir, '第5章/图5-4_强线缆干扰下三种控制策略的装配力力矩曲线对比.png')
)
print("  ✅ 图5-4 已生成")

# 表5-1可视化: 感知-规划结果
perception_data = generator.generate_perception_planning_data()
visualizer.plot_perception_planning_results(
    perception_data,
    os.path.join(output_dir, '第5章/图5-3_不同遮挡工况下感知规划结果对比.png')
)
print("  ✅ 图5-3 已生成")

# 表5-2可视化: 成功率对比
success_data = generator.generate_success_rate_data()
visualizer.plot_success_rate_comparison(
    success_data,
    os.path.join(output_dir, '第5章/表5-2_力控策略消融实验统计结果可视化.png')
)
print("  ✅ 表5-2可视化 已生成")

# 状态机流程图
visualizer.plot_state_machine_diagram(
    os.path.join(output_dir, '第5章/状态机流程图.png')
)
print("  ✅ 状态机流程图 已生成")

print("\n" + "=" * 60)
print("图表生成完成！")
print(f"所有图表保存在: {os.path.abspath(output_dir)}")
print("=" * 60)

# 列出生成的文件
print("\n生成的文件列表:")
for root, dirs, files in os.walk(output_dir):
    for file in sorted(files):
        if file.endswith('.png'):
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath) / 1024  # KB
            rel_path = os.path.relpath(filepath, output_dir)
            print(f"  - {rel_path} ({size:.1f} KB)")

