# EPnP + RANSAC 位姿解算模块

## 功能概述

本模块实现从2D关键点到6D位姿的解算，采用EPnP算法结合RANSAC外点剔除，抗线缆遮挡干扰。

## 开源库引用

### OpenCV (EPnP实现)
- **安装**: `pip install opencv-python opencv-contrib-python`
- **文档**: https://docs.opencv.org/
- **函数**: `cv2.solvePnP()` (flags=cv2.SOLVEPNP_EPNP)

### 独立EPnP实现（可选）
- **GitHub**: https://github.com/jessecw/EPnP
- **安装**:
  ```bash
  git clone https://github.com/jessecw/EPnP.git
  cd EPnP
  pip install -e .
  ```

## 目录结构

```
pose_estimation/
├── README.md                    # 本文件
├── epnp_solver.py              # EPnP算法实现
├── ransac_pnp.py               # RANSAC+PnP组合
├── refine_pose.py              # Levenberg-Marquardt优化
└── utils/
    ├── __init__.py
    └── projection_utils.py     # 投影与重投影误差计算
```

## 核心算法

### 1. 相机投影模型
对于3D点 $P_i^w = [X_i, Y_i, Z_i]^T$，投影到2D像素点 $p_i = [u_i, v_i]^T$：

$$s \begin{bmatrix} u_i \\ v_i \\ 1 \end{bmatrix} = K [R | t] \begin{bmatrix} X_i \\ Y_i \\ Z_i \\ 1 \end{bmatrix}$$

其中：
- $K$: 相机内参矩阵
- $R, t$: 待求解的旋转矩阵和平移向量

### 2. RANSAC外点剔除
算法流程：
1. 随机采样4个点（PnP最小解集）
2. 使用EPnP解算假设位姿
3. 计算所有点的重投影误差
4. 判定内点（误差 < 阈值，如3像素）
5. 迭代优化，选择内点最多的模型
6. 使用所有内点进行非线性优化

### 3. 重投影误差
$$e_i = || p_i - \pi(P_i^w, K, R, t) ||^2$$

## 使用方法

### 1. 准备3D模型关键点
从CAD模型获取关键点的3D坐标（物体坐标系）：
```python
# 3D关键点（物体坐标系，单位：mm）
model_points_3d = np.array([
    [0, 0, 0],      # 定位孔1
    [10, 0, 0],     # 定位孔2
    [5, 10, 0],     # 定位孔3
    [5, 5, -5],     # 线缆根部
], dtype=np.float32)
```

### 2. 位姿解算
```python
from ransac_pnp import RANSACPnPSolver

solver = RANSACPnPSolver(
    camera_matrix=K,  # 相机内参
    dist_coeffs=None,  # 畸变系数
    reprojection_threshold=3.0,  # RANSAC阈值（像素）
    max_iterations=1000
)

# 2D关键点（从DeepLabV3+获取）
image_points_2d = np.array([
    [320, 240],  # 定位孔1
    [330, 240],  # 定位孔2
    [325, 250],  # 定位孔3
    [325, 245],  # 线缆根部
], dtype=np.float32)

# 解算位姿
success, R, t, inliers = solver.solve(
    model_points_3d, 
    image_points_2d
)

if success:
    print(f"旋转矩阵 R:\n{R}")
    print(f"平移向量 t: {t}")
    print(f"内点数量: {len(inliers)}/{len(image_points_2d)}")
```

### 3. 位姿优化
```python
from refine_pose import refine_pose

# 使用LM算法进一步优化
R_refined, t_refined = refine_pose(
    model_points_3d[inliers],
    image_points_2d[inliers],
    K,
    R, t  # 初始估计
)
```

## 输出接口

### 到第3章（抓取规划）
- **6D位姿** (`pose_6d`): 
  ```python
  {
      'R': np.array(3x3),  # 旋转矩阵
      't': np.array(3,),   # 平移向量
      'quaternion': ...,   # 四元数表示（可选）
      'euler': ...         # 欧拉角表示（可选）
  }
  ```

## 评估指标

- **ADD-S误差**: Average Distance of Model Points
  - 阈值: 2mm (高精度), 5mm (抓取容许)
- **重投影误差**: 平均像素误差
- **内点率**: RANSAC内点占比

## 注意事项

1. **3D模型精度**: CAD模型的3D关键点坐标必须精确
2. **相机标定**: 内参矩阵K的精度直接影响位姿解算精度
3. **外点处理**: RANSAC阈值需根据关键点检测精度调整
4. **实时性**: 位姿解算需在10ms内完成

