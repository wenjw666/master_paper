"""
Actor网络（策略网络）
输出动作分布的高斯参数
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple


class Actor(nn.Module):
    """Actor网络"""
    
    def __init__(self, state_dim: int, action_dim: int, action_range: tuple):
        """
        初始化Actor网络
        
        Args:
            state_dim: 状态维度
            action_dim: 动作维度
            action_range: 动作范围 (low, high)
        """
        super(Actor, self).__init__()
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.action_range = action_range
        self.action_low = torch.tensor(action_range[0], dtype=torch.float32)
        self.action_high = torch.tensor(action_range[1], dtype=torch.float32)
        
        # 网络结构：3层MLP，每层256个神经元
        self.fc1 = nn.Linear(state_dim, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 256)
        
        # 输出层：均值和标准差
        self.mean_layer = nn.Linear(256, action_dim)
        self.log_std_layer = nn.Linear(256, action_dim)
        
        # Layer Normalization（用于消除量纲差异）
        self.ln1 = nn.LayerNorm(256)
        self.ln2 = nn.LayerNorm(256)
        self.ln3 = nn.LayerNorm(256)
        
        # 初始化权重
        self._initialize_weights()
    
    def _initialize_weights(self):
        """初始化网络权重"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.orthogonal_(m.weight, gain=np.sqrt(2))
                nn.init.constant_(m.bias, 0.0)
    
    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        前向传播
        
        Args:
            state: 状态张量 (batch_size, state_dim)
        
        Returns:
            (action, log_prob) - 动作和其对数的概率
        """
        # 网络前向传播
        x = F.relu(self.ln1(self.fc1(state)))
        x = F.relu(self.ln2(self.fc2(x)))
        x = F.relu(self.ln3(self.fc3(x)))
        
        # 输出均值和标准差
        mean = self.mean_layer(x)
        log_std = self.log_std_layer(x)
        log_std = torch.clamp(log_std, -20, 2)  # 限制标准差范围
        std = torch.exp(log_std)
        
        # 采样动作（重参数化技巧）
        normal = torch.distributions.Normal(mean, std)
        x_t = normal.rsample()  # 可微分的采样
        
        # Tanh激活，将动作限制在[-1, 1]
        action = torch.tanh(x_t)
        
        # 计算log概率（考虑Tanh变换的雅可比）
        log_prob = normal.log_prob(x_t)
        log_prob -= torch.log(1 - action.pow(2) + 1e-6)
        log_prob = log_prob.sum(1, keepdim=True)
        
        # 将动作缩放到实际范围
        action = self._scale_action(action)
        
        return action, log_prob
    
    def sample(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        采样动作（用于训练）
        
        Args:
            state: 状态张量
        
        Returns:
            (action, log_prob)
        """
        return self.forward(state)
    
    def _scale_action(self, action: torch.Tensor) -> torch.Tensor:
        """
        将动作从[-1, 1]缩放到实际范围
        
        Args:
            action: 归一化动作 [-1, 1]
        
        Returns:
            缩放后的动作
        """
        # 线性缩放
        action_scaled = (action + 1.0) / 2.0  # [0, 1]
        action_scaled = action_scaled * (self.action_high - self.action_low) + self.action_low
        return action_scaled

