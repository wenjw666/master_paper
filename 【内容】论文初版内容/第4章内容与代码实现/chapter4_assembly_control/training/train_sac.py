"""
SAC训练主脚本
"""

import argparse
import yaml
import numpy as np
import torch
from tqdm import tqdm
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from sac_algorithm.sac import SAC
from sac_algorithm.replay_buffer import ReplayBuffer
from rl_environment.connector_assembly_env import ConnectorAssemblyEnv


def train_sac(config_path: str, total_steps: int, save_dir: str):
    """
    训练SAC策略
    
    Args:
        config_path: 配置文件路径
        total_steps: 总训练步数
        save_dir: 模型保存目录
    """
    # 加载配置
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # 创建环境
    env = ConnectorAssemblyEnv(
        render_mode=None,
        use_domain_randomization=config.get('use_domain_randomization', True)
    )
    
    # 获取状态和动作维度
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space_gym.shape[0]
    action_range = (env.action_space_gym.low[0], env.action_space_gym.high[0])
    
    # 初始化SAC
    sac = SAC(
        state_dim=state_dim,
        action_dim=action_dim,
        action_range=action_range,
        device=config.get('device', 'cuda'),
        lr_actor=config['learning_rate']['actor'],
        lr_critic=config['learning_rate']['critic'],
        lr_alpha=config['learning_rate']['alpha'],
        gamma=config['gamma'],
        tau=config['tau'],
        alpha_auto_tune=config.get('alpha_auto_tune', True)
    )
    
    # 初始化回放缓冲区
    replay_buffer = ReplayBuffer(capacity=config['replay_buffer_size'])
    
    # 训练循环
    state, _ = env.reset()
    episode_reward = 0
    episode_length = 0
    episode_count = 0
    
    progress_bar = tqdm(total=total_steps, desc="Training")
    
    for step in range(total_steps):
        # 选择动作
        if len(replay_buffer) < config.get('warmup_steps', 10000):
            # 探索阶段：随机动作
            action = env.action_space_gym.sample()
        else:
            # 使用策略
            action = sac.select_action(state, deterministic=False)
        
        # 执行动作
        next_state, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        
        # 存储经验
        replay_buffer.push(state, action, reward, next_state, done)
        
        state = next_state
        episode_reward += reward
        episode_length += 1
        
        # 更新网络
        if len(replay_buffer) >= config.get('warmup_steps', 10000):
            if step % config.get('update_frequency', 1) == 0:
                batch = replay_buffer.sample(config['batch_size'])
                losses = sac.update(batch)
                
                # 记录损失（可选：使用tensorboard）
                if step % 1000 == 0:
                    progress_bar.set_postfix({
                        'episode': episode_count,
                        'reward': episode_reward,
                        'critic_loss': losses['critic_loss'],
                        'alpha': losses['alpha']
                    })
        
        # Episode结束
        if done:
            episode_count += 1
            state, _ = env.reset()
            episode_reward = 0
            episode_length = 0
        
        # 保存模型
        if step % config.get('save_frequency', 100000) == 0 and step > 0:
            save_path = os.path.join(save_dir, f'sac_step_{step}.pt')
            sac.save(save_path)
            print(f"\n模型已保存: {save_path}")
        
        progress_bar.update(1)
    
    # 保存最终模型
    final_save_path = os.path.join(save_dir, 'sac_final.pt')
    sac.save(final_save_path)
    print(f"\n最终模型已保存: {final_save_path}")
    
    env.close()
    progress_bar.close()


def main():
    parser = argparse.ArgumentParser(description='SAC训练脚本')
    parser.add_argument('--config', type=str, required=True,
                       help='配置文件路径')
    parser.add_argument('--total-steps', type=int, default=1000000,
                       help='总训练步数')
    parser.add_argument('--save-dir', type=str, default='./checkpoints',
                       help='模型保存目录')
    
    args = parser.parse_args()
    
    train_sac(args.config, args.total_steps, args.save_dir)


if __name__ == '__main__':
    main()

