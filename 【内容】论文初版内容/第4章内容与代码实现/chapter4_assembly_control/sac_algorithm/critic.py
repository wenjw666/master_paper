"""
Critic网络（价值网络）
双Q网络，缓解过估计问题
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple


class Critic(nn.Module):
    """Critic网络（双Q网络）"""
    
    def __init__(self, state_dim: int, action_dim: int):
        """
        初始化Critic网络
        
        Args:
            state_dim: 状态维度
            action_dim: 动作维度
        """
        super(Critic, self).__init__()
        
        # Q1网络
        self.q1_fc1 = nn.Linear(state_dim + action_dim, 256)
        self.q1_fc2 = nn.Linear(256, 256)
        self.q1_fc3 = nn.Linear(256, 256)
        self.q1_fc4 = nn.Linear(256, 1)
        
        # Q2网络
        self.q2_fc1 = nn.Linear(state_dim + action_dim, 256)
        self.q2_fc2 = nn.Linear(256, 256)
        self.q2_fc3 = nn.Linear(256, 256)
        self.q2_fc4 = nn.Linear(256, 1)
        
        # Layer Normalization
        self.q1_ln1 = nn.LayerNorm(256)
        self.q1_ln2 = nn.LayerNorm(256)
        self.q1_ln3 = nn.LayerNorm(256)
        
        self.q2_ln1 = nn.LayerNorm(256)
        self.q2_ln2 = nn.LayerNorm(256)
        self.q2_ln3 = nn.LayerNorm(256)
        
        # 初始化权重
        self._initialize_weights()
    
    def _initialize_weights(self):
        """初始化网络权重"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.orthogonal_(m.weight, gain=np.sqrt(2))
                nn.init.constant_(m.bias, 0.0)
    
    def forward(self, state: torch.Tensor, action: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        前向传播
        
        Args:
            state: 状态张量 (batch_size, state_dim)
            action: 动作张量 (batch_size, action_dim)
        
        Returns:
            (q1, q2) - 两个Q网络的输出
        """
        # 拼接状态和动作
        sa = torch.cat([state, action], dim=1)
        
        # Q1网络
        q1 = F.relu(self.q1_ln1(self.q1_fc1(sa)))
        q1 = F.relu(self.q1_ln2(self.q1_fc2(q1)))
        q1 = F.relu(self.q1_ln3(self.q1_fc3(q1)))
        q1 = self.q1_fc4(q1)
        
        # Q2网络
        q2 = F.relu(self.q2_ln1(self.q2_fc1(sa)))
        q2 = F.relu(self.q2_ln2(self.q2_fc2(q2)))
        q2 = F.relu(self.q2_ln3(self.q2_fc3(q2)))
        q2 = self.q2_fc4(q2)
        
        return q1, q2
    
    def Q1(self, state: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        """
        仅返回Q1值（用于某些计算）
        
        Args:
            state: 状态张量
            action: 动作张量
        
        Returns:
            Q1值
        """
        sa = torch.cat([state, action], dim=1)
        q1 = F.relu(self.q1_ln1(self.q1_fc1(sa)))
        q1 = F.relu(self.q1_ln2(self.q1_fc2(q1)))
        q1 = F.relu(self.q1_ln3(self.q1_fc3(q1)))
        q1 = self.q1_fc4(q1)
        return q1

