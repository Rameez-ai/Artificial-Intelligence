"""
Smart Loan AI - RL Agent Training Script
==========================================
Trains the Q-Learning agent on the custom financial recommendation environment.

Usage:
    python train_agent.py [--episodes 5000] [--output ./trained_agent.pkl]
"""

import numpy as np
import argparse
import os
import json
from datetime import datetime
from environment import LoanRecommendationEnv
from agent import QLearningAgent


def train(n_episodes=5000, output_path=None):
    """Train the RL agent."""
    print("=" * 60)
    print("  Smart Loan AI - RL Agent Training")
    print(f"  Episodes: {n_episodes}")
    print("=" * 60)

    env = LoanRecommendationEnv()
    agent = QLearningAgent(
        n_states_per_dim=10, n_actions=env.N_ACTIONS,
        learning_rate=0.1, discount_factor=0.95,
        epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.998
    )

    reward_history = []
    best_avg_reward = -float('inf')

    for episode in range(n_episodes):
        state = env.reset()
        total_reward = 0
        done = False

        while not done:
            action = agent.select_action(state, training=True)
            next_state, reward, done, info = env.step(action)
            agent.update(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward

        agent.total_rewards.append(total_reward)
        agent.decay_epsilon()
        reward_history.append(total_reward)

        # Progress logging
        if (episode + 1) % 500 == 0:
            avg = np.mean(reward_history[-500:])
            print(f"  Episode {episode+1}/{n_episodes} | "
                  f"Avg Reward: {avg:.3f} | Epsilon: {agent.epsilon:.4f} | "
                  f"Q-table size: {len(agent.q_table)}")
            if avg > best_avg_reward:
                best_avg_reward = avg

    # Save agent
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), 'trained_agent.pkl')
    agent.save(output_path)
    print(f"\n  Agent saved to: {output_path}")

    # Save training metrics
    metrics = {
        'training_date': datetime.now().isoformat(),
        'n_episodes': n_episodes,
        'best_avg_reward': round(best_avg_reward, 4),
        'final_epsilon': round(agent.epsilon, 4),
        'q_table_size': len(agent.q_table),
        'final_avg_reward_100': round(np.mean(reward_history[-100:]), 4),
    }
    metrics_path = os.path.join(os.path.dirname(output_path), 'training_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"  Metrics saved to: {metrics_path}")

    print(f"\n{'=' * 60}")
    print(f"  Training Complete!")
    print(f"  Best Avg Reward: {best_avg_reward:.4f}")
    print(f"  Q-table entries: {len(agent.q_table)}")
    print(f"{'=' * 60}")

    return agent


def main():
    parser = argparse.ArgumentParser(description='Train RL recommendation agent')
    parser.add_argument('--episodes', type=int, default=5000)
    parser.add_argument('--output', type=str, default=None)
    args = parser.parse_args()
    train(args.episodes, args.output)


if __name__ == '__main__':
    main()
