"""
GRRT-Connect (Guided RRT-Connect) 路径规划算法
改进的引导式RRT-Connect，适用于狭窄空间
"""

import numpy as np
from typing import List, Optional, Tuple, Dict
import random
import math


class Node:
    """RRT树节点"""
    def __init__(self, config: np.ndarray, parent: Optional['Node'] = None):
        self.config = config  # 配置空间中的点（关节角度）
        self.parent = parent
        self.cost = 0.0  # 从根节点到当前节点的代价


class GRRTConnect:
    """GRRT-Connect路径规划器"""
    
    def __init__(self,
                 obstacle_map,
                 goal_bias: float = 0.3,
                 step_size: float = 0.05,
                 max_iterations: int = 10000,
                 connection_threshold: float = 0.1):
        """
        初始化GRRT-Connect规划器
        
        Args:
            obstacle_map: 混合障碍物地图（AABB + Octomap）
            goal_bias: 目标偏置概率 P_goal
            step_size: 扩展步长 ε（弧度或米）
            max_iterations: 最大迭代次数
            connection_threshold: 两树连接阈值
        """
        self.obstacle_map = obstacle_map
        self.goal_bias = goal_bias
        self.step_size = step_size
        self.max_iterations = max_iterations
        self.connection_threshold = connection_threshold
        
        # 两棵搜索树
        self.tree_a = []  # 从起点生长
        self.tree_b = []  # 从终点生长
    
    def plan(self,
             start: np.ndarray,
             goal: np.ndarray,
             joint_limits: Optional[Dict] = None) -> Optional[List[np.ndarray]]:
        """
        规划路径
        
        Args:
            start: 起始配置（关节角度）
            goal: 目标配置（关节角度）
            joint_limits: 关节限位 {'lower': [...], 'upper': [...]}
        
        Returns:
            路径（配置序列），如果规划失败则返回None
        """
        # 初始化两棵树
        self.tree_a = [Node(start)]
        self.tree_b = [Node(goal)]
        
        # 检查起点和终点是否在自由空间
        if not self._is_free(start):
            print("警告: 起点在障碍物内")
            return None
        
        if not self._is_free(goal):
            print("警告: 终点在障碍物内")
            return None
        
        # 迭代扩展
        for iteration in range(self.max_iterations):
            # 随机选择一棵树进行扩展
            if random.random() < 0.5:
                # 扩展树A
                q_rand = self._sample(goal)  # 目标偏置采样
                q_new = self._extend(self.tree_a, q_rand, joint_limits)
                
                if q_new is not None:
                    # 尝试连接两棵树
                    if self._try_connect(self.tree_b, q_new.config, joint_limits):
                        # 找到路径
                        path_a = self._extract_path(self.tree_a, q_new)
                        path_b = self._extract_path(self.tree_b, self.tree_b[-1])
                        path_b.reverse()
                        return path_a + path_b[1:]  # 合并路径，去除重复点
            else:
                # 扩展树B
                q_rand = self._sample(start)  # 向起点采样
                q_new = self._extend(self.tree_b, q_rand, joint_limits)
                
                if q_new is not None:
                    # 尝试连接两棵树
                    if self._try_connect(self.tree_a, q_new.config, joint_limits):
                        # 找到路径
                        path_a = self._extract_path(self.tree_a, self.tree_a[-1])
                        path_b = self._extract_path(self.tree_b, q_new)
                        path_b.reverse()
                        return path_a + path_b[1:]
        
        # 规划失败
        return None
    
    def _sample(self, goal: np.ndarray) -> np.ndarray:
        """
        采样配置（目标偏置策略）
        
        q_rand = {
            q_goal,              with probability P_goal
            RandomSample(C_free), with probability 1-P_goal
        }
        """
        if random.random() < self.goal_bias:
            return goal.copy()
        else:
            # 随机采样（简化：在关节限位内均匀采样）
            # 实际应使用障碍物地图的C_free空间
            return self._random_sample()
    
    def _random_sample(self) -> np.ndarray:
        """随机采样配置"""
        # 简化实现：假设6自由度，每个关节在[-π, π]内
        # 实际应根据关节限位和障碍物地图采样
        return np.random.uniform(-np.pi, np.pi, 6)
    
    def _extend(self,
                tree: List[Node],
                q_rand: np.ndarray,
                joint_limits: Optional[Dict]) -> Optional[Node]:
        """
        扩展树
        
        q_new = q_near + ε * (q_rand - q_near) / ||q_rand - q_near||
        """
        # 找到最近的节点
        q_near = self._nearest(tree, q_rand)
        
        # 计算方向
        direction = q_rand - q_near.config
        dist = np.linalg.norm(direction)
        
        if dist < 1e-6:
            return None
        
        # 归一化方向
        direction = direction / dist
        
        # 扩展
        q_new_config = q_near.config + self.step_size * direction
        
        # 检查关节限位
        if joint_limits is not None:
            q_new_config = np.clip(
                q_new_config,
                joint_limits['lower'],
                joint_limits['upper']
            )
        
        # 检查是否在自由空间
        if not self._is_free(q_new_config):
            return None
        
        # 检查路径是否无碰撞
        if not self._is_path_free(q_near.config, q_new_config):
            return None
        
        # 创建新节点
        q_new = Node(q_new_config, parent=q_near)
        q_new.cost = q_near.cost + self.step_size
        tree.append(q_new)
        
        return q_new
    
    def _nearest(self, tree: List[Node], q: np.ndarray) -> Node:
        """找到树中距离q最近的节点"""
        min_dist = float('inf')
        nearest = tree[0]
        
        for node in tree:
            dist = np.linalg.norm(node.config - q)
            if dist < min_dist:
                min_dist = dist
                nearest = node
        
        return nearest
    
    def _try_connect(self,
                    tree: List[Node],
                    q_target: np.ndarray,
                    joint_limits: Optional[Dict]) -> bool:
        """
        尝试连接树到目标配置
        
        Args:
            tree: 目标树
            q_target: 目标配置
            joint_limits: 关节限位
        
        Returns:
            是否成功连接
        """
        q_near = self._nearest(tree, q_target)
        dist = np.linalg.norm(q_near.config - q_target)
        
        if dist < self.connection_threshold:
            # 直接连接
            if self._is_path_free(q_near.config, q_target):
                q_new = Node(q_target, parent=q_near)
                tree.append(q_new)
                return True
        
        return False
    
    def _is_free(self, config: np.ndarray) -> bool:
        """
        检查配置是否在自由空间
        
        Args:
            config: 配置（关节角度）
        
        Returns:
            是否自由
        """
        # 使用障碍物地图检查碰撞
        return self.obstacle_map.is_free(config)
    
    def _is_path_free(self, q1: np.ndarray, q2: np.ndarray) -> bool:
        """
        检查路径是否无碰撞
        
        Args:
            q1: 起点配置
            q2: 终点配置
        
        Returns:
            路径是否自由
        """
        # 在路径上采样多个点进行检查
        num_samples = max(10, int(np.linalg.norm(q2 - q1) / self.step_size * 2))
        
        for i in range(num_samples + 1):
            alpha = i / num_samples
            q_interp = (1 - alpha) * q1 + alpha * q2
            
            if not self._is_free(q_interp):
                return False
        
        return True
    
    def _extract_path(self, tree: List[Node], goal_node: Node) -> List[np.ndarray]:
        """从树中提取路径"""
        path = []
        node = goal_node
        
        while node is not None:
            path.append(node.config.copy())
            node = node.parent
        
        path.reverse()
        return path

