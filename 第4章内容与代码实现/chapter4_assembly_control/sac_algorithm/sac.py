"""
Soft Actor-Critic (SAC) 算法实现
最大熵强化学习框架
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Dict, Optional, Tuple
import sys
import os

sys.path.append(os.path.dirname(__file__))
from .actor import Actor
from .critic import Critic
from .replay_buffer import ReplayBuffer


class SAC:
    """Soft Actor-Critic算法"""
    
    def __init__(self,
                 state_dim: int,
                 action_dim: int,
                 action_range: Tuple[float, float],
                 device: str = 'cuda',
                 lr_actor: float = 3e-4,
                 lr_critic: float = 3e-4,
                 lr_alpha: float = 3e-4,
                 gamma: float = 0.99,
                 tau: float = 0.005,
                 alpha: Optional[float] = None,
                 alpha_auto_tune: bool = True):
        """
        初始化SAC算法
        
        Args:
            state_dim: 状态维度
            action_dim: 动作维度
            action_range: 动作范围 (low, high)
            device: 计算设备
            lr_actor: Actor学习率
            lr_critic: Critic学习率
            lr_alpha: 温度系数学习率
            gamma: 折扣因子
            tau: 软更新系数
            alpha: 初始温度系数（如果为None则自动调节）
            alpha_auto_tune: 是否自动调节温度系数
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.action_range = action_range
        self.device = device
        self.gamma = gamma
        self.tau = tau
        self.alpha_auto_tune = alpha_auto_tune
        
        # 初始化Actor和Critic网络
        self.actor = Actor(state_dim, action_dim, action_range).to(device)
        self.critic = Critic(state_dim, action_dim).to(device)
        self.critic_target = Critic(state_dim, action_dim).to(device)
        
        # 复制Critic参数到目标网络
        self.critic_target.load_state_dict(self.critic.state_dict())
        
        # 优化器
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=lr_actor)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=lr_critic)
        
        # 温度系数（熵权重）
        if alpha_auto_tune:
            self.target_entropy = -action_dim  # 目标熵
            self.log_alpha = torch.zeros(1, requires_grad=True, device=device)
            self.alpha_optimizer = optim.Adam([self.log_alpha], lr=lr_alpha)
            self.alpha = None  # 动态计算
        else:
            self.alpha = alpha if alpha is not None else 0.2
            self.log_alpha = None
            self.alpha_optimizer = None
    
    def select_action(self, state: np.ndarray, deterministic: bool = False) -> np.ndarray:
        """
        选择动作
        
        Args:
            state: 状态向量
            deterministic: 是否使用确定性策略
        
        Returns:
            动作向量
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            if deterministic:
                # 确定性策略：使用均值
                action, _ = self.actor(state_tensor)
            else:
                # 随机策略：采样
                action, _ = self.actor.sample(state_tensor)
        
        action = action.cpu().numpy()[0]
        return action
    
    def update(self, batch: Dict) -> Dict:
        """
        更新网络参数
        
        Args:
            batch: 经验批次 {
                'states': (batch_size, state_dim),
                'actions': (batch_size, action_dim),
                'rewards': (batch_size,),
                'next_states': (batch_size, state_dim),
                'dones': (batch_size,)
            }
        
        Returns:
            损失字典
        """
        states = torch.FloatTensor(batch['states']).to(self.device)
        actions = torch.FloatTensor(batch['actions']).to(self.device)
        rewards = torch.FloatTensor(batch['rewards']).to(self.device)
        next_states = torch.FloatTensor(batch['next_states']).to(self.device)
        dones = torch.FloatTensor(batch['dones']).to(self.device)
        
        # 更新温度系数
        if self.alpha_auto_tune:
            self.alpha = torch.exp(self.log_alpha)
        
        # 更新Critic
        critic_loss = self._update_critic(states, actions, rewards, next_states, dones)
        
        # 更新Actor
        actor_loss = self._update_actor(states)
        
        # 更新温度系数
        if self.alpha_auto_tune:
            alpha_loss = self._update_alpha(states)
        else:
            alpha_loss = 0.0
        
        # 软更新目标网络
        self._soft_update_target()
        
        return {
            'critic_loss': critic_loss,
            'actor_loss': actor_loss,
            'alpha_loss': alpha_loss,
            'alpha': self.alpha.item() if isinstance(self.alpha, torch.Tensor) else self.alpha
        }
    
    def _update_critic(self, states, actions, rewards, next_states, dones):
        """更新Critic网络"""
        with torch.no_grad():
            # 计算目标Q值
            next_actions, next_log_probs = self.actor.sample(next_states)
            q1_next, q2_next = self.critic_target(next_states, next_actions)
            q_next = torch.min(q1_next, q2_next) - self.alpha * next_log_probs
            target_q = rewards + (1 - dones) * self.gamma * q_next
        
        # 当前Q值
        q1, q2 = self.critic(states, actions)
        
        # Critic损失
        critic_loss = nn.MSELoss()(q1, target_q) + nn.MSELoss()(q2, target_q)
        
        # 反向传播
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()
        
        return critic_loss.item()
    
    def _update_actor(self, states):
        """更新Actor网络"""
        # 采样动作
        actions, log_probs = self.actor.sample(states)
        
        # Q值
        q1, q2 = self.critic(states, actions)
        q = torch.min(q1, q2)
        
        # Actor损失（最大熵目标）
        actor_loss = (self.alpha * log_probs - q).mean()
        
        # 反向传播
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()
        
        return actor_loss.item()
    
    def _update_alpha(self, states):
        """更新温度系数"""
        with torch.no_grad():
            actions, log_probs = self.actor.sample(states)
        
        alpha_loss = -(self.log_alpha * (log_probs + self.target_entropy).detach()).mean()
        
        self.alpha_optimizer.zero_grad()
        alpha_loss.backward()
        self.alpha_optimizer.step()
        
        return alpha_loss.item()
    
    def _soft_update_target(self):
        """软更新目标网络"""
        for target_param, param in zip(self.critic_target.parameters(), self.critic.parameters()):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)
    
    def save(self, filepath: str):
        """保存模型"""
        torch.save({
            'actor': self.actor.state_dict(),
            'critic': self.critic.state_dict(),
            'critic_target': self.critic_target.state_dict(),
            'actor_optimizer': self.actor_optimizer.state_dict(),
            'critic_optimizer': self.critic_optimizer.state_dict(),
            'log_alpha': self.log_alpha if self.alpha_auto_tune else None,
            'alpha_optimizer': self.alpha_optimizer.state_dict() if self.alpha_auto_tune else None
        }, filepath)
    
    def load(self, filepath: str):
        """加载模型"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.actor.load_state_dict(checkpoint['actor'])
        self.critic.load_state_dict(checkpoint['critic'])
        self.critic_target.load_state_dict(checkpoint['critic_target'])
        self.actor_optimizer.load_state_dict(checkpoint['actor_optimizer'])
        self.critic_optimizer.load_state_dict(checkpoint['critic_optimizer'])
        
        if self.alpha_auto_tune and checkpoint['log_alpha'] is not None:
            self.log_alpha = checkpoint['log_alpha']
            self.alpha_optimizer.load_state_dict(checkpoint['alpha_optimizer'])

