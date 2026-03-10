"""
经验回放缓冲区
存储和采样训练经验
"""

import numpy as np
from typing import Dict, Optional
import random


class ReplayBuffer:
    """经验回放缓冲区"""
    
    def __init__(self, capacity: int = 1000000):
        """
        初始化回放缓冲区
        
        Args:
            capacity: 缓冲区容量
        """
        self.capacity = capacity
        self.buffer = []
        self.position = 0
    
    def push(self,
            state: np.ndarray,
            action: np.ndarray,
            reward: float,
            next_state: np.ndarray,
            done: bool):
        """
        添加经验到缓冲区
        
        Args:
            state: 状态
            action: 动作
            reward: 奖励
            next_state: 下一状态
            done: 是否终止
        """
        if len(self.buffer) < self.capacity:
            self.buffer.append(None)
        
        self.buffer[self.position] = (state, action, reward, next_state, done)
        self.position = (self.position + 1) % self.capacity
    
    def sample(self, batch_size: int) -> Dict:
        """
        从缓冲区采样批次
        
        Args:
            batch_size: 批次大小
        
        Returns:
            经验批次字典
        """
        batch = random.sample(self.buffer, batch_size)
        
        states = np.array([e[0] for e in batch])
        actions = np.array([e[1] for e in batch])
        rewards = np.array([e[2] for e in batch])
        next_states = np.array([e[3] for e in batch])
        dones = np.array([e[4] for e in batch])
        
        return {
            'states': states,
            'actions': actions,
            'rewards': rewards,
            'next_states': next_states,
            'dones': dones
        }
    
    def __len__(self) -> int:
        """返回缓冲区当前大小"""
        return len(self.buffer)

