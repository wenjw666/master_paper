# AI生成图表提示词

所有无法自动生成的图表提示词，直接复制到AI绘图工具使用。

---

## 第2章：基于深度学习的电连接器识别与位姿估计研究

### 图2-1：航空机舱内电连接器多实例堆叠与线缆遮挡典型场景

**提示词：**
```
Create a high-quality technical photograph-style image showing an aviation manufacturing scene. The image should depict:

1. Multiple electrical connectors (circular aviation connectors, D38999 series style) stacked closely together on a workbench
2. Black flexible cables (approximately 8mm diameter) hanging down and partially covering the connectors
3. Some cables crossing over connector surfaces, obscuring key features like positioning holes
4. Industrial aviation cabin environment with metallic walls in the background
5. Mixed lighting conditions with some areas having strong reflections and others in shadow
6. Professional technical photography style, high resolution, clear focus on the connectors and cable occlusion
7. Add subtle annotations showing connector positions and cable occlusion areas
8. Color scheme: metallic grays, blacks for cables, industrial environment tones
```

**关键元素：**
- 多个圆形航空电连接器紧密堆叠
- 黑色柔性线缆垂落并遮挡连接器
- 线缆横跨连接器表面，遮挡定位孔
- 工业机舱环境，金属壁面
- 混合光照条件（强反光+阴影）

---

### 图2-2：级联式视觉感知系统总体架构图

**提示词：**
```
Create a professional system architecture diagram showing a cascaded vision perception system. The diagram should include:

1. Three main stages arranged horizontally: "YOLOv8-seg Detection" → "DeepLabV3+ Keypoint Extraction" → "EPnP+RANSAC Pose Estimation"
2. Input: RGB-D camera images at the left
3. Output: 6D pose, cable mask, tag ID at the right
4. Data flow arrows showing: RGB image → YOLOv8-seg → ROI cropping → DeepLabV3+ → Keypoint heatmaps → EPnP solver → Final pose
5. Parallel branches: cable segmentation mask extraction
6. Professional technical diagram style, clean lines, labeled boxes, color-coded modules
7. Use blue for detection stage, green for feature extraction, orange for pose estimation
8. Include small icons or symbols for camera, neural networks, and coordinate systems
9. Chinese and English labels acceptable
10. Academic paper style, high contrast, suitable for printing
```

**关键元素：**
- 三级级联架构：检测→特征提取→位姿解算
- 数据流向清晰标注
- 模块化设计，颜色区分
- 学术论文风格

---

### 图2-3：包含真实采集与仿真合成的混合数据集样本示例

**提示词：**
```
Create a side-by-side comparison image showing dataset samples. Left side: real captured images, Right side: Blender synthetic images.

Left side (Real images):
- High-quality photographs of electrical connectors in real industrial environment
- Natural lighting, some shadows and reflections
- Realistic cable occlusion patterns
- 3-4 sample images arranged vertically

Right side (Synthetic images):
- Computer-generated 3D rendered images of the same connectors
- Blender-style rendering with perfect lighting
- Simulated cable positions
- Matching number of samples as left side

Style: Professional technical documentation, grid layout, labeled "Real Data" and "Synthetic Data", high resolution, clear separation between left and right sections
```

**关键元素：**
- 左右对比：真实图像 vs Blender合成图像
- 3-4组样本对比
- 清晰标注"真实数据"和"合成数据"

---

### 图2-4：数据增强前后的类别分布平衡性分析图

**提示词：**
```
Create a bar chart or pie chart comparison showing class distribution before and after data augmentation.

Before augmentation:
- Uneven distribution with some connector ID classes having many samples and others having few
- Show 5-6 different connector classes (labeled as ID A, B, C, D, E, F)
- Some classes with 200+ samples, others with only 50-100 samples

After augmentation:
- More balanced distribution across all classes
- All classes now have similar sample counts (around 200-250)
- Same 5-6 classes

Style: Professional academic chart, two subplots side by side, labeled "Before Augmentation" and "After Augmentation", use different colors for each class, include legend, high resolution suitable for academic paper
```

**关键元素：**
- 前后对比柱状图或饼图
- 显示类别不平衡→平衡的变化
- 5-6个连接器ID类别

---

### 图2-5：YOLOv8-seg 网络结构图及 C2f 模块细节

**提示词：**
```
Create a detailed neural network architecture diagram for YOLOv8-seg:

Main architecture:
1. Input layer (640x640 RGB image)
2. Backbone: CSPDarknet53 with C2f modules
3. Neck: Feature Pyramid Network (FPN) + Path Aggregation Network (PAN)
4. Head: Three parallel branches - Detection head, Segmentation head, Classification head
5. Output: Bounding boxes, masks, class predictions

C2f module detail (inset or separate diagram):
- Show cross-stage partial connections
- Two convolution blocks with skip connections
- Input feature map → Split → Conv blocks → Concatenate → Output
- Label key components: C2f module, skip connections, feature fusion

Style: Professional deep learning architecture diagram, use standard neural network visualization conventions, color-code different types of layers (conv=blue, activation=green, pooling=orange), include layer dimensions, clean and readable, suitable for academic paper
```

**关键元素：**
- YOLOv8-seg完整网络架构
- C2f模块详细结构（可插入放大图）
- 三个输出分支：检测、分割、分类
- 标准深度学习架构图风格

---

### 图2-5：DeepLabV3+ 编码器-解码器架构及改进的输出头设计

**提示词：**
```
Create a detailed neural network architecture diagram for DeepLabV3+ with custom output heads:

Main architecture:
1. Encoder: ResNet backbone (show as ResNet-101 blocks)
2. ASPP module (Atrous Spatial Pyramid Pooling): Show parallel atrous convolutions with rates 6, 12, 18, and image pooling
3. Decoder: Upsampling and feature fusion
4. Custom dual output heads:
   - Branch 1: Keypoint detection head → Gaussian heatmaps (4 channels: 3 positioning holes + 1 cable root)
   - Branch 2: Cable segmentation head → Binary mask (1 channel)

Key features to highlight:
- ASPP module with different dilation rates
- Skip connections from encoder to decoder
- Parallel output branches
- Input: ROI cropped image from YOLOv8-seg
- Output: Heatmaps + Cable mask

Style: Professional deep learning diagram, use color coding (encoder=blue, ASPP=purple, decoder=green, output heads=orange), show feature map dimensions, clean academic style
```

**关键元素：**
- ResNet编码器 + ASPP模块 + 解码器
- 双输出头：关键点热力图 + 线缆分割掩膜
- ASPP模块的并行空洞卷积结构
- 跳跃连接

---

### 图2-6：线缆遮挡下的关键点高斯热力图预测结果

**提示词：**
```
Create a three-column visualization showing keypoint heatmap prediction results under cable occlusion:

Column 1 (Input):
- RGB image of an electrical connector
- Black cable partially covering the connector, especially covering one positioning hole in the upper right
- Clear view of other positioning holes

Column 2 (Predicted Heatmaps):
- Four Gaussian heatmap visualizations (one for each keypoint)
- Each heatmap shows a bright peak (red/yellow) at the predicted keypoint location
- Even the occluded positioning hole shows a peak in the correct location (demonstrating context-aware prediction)
- Use jet colormap (blue=cold, red=hot)

Column 3 (Cable Segmentation):
- Binary mask showing the cable region in white/red
- Accurate extraction of the cable shape
- Overlaid on the original image for reference

Style: Professional technical visualization, three equal-width columns, labeled clearly, high resolution, use scientific colormaps, show the robustness of the method despite occlusion
```

**关键元素：**
- 三列布局：输入图像、预测热力图、线缆分割
- 即使被遮挡的关键点也能正确预测
- 高斯热力图使用jet配色

---

### 图2-7：EPnP+RANSAC 位姿解算流程图

**提示词：**
```
Create a flowchart diagram showing the EPnP+RANSAC pose estimation algorithm:

Flowchart steps:
1. Start: Input keypoint detections (4+ points)
2. RANSAC Loop:
   - Randomly sample 4 points (minimum set for PnP)
   - Solve EPnP to get hypothesis pose (R, t)
   - Project all 3D model points using hypothesis pose
   - Calculate reprojection errors
   - Count inliers (errors < threshold, e.g., 3 pixels)
   - Keep best hypothesis (most inliers)
3. Refinement: Use all inliers for nonlinear optimization (Levenberg-Marquardt)
4. Output: Final refined pose (R, t)

Visual elements:
- Show example: First iteration with outlier (dashed box, wrong pose)
- Show final iteration with inliers only (solid box, correct pose)
- Include small diagrams showing: 3D model points, 2D image points, projection lines
- Use decision diamonds for "inlier check"
- Color code: outliers=red, inliers=green, hypothesis=blue

Style: Professional algorithm flowchart, use standard flowchart symbols, clear arrows, labeled steps, academic paper style
```

**关键元素：**
- RANSAC迭代流程
- 外点剔除过程
- EPnP求解 + 非线性优化
- 示例：第一次迭代（错误）vs 最终迭代（正确）

---

## 第3章：电连接器自主抓取方法研究

### 图3-1：狭窄机舱环境下机械臂抓取路径规划的约束条件与挑战示意图

**提示词：**
```
Create a 3D technical illustration showing a narrow aviation cabin environment with robot arm grasp planning constraints:

Scene elements:
1. UR5 robot arm (6-DOF, shown in blue/gray) at initial position (green highlight)
2. Target electrical connector (yellow highlight) at goal position
3. Rigid cabin walls (blue boxes/AABB representation) creating narrow passages
4. Flexible cables (red curves, shown as point clouds or octree voxels) hanging down and creating obstacles
5. Narrow workspace with limited clearance

Key visualizations:
- Show the challenge: narrow space between walls
- Highlight cable obstacles in red
- Show potential collision zones
- Include coordinate frame (base frame, end-effector frame)
- Add annotations: "Narrow Space", "Cable Obstacles", "Goal Position"

Style: 3D technical illustration, isometric or perspective view, use color coding (robot=blue, walls=gray, cables=red, goal=yellow), professional engineering drawing style, clear labels, suitable for academic paper
```

**关键元素：**
- 3D场景：UR5机械臂、狭窄空间、舱壁、线缆障碍
- 标注：起始位置、目标位置、障碍物
- 工程制图风格

---

### 图3-2：端到端 6D 抓取生成网络架构图

**提示词：**
```
Create a neural network architecture diagram for end-to-end 6D grasp generation (Contact-GraspNet style):

Architecture:
1. Input: Point cloud (N points, XYZ + RGB)
2. Backbone: PointNet++ feature extraction
   - Set abstraction layers
   - Feature propagation layers
3. Decoder: Per-point prediction
4. Three parallel output branches:
   - Confidence branch: Binary classification (grasp success probability)
   - Pose branch: 6D pose prediction (translation t + rotation R)
   - Width branch: Gripper opening width regression

Key features:
- Show point cloud input visualization
- PointNet++ hierarchical feature extraction
- Per-point predictions (each point predicts a grasp)
- Output: Multiple candidate grasps with confidence scores

Style: Professional deep learning architecture diagram, show point cloud as 3D scatter, use standard NN visualization, color-code branches, include dimensions, academic paper style
```

**关键元素：**
- PointNet++骨干网络
- 三个并行输出分支：置信度、位姿、宽度
- 点云输入可视化
- 端到端架构

---

### 图3-3：电连接器表面的候选抓取位姿分布可视化

**提示词：**
```
Create a 3D point cloud visualization showing candidate grasp poses on an electrical connector surface:

Visualization elements:
1. Point cloud of the electrical connector (gray/white points)
2. Multiple candidate grasp poses (top 10-20 shown):
   - Each grasp shown as a green arrow
   - Arrow direction = approach direction (gripper Z-axis)
   - Arrow length = confidence score (longer = higher confidence)
   - Color intensity = confidence (bright green = high, dark green = low)
3. Connector geometry clearly visible
4. High-confidence grasps clustered on stable regions (side walls)
5. Low-confidence grasps near cable root or unstable areas

View: Isometric 3D view, clear depth perception, professional technical visualization
Style: Scientific 3D plot style, use colormap for confidence, include colorbar, high resolution, suitable for academic paper
```

**关键元素：**
- 3D点云 + 抓取位姿箭头
- 颜色表示置信度
- 高置信度抓取集中在稳定区域
- 科学可视化风格

---

### 图3-4：基于多约束优化的最优抓取点筛选流程图

**提示词：**
```
Create a flowchart showing the multi-constraint grasp selection process:

Flowchart:
1. Input: 100 candidate grasp poses from network
2. Constraint 1 - Kinematic Feasibility:
   - IK solver check
   - Filter: 100 → 65 (remove infeasible)
3. Constraint 2 - Collision Avoidance:
   - Check against cable point cloud (from Ch2)
   - Filter: 65 → 42 (remove colliding)
4. Constraint 3 - Task Compatibility:
   - Alignment score with assembly direction
   - Filter: 42 → 1 (select best)
5. Output: Optimal grasp pose (highlighted in red)

Visual elements:
- Show filtering process with numbers
- Highlight the final selected grasp in red
- Include small icons: IK solver, collision detection, alignment check
- Show cable point cloud in background

Style: Professional flowchart, use standard symbols, color-code filters (green=pass, red=reject), clear progression, academic style
```

**关键元素：**
- 三级筛选流程
- 数量变化：100→65→42→1
- 最终选中的抓取位姿高亮
- 流程图风格

---

### 图3-5：GRRT-Connect 算法在狭窄通道内的搜索树扩展过程示意图

**提示词：**
```
Create a side-by-side comparison showing RRT-Connect vs GRRT-Connect search tree expansion:

Left side (Standard RRT-Connect):
- Search tree shown as green lines (nodes and edges)
- Many red nodes indicating collisions with obstacles
- Tree grows randomly, many wasted expansions
- Narrow passage with obstacles (blue walls, red cables)
- Tree struggles to find path through narrow space

Right side (GRRT-Connect):
- Search tree shown as green lines
- Fewer red collision nodes
- Tree grows more efficiently toward goal (goal-biased sampling)
- Same narrow passage
- Clear path found (highlighted in bright green/thick line)
- Goal position reached successfully

Key differences to highlight:
- Goal-biased sampling strategy
- More efficient tree growth
- Successful path planning

Style: 2D top-down view, technical diagram, use color coding (tree=green, collisions=red, obstacles=blue/gray, final path=thick green), clear labels, academic paper style
```

**关键元素：**
- 左右对比：标准RRT vs GRRT-Connect
- 搜索树可视化
- 碰撞节点（红色）vs 成功路径（绿色）
- 目标偏置采样效果

---

### 图3-6：避开柔性线缆障碍物的规划路径与传统 RRT 路径对比

**提示词：**
```
Create a 3D path visualization comparing traditional RRT vs GRRT-Connect paths:

Scene:
- 3D workspace with rigid walls (gray boxes)
- Flexible cables shown as red point cloud or octree voxels
- Start position (green sphere)
- Goal position (yellow sphere)

Two paths:
1. Traditional RRT path (blue dashed line):
   - Path intersects with cable obstacles
   - Shows collision points (red X marks)
   - Path is longer and unsafe

2. GRRT-Connect path (red solid line):
   - Path clearly avoids all cable obstacles
   - Smooth detour around cables
   - Shorter and collision-free
   - Uses Octomap for precise cable modeling

Visual elements:
- Show cable obstacles in red (Octomap representation)
- Highlight collision points on traditional path
- Show safe clearance on GRRT-Connect path
- Include coordinate frame

Style: 3D technical visualization, isometric view, professional engineering style, clear path comparison, suitable for academic paper
```

**关键元素：**
- 3D路径对比
- 传统RRT路径与线缆碰撞
- GRRT-Connect路径成功避障
- Octomap线缆表示

---

### 图3-7：自主抓取实验现场序列图（接近-抓取-提升）

**提示词：**
```
Create a sequence of 4-6 high-quality technical photographs showing the autonomous grasping process:

Sequence:
1. Approach: Robot arm moving toward the connector, end-effector open
2. Pre-grasp: Robot arm positioned near connector, aligning with grasp pose
3. Contact: Gripper fingers making contact with connector
4. Grasp: Gripper closed, connector securely held
5. Lift: Robot arm lifting the connector upward
6. (Optional) Transport: Moving connector to next position

Requirements:
- Consistent camera angle across all frames
- High resolution, professional technical photography
- Clear view of robot arm, gripper, and connector
- Industrial environment background
- Show cable attached to connector
- Professional lighting, no harsh shadows
- Frame numbers or time stamps
- Label each frame: "Approach", "Grasp", "Lift", etc.

Style: Technical documentation photography, grid layout (2x3 or 3x2), consistent framing, professional industrial photography style
```

**关键元素：**
- 4-6张关键帧序列
- 固定视角，一致性
- 标注每帧动作
- 工业摄影风格

---

## 第4章：基于深度强化学习的电连接器装配方法研究

### 图4-1：电连接器装配过程中的刚柔耦合受力分析与控制策略总览图

**提示词：**
```
Create a technical diagram showing rigid-flexible coupling force analysis during connector assembly:

Main elements:
1. Three assembly stages labeled:
   - Stage I: Approach (0-2s)
   - Stage II: Contact/Hole Searching (2-4.5s)
   - Stage III: Insertion (4.5-8s)

2. Force analysis:
   - Rigid contact force F_rigid (blue arrow) from pin-socket contact
   - Flexible interference force F_cable (red arrow) from cable deformation
   - Resultant force (combined vector)

3. Control strategy:
   - DRL policy output: pose correction Δx
   - Force-position hybrid controller
   - Visual feedforward compensation (using cable vector from Ch2)

4. Visual elements:
   - Connector with cable attached
   - Socket/receptacle
   - Force vectors with labels
   - Control system block diagram overlay

Style: Professional technical diagram, use color coding (rigid force=blue, flexible force=red, control=green), include force vector diagrams, clear stage labels, academic engineering style
```

**关键元素：**
- 三个阶段：接近、接触/搜孔、插入
- 刚柔耦合力分析
- 控制策略框图
- 力向量标注

---

### 图4-2：基于视觉前馈补偿的力位混合控制系统框图

**提示词：**
```
Create a control system block diagram showing force-position hybrid control with visual feedforward:

System components:
1. Inputs:
   - Desired trajectory x_d
   - Cable vector v_cable (from Ch2 vision)
   - Measured force F_measured (from F/T sensor)

2. Control blocks:
   - Outer loop: DRL policy (SAC) → pose correction Δx
   - Feedforward block: Cable force estimation F_cable_hat = k * v_cable
   - Impedance controller: M, B, K parameters
   - Inner loop: Torque controller

3. Signal flow:
   - x_d + Δx → Impedance controller
   - F_measured → Impedance controller
   - F_cable_hat → Feedforward compensation
   - Combined → Torque output → Robot

4. Visual elements:
   - Clear signal flow arrows
   - Block labels in Chinese/English
   - Color coding: vision input=blue, force input=red, control=green

Style: Professional control system diagram, use standard control block diagram symbols, clear signal flow, labeled blocks, academic paper style
```

**关键元素：**
- 控制系统框图
- 视觉前馈通道
- 阻抗控制内环
- 信号流向清晰

---

### 图4-3：强化学习环境交互流程与奖励函数曲线示意图

**提示词：**
```
Create a two-part diagram:

Part 1 (Left/Top): RL Environment Interaction Flow
- Agent (SAC policy) → Action a_t
- Environment (PyBullet simulation) → State s_t, Reward r_t
- State space components: pose error, velocity, force, cable vector
- Action space: 6DOF pose increment
- Reward function components shown as blocks

Part 2 (Right/Bottom): Reward Function Curves
- Plot showing reward components over time:
  - Distance reward (decreasing as approaching goal)
  - Force safety reward (penalty for high forces)
  - Completion reward (sparse, large spike at success)
- X-axis: Time steps or episodes
- Y-axis: Reward value
- Multiple curves with different colors

Style: Professional technical diagram, two subplots, clear flow diagram, scientific plotting style, labeled axes, academic paper format
```

**关键元素：**
- 交互流程图
- 奖励函数曲线
- 状态/动作空间标注
- 科学绘图风格

---

### 图4-4：基于 SAC 的 Actor-Critic 网络详细架构图

**提示词：**
```
Create a detailed neural network architecture diagram for SAC (Soft Actor-Critic):

Main components:
1. Actor Network (Policy Network):
   - Input: 18-dim state vector
   - Hidden layers: 3 FC layers [256, 256, 256] with ReLU
   - Output: Gaussian parameters (mean μ, std σ)
   - Action sampling: Reparameterization trick

2. Critic Networks (Dual Q-networks):
   - Q1 and Q2 networks (identical structure)
   - Input: State (18-dim) + Action (6-dim) concatenated
   - Hidden layers: 3 FC layers [256, 256, 256] with ReLU
   - Output: Q-value (scalar)
   - Target Q: min(Q1, Q2) for conservative estimation

3. Key features:
   - Layer Normalization on input
   - Tanh activation on output (action bounds)
   - Show entropy term in loss function
   - Temperature parameter α

Style: Professional deep learning architecture diagram, show both networks side by side, use standard NN visualization, color-code (Actor=blue, Critic=green), include layer dimensions, academic style
```

**关键元素：**
- Actor网络：状态→动作分布
- 双Critic网络：Q1和Q2
- 网络结构细节（层数、神经元数）
- 熵正则化项

---

### 图4-5：PyBullet 仿真训练环境与线缆动态模型可视化

**提示词：**
```
Create a screenshot-style visualization of PyBullet simulation environment:

Scene elements:
1. UR5 robot arm (gray/blue) in simulation
2. Electrical connector (yellow/gray) held by gripper
3. Flexible cable model:
   - Shown as linked rigid segments (discrete approximation)
   - Cable hanging down from connector
   - Realistic physics-based deformation
4. Socket/receptacle (gray) for assembly target
5. Simulation environment:
   - Ground plane
   - Lighting from simulation
   - Physics visualization (if applicable)

Key features:
- Realistic PyBullet rendering style
- Show cable as segmented model (not smooth curve)
- Robot in mid-assembly pose
- Clear view of cable dynamics

Style: Simulation screenshot, professional technical visualization, PyBullet rendering style, high resolution, suitable for academic paper
```

**关键元素：**
- PyBullet仿真环境
- 分段线缆模型
- 机器人装配姿态
- 物理仿真渲染

---

### 图4-7：真实环境下的电连接器柔顺装配过程序列图

**提示词：**
```
Create a sequence of 4-6 high-quality technical photographs showing the compliant assembly process:

Sequence:
1. Pre-assembly: Robot arm approaching socket with connector
2. Contact: Pin making initial contact with socket surface
3. Hole searching: DRL policy adjusting pose to find hole
4. Alignment: Pin aligned with hole, slight insertion
5. Insertion: Pin sliding into hole smoothly
6. Complete: Full insertion, connector locked

Requirements:
- Consistent camera angle (side view or isometric)
- High resolution, professional technical photography
- Clear view of connector, socket, and cable
- Show force sensor if visible
- Professional lighting
- Frame labels: "Contact", "Searching", "Insertion", etc.
- Show smooth, compliant motion (no rigid collision)

Style: Technical documentation photography, grid layout, consistent framing, professional industrial photography, show the compliant nature of the assembly
```

**关键元素：**
- 4-6张关键帧序列
- 柔顺装配过程
- 固定视角
- 工业摄影风格

---

## 第5章：电连接器机器人自主装配系统集成与综合实验研究

### 图5-1：面向航空制造的电连接器自主装配实验平台硬件集成图

**提示词：**
```
Create a high-quality technical photograph showing the complete experimental platform:

Hardware components to include:
1. UR5e 6-DOF collaborative robot arm (prominent, in center)
2. Robotiq 2F-85 gripper with custom TPU fingertips
3. Intel RealSense D435i camera mounted on end-effector (eye-in-hand)
4. ATI Gamma 6-DOF force/torque sensor between flange and gripper
5. Experimental frame/workbench (600x600x500mm aluminum frame)
6. Three electrical connectors with 1.5m cables
7. Simulated cabin walls inside frame
8. Industrial computer/workstation (optional, in background)

Annotations:
- Label each major component
- Show coordinate frames if applicable
- Professional technical photography
- High resolution, clear focus
- Industrial environment lighting
- Show cable routing and connector positions

Style: Professional technical documentation photography, isometric or front view, labeled diagram style, high resolution, suitable for academic paper cover or introduction
```

**关键元素：**
- 完整实验平台
- 所有硬件组件清晰可见
- 专业标注
- 工业摄影风格

---

### 图5-3：不同遮挡工况下 Octomap 构建与避障路径规划可视化对比

**提示词：**
```
Create a comparison visualization showing Octomap construction and path planning under different occlusion conditions:

Three scenarios (arranged horizontally or vertically):
1. Light occlusion (<10%): Cable naturally hanging, minimal occlusion
2. Medium occlusion (30%): Cable crossing connector, partial feature occlusion
3. Heavy occlusion (>50%): Cable wrapped around connector, severe occlusion

For each scenario show:
- Left: RGB image with cable occlusion
- Middle: Octomap visualization (3D voxel grid, red voxels = cable obstacles)
- Right: Planned path (green line) successfully avoiding cable obstacles

Key features:
- Octomap shown as 3D voxel representation
- Path clearly detours around cable obstacles
- Baseline method path (blue, colliding) vs Ours method path (green, safe)
- Show "circumvention" trajectory clearly

Style: Professional technical visualization, three-column or three-row layout, use scientific colormaps, clear comparison, academic paper style
```

**关键元素：**
- 三种遮挡工况对比
- Octomap体素可视化
- 路径规划对比（Baseline碰撞 vs Ours避障）
- 清晰展示绕行轨迹

---

### 图5-5：全流程自主装配实验的关键帧序列图

**提示词：**
```
Create a sequence of 6-8 high-quality technical photographs showing the complete autonomous assembly workflow:

Sequence:
1. Global perception: Camera viewing multiple connectors, system identifying target
2. Approach planning: Robot arm starting to move toward target
3. Grasp execution: Gripper closing on target connector
4. Lift and transport: Robot lifting connector and moving to assembly area
5. Pre-assembly: Positioning connector near socket
6. Assembly start: Initial contact with socket
7. Insertion: Pin entering hole
8. Complete: Connector fully inserted and locked

Requirements:
- Consistent camera angle across all frames
- High resolution, professional technical photography
- Show complete workflow from perception to assembly
- Clear view of robot, connector, cable, and socket
- Professional lighting
- Frame numbers and labels
- Grid layout (2x4 or 3x3)

Style: Technical documentation photography, consistent framing, professional industrial photography, show the autonomous nature of the complete system
```

**关键元素：**
- 6-8张完整流程关键帧
- 从感知到装配的全流程
- 固定视角
- 工业摄影风格

---

## 表格提示词

### 表4-1：不同方法的成功率统计

**提示词：**
```
Create a professional academic table with the following structure:

| Method | Success Count | Avg Time (s) | Max Contact Force (N) | Failure Cause |
|--------|---------------|--------------|----------------------|---------------|
| Pure Position Control | 12/50 | - | >30 (emergency stop) | Rigid jamming |
| Traditional Impedance Control | 34/50 | 15.4 | 12.5 | Cable pull-off misalignment |
| **Our Method (SAC+Feedforward)** | **48/50** | **8.2** | **6.8** | Extreme cable entanglement |

Style: Professional academic table, clear borders, bold header row, highlight best results, use LaTeX table style or Word table format, suitable for academic paper
```

---

### 表5-3：综合性能统计表

**提示词：**
```
Create a professional academic comparison table:

| Evaluation Metric | Manual Assembly (Skilled Worker) | Traditional Visual Servo | **Our Autonomous System** |
|-------------------|----------------------------------|--------------------------|---------------------------|
| **Single Cycle Time (s)** | **15.5** | 45.5 | **22.8** |
| **Force Consistency (Force Peak Variance, N²)** | 2.5 | 15.8 | **0.4** |
| **Success Rate under Cable Interference (%)** | 98% | 30% | **96.7%** |
| **Manual Intervention Count** | 0 | 21 | **1** |

Style: Professional academic table, three-way comparison, bold best results, clear metrics, LaTeX or Word format, suitable for academic paper
```

---

## 使用方法

1. 复制对应图表的提示词
2. 粘贴到AI绘图工具（Midjourney、DALL-E等）
3. 根据结果调整提示词
4. 保存到对应章节目录

