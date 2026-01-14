"""
直接运行图表生成（独立脚本）
"""

import os
import sys

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../'))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, '论文图片')

print("=" * 70)
print("论文图表生成脚本")
print("=" * 70)
print(f"脚本目录: {SCRIPT_DIR}")
print(f"项目根目录: {PROJECT_ROOT}")
print(f"输出目录: {OUTPUT_DIR}")
print("=" * 70)

# 创建输出目录
for chapter in ['第2章', '第3章', '第4章', '第5章']:
    chapter_path = os.path.join(OUTPUT_DIR, chapter)
    os.makedirs(chapter_path, exist_ok=True)
    print(f"✓ 目录已创建: {chapter_path}")

# 添加路径
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, '第2章内容与代码实现', 'chapter2_vision_perception', 'utils'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, '第3章内容与代码实现', 'chapter3_grasp_planning', 'utils'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, '第4章内容与代码实现', 'chapter4_assembly_control', 'training'))

# 检查依赖
print("\n检查依赖模块...")
try:
    import matplotlib
    print(f"✓ matplotlib {matplotlib.__version__}")
except ImportError:
    print("✗ matplotlib 未安装")
    sys.exit(1)

try:
    import numpy
    print(f"✓ numpy {numpy.__version__}")
except ImportError:
    print("✗ numpy 未安装")
    sys.exit(1)

try:
    import seaborn
    print(f"✓ seaborn")
except ImportError:
    print("⚠ seaborn 未安装（可选）")

# 导入自定义模块
print("\n导入自定义模块...")
try:
    from visualization import ExperimentVisualizer
    print("✓ ExperimentVisualizer")
except Exception as e:
    print(f"✗ ExperimentVisualizer: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from generate_realistic_data import RealisticDataGenerator
    print("✓ RealisticDataGenerator")
except Exception as e:
    print(f"✗ RealisticDataGenerator: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 初始化
print("\n初始化生成器...")
generator = RealisticDataGenerator(seed=42)
visualizer = ExperimentVisualizer(figsize=(12, 8), dpi=300)

# 生成图表
print("\n" + "=" * 70)
print("开始生成图表...")
print("=" * 70)

generated_files = []

# ========== 第2章 ==========
print("\n【第2章】")
try:
    from visualization import plot_pose_accuracy_curve
    pose_data = generator.generate_pose_accuracy_data()
    output_path = os.path.join(OUTPUT_DIR, '第2章', '图2-8_不同遮挡率下的ADD-S精度曲线对比图.png')
    plot_pose_accuracy_curve(
        pose_data['occlusion_rates'],
        pose_data['accuracies_2mm'],
        pose_data['accuracies_5mm'],
        pose_data['method_names'],
        output_path
    )
    generated_files.append(output_path)
    print(f"  ✅ 图2-8")
except Exception as e:
    print(f"  ❌ 图2-8: {e}")

# ========== 第3章 ==========
print("\n【第3章】")
try:
    # 重新导入（可能路径冲突）
    import importlib
    if 'visualization' in sys.modules:
        del sys.modules['visualization']
    sys.path.insert(0, os.path.join(PROJECT_ROOT, '第3章内容与代码实现', 'chapter3_grasp_planning', 'utils'))
    from visualization import plot_planning_comparison
    
    planning_data = generator.generate_planning_comparison_data()
    output_path = os.path.join(OUTPUT_DIR, '第3章', '图3-8_不同规划算法的耗时与路径长度对比箱线图.png')
    plot_planning_comparison(planning_data, output_path)
    generated_files.append(output_path)
    print(f"  ✅ 图3-8")
except Exception as e:
    print(f"  ❌ 图3-8: {e}")
    import traceback
    traceback.print_exc()

# ========== 第4章 ==========
print("\n【第4章】")

# 图4-6
try:
    training_data = generator.generate_training_curves_data()
    output_path = os.path.join(OUTPUT_DIR, '第4章', '图4-6_不同算法的平均奖励收敛曲线对比.png')
    visualizer.plot_training_curves(training_data, output_path)
    generated_files.append(output_path)
    print(f"  ✅ 图4-6")
except Exception as e:
    print(f"  ❌ 图4-6: {e}")
    import traceback
    traceback.print_exc()

# 图4-8
try:
    if 'visualization' in sys.modules:
        del sys.modules['visualization']
    sys.path.insert(0, os.path.join(PROJECT_ROOT, '第4章内容与代码实现', 'chapter4_assembly_control', 'training'))
    from visualization import plot_force_history
    
    force_history_data = generator.generate_force_history_data()
    output_path = os.path.join(OUTPUT_DIR, '第4章', '图4-8_装配全过程的接触力与力矩信号变化曲线.png')
    plot_force_history(
        force_history_data['force_history'],
        force_history_data['timestamps'],
        output_path
    )
    generated_files.append(output_path)
    print(f"  ✅ 图4-8")
except Exception as e:
    print(f"  ❌ 图4-8: {e}")
    import traceback
    traceback.print_exc()

# ========== 第5章 ==========
print("\n【第5章】")

# 图5-2
try:
    output_path = os.path.join(OUTPUT_DIR, '第5章', '图5-2_基于ROS的系统软件架构与数据流向图.png')
    visualizer.plot_system_architecture(output_path)
    generated_files.append(output_path)
    print(f"  ✅ 图5-2")
except Exception as e:
    print(f"  ❌ 图5-2: {e}")
    import traceback
    traceback.print_exc()

# 图5-4
try:
    force_data = generator.generate_force_curves_data()
    output_path = os.path.join(OUTPUT_DIR, '第5章', '图5-4_强线缆干扰下三种控制策略的装配力力矩曲线对比.png')
    visualizer.plot_force_curves_comparison(
        force_data['baseline1'],
        force_data['baseline2'],
        force_data['ours'],
        output_path
    )
    generated_files.append(output_path)
    print(f"  ✅ 图5-4")
except Exception as e:
    print(f"  ❌ 图5-4: {e}")
    import traceback
    traceback.print_exc()

# 图5-3
try:
    perception_data = generator.generate_perception_planning_data()
    output_path = os.path.join(OUTPUT_DIR, '第5章', '图5-3_不同遮挡工况下感知规划结果对比.png')
    visualizer.plot_perception_planning_results(perception_data, output_path)
    generated_files.append(output_path)
    print(f"  ✅ 图5-3")
except Exception as e:
    print(f"  ❌ 图5-3: {e}")
    import traceback
    traceback.print_exc()

# 表5-2
try:
    success_data = generator.generate_success_rate_data()
    output_path = os.path.join(OUTPUT_DIR, '第5章', '表5-2_力控策略消融实验统计结果可视化.png')
    visualizer.plot_success_rate_comparison(success_data, output_path)
    generated_files.append(output_path)
    print(f"  ✅ 表5-2")
except Exception as e:
    print(f"  ❌ 表5-2: {e}")
    import traceback
    traceback.print_exc()

# 状态机
try:
    output_path = os.path.join(OUTPUT_DIR, '第5章', '状态机流程图.png')
    visualizer.plot_state_machine_diagram(output_path)
    generated_files.append(output_path)
    print(f"  ✅ 状态机流程图")
except Exception as e:
    print(f"  ❌ 状态机流程图: {e}")
    import traceback
    traceback.print_exc()

# 总结
print("\n" + "=" * 70)
print("生成完成！")
print("=" * 70)
print(f"\n成功生成 {len(generated_files)} 个图表文件:")
for f in generated_files:
    if os.path.exists(f):
        size = os.path.getsize(f) / 1024
        rel_path = os.path.relpath(f, PROJECT_ROOT)
        print(f"  ✓ {rel_path} ({size:.1f} KB)")
    else:
        print(f"  ✗ {f} (文件不存在)")

print(f"\n所有文件保存在: {OUTPUT_DIR}")



