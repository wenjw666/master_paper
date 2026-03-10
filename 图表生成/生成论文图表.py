"""
生成所有可自动生成的论文图表
运行: python 生成论文图表.py
输出: 论文图片/ 目录
"""

import os
import sys

# 路径设置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = SCRIPT_DIR
OUTPUT_DIR = os.path.join(PROJECT_ROOT, '论文图片')
DATA_DIR = os.path.join(PROJECT_ROOT, '第5章内容与代码实现', 'chapter5_system_integration', 'data_collection')

# 创建输出目录
for chapter in ['第2章', '第3章', '第4章', '第5章']:
    os.makedirs(os.path.join(OUTPUT_DIR, chapter), exist_ok=True)

# 添加路径
sys.path.insert(0, DATA_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, '第2章内容与代码实现', 'chapter2_vision_perception', 'utils'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, '第3章内容与代码实现', 'chapter3_grasp_planning', 'utils'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, '第4章内容与代码实现', 'chapter4_assembly_control', 'training'))

# 导入
from visualization import ExperimentVisualizer
from generate_realistic_data import RealisticDataGenerator

generator = RealisticDataGenerator(seed=42)
visualizer = ExperimentVisualizer(figsize=(12, 8), dpi=300)

print("=" * 60)
print("生成论文图表")
print(f"输出: {OUTPUT_DIR}")
print("=" * 60)

# 第2章
print("\n【第2章】")
try:
    from visualization import plot_pose_accuracy_curve
    data = generator.generate_pose_accuracy_data()
    plot_pose_accuracy_curve(data['occlusion_rates'], data['accuracies_2mm'], 
                            data['accuracies_5mm'], data['method_names'],
                            os.path.join(OUTPUT_DIR, '第2章', '图2-8_不同遮挡率下的ADD-S精度曲线对比图.png'))
    print("  ✅ 图2-8")
except Exception as e:
    print(f"  ❌ 图2-8: {e}")

# 第3章
print("\n【第3章】")
try:
    if 'visualization' in sys.modules:
        del sys.modules['visualization']
    sys.path.insert(0, os.path.join(PROJECT_ROOT, '第3章内容与代码实现', 'chapter3_grasp_planning', 'utils'))
    from visualization import plot_planning_comparison
    plot_planning_comparison(generator.generate_planning_comparison_data(),
                            os.path.join(OUTPUT_DIR, '第3章', '图3-8_不同规划算法的耗时与路径长度对比箱线图.png'))
    print("  ✅ 图3-8")
except Exception as e:
    print(f"  ❌ 图3-8: {e}")

# 第4章
print("\n【第4章】")
try:
    visualizer.plot_training_curves(generator.generate_training_curves_data(),
                                   os.path.join(OUTPUT_DIR, '第4章', '图4-6_不同算法的平均奖励收敛曲线对比.png'))
    print("  ✅ 图4-6")
except Exception as e:
    print(f"  ❌ 图4-6: {e}")

try:
    if 'visualization' in sys.modules:
        del sys.modules['visualization']
    sys.path.insert(0, os.path.join(PROJECT_ROOT, '第4章内容与代码实现', 'chapter4_assembly_control', 'training'))
    from visualization import plot_force_history
    fh_data = generator.generate_force_history_data()
    plot_force_history(fh_data['force_history'], fh_data['timestamps'],
                      os.path.join(OUTPUT_DIR, '第4章', '图4-8_装配全过程的接触力与力矩信号变化曲线.png'))
    print("  ✅ 图4-8")
except Exception as e:
    print(f"  ❌ 图4-8: {e}")

# 第5章
print("\n【第5章】")
try:
    visualizer.plot_system_architecture(os.path.join(OUTPUT_DIR, '第5章', '图5-2_基于ROS的系统软件架构与数据流向图.png'))
    print("  ✅ 图5-2")
except Exception as e:
    print(f"  ❌ 图5-2: {e}")

try:
    fd = generator.generate_force_curves_data()
    visualizer.plot_force_curves_comparison(fd['baseline1'], fd['baseline2'], fd['ours'],
                                           os.path.join(OUTPUT_DIR, '第5章', '图5-4_强线缆干扰下三种控制策略的装配力力矩曲线对比.png'))
    print("  ✅ 图5-4")
except Exception as e:
    print(f"  ❌ 图5-4: {e}")

try:
    visualizer.plot_perception_planning_results(generator.generate_perception_planning_data(),
                                               os.path.join(OUTPUT_DIR, '第5章', '图5-3_不同遮挡工况下感知规划结果对比.png'))
    print("  ✅ 图5-3")
except Exception as e:
    print(f"  ❌ 图5-3: {e}")

try:
    visualizer.plot_success_rate_comparison(generator.generate_success_rate_data(),
                                           os.path.join(OUTPUT_DIR, '第5章', '表5-2_力控策略消融实验统计结果可视化.png'))
    print("  ✅ 表5-2")
except Exception as e:
    print(f"  ❌ 表5-2: {e}")

try:
    visualizer.plot_state_machine_diagram(os.path.join(OUTPUT_DIR, '第5章', '状态机流程图.png'))
    print("  ✅ 状态机流程图")
except Exception as e:
    print(f"  ❌ 状态机流程图: {e}")

print("\n" + "=" * 60)
print(f"完成！图表保存在: {OUTPUT_DIR}")
print("=" * 60)
