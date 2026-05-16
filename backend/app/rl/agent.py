"""
Smart Loan AI - Q-Learning Agent
=================================
Tabular Q-Learning agent for financial recommendation optimization.
Uses epsilon-greedy exploration with decaying epsilon.
"""

import numpy as np
import pickle
import os


class QLearningAgent:
    """Q-Learning agent with discretized state space."""

    def __init__(self, n_states_per_dim=10, n_actions=10, learning_rate=0.1,
                 discount_factor=0.95, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995):
        self.n_bins = n_states_per_dim
        self.n_actions = n_actions
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        # Q-table: discretized state -> action values
        # State is 7-dimensional, each dimension discretized into n_bins
        self.q_table = {}

        # Training metrics
        self.total_rewards = []
        self.episode_lengths = []

    def _discretize_state(self, state):
        """Convert continuous state to discrete tuple for Q-table lookup."""
        discrete = tuple(
            min(int(s * self.n_bins), self.n_bins - 1) for s in state
        )
        return discrete

    def _get_q_values(self, state_key):
        """Get Q-values for a state, initializing if needed."""
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.n_actions)
        return self.q_table[state_key]

    def select_action(self, state, training=True):
        """Select action using epsilon-greedy policy."""
        state_key = self._discretize_state(state)
        q_values = self._get_q_values(state_key)

        if training and np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)
        return int(np.argmax(q_values))

    def update(self, state, action, reward, next_state, done):
        """Update Q-table using TD learning."""
        state_key = self._discretize_state(state)
        next_state_key = self._discretize_state(next_state)

        q_values = self._get_q_values(state_key)
        next_q_values = self._get_q_values(next_state_key)

        if done:
            target = reward
        else:
            target = reward + self.gamma * np.max(next_q_values)

        q_values[action] += self.lr * (target - q_values[action])

    def decay_epsilon(self):
        """Decay exploration rate."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def get_top_actions(self, state, n=3):
        """Get top N recommended actions for a state."""
        state_key = self._discretize_state(state)
        q_values = self._get_q_values(state_key)
        top_indices = np.argsort(q_values)[::-1][:n]
        return [(int(idx), float(q_values[idx])) for idx in top_indices]

    def get_metrics(self):
        """Return training metrics."""
        return {
            'total_episodes': len(self.total_rewards),
            'q_table_size': len(self.q_table),
            'epsilon': round(self.epsilon, 4),
            'avg_reward_last_100': round(np.mean(self.total_rewards[-100:]), 4) if self.total_rewards else 0,
            'max_reward': round(max(self.total_rewards), 4) if self.total_rewards else 0,
        }

    def save(self, filepath):
        """Save agent to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filepath):
        """Load agent from disk."""
        with open(filepath, 'rb') as f:
            return pickle.load(f)
