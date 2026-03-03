"""N-step Replay Buffer with Prioritized Experience Replay."""

from __future__ import annotations

from collections import deque
from typing import Tuple

import numpy as np


class NStepReplayBuffer:
    """
    N-step Replay Buffer with Prioritized Experience Replay.

    Combines:
    - N-step returns for faster credit assignment
    - Prioritized sampling based on TD error
    """

    def __init__(
        self,
        capacity: int = 10000,
        alpha: float = 0.6,
        n_step: int = 3,
        gamma: float = 0.99,
    ):
        self.capacity = capacity
        self.alpha = alpha
        self.n_step = n_step
        self.gamma = gamma

        self.buffer = []
        self.priorities = np.zeros(capacity, dtype=np.float32)
        self.position = 0
        self.size = 0

        # N-step buffer
        self.n_step_buffer = deque(maxlen=n_step)

    def _get_n_step_info(self) -> Tuple:
        """Calculate n-step return and get n-step transition."""
        # Get first and last transitions
        state, action = self.n_step_buffer[0][:2]
        _, _, _, next_state, done = self.n_step_buffer[-1]

        # Calculate n-step return
        n_step_return = 0.0
        for i, (_, _, reward, _, d) in enumerate(self.n_step_buffer):
            n_step_return += (self.gamma ** i) * reward
            if d:  # If episode ends, stop accumulating
                next_state = self.n_step_buffer[i][3]
                done = True
                break

        return state, action, n_step_return, next_state, done

    def push(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        priority: float = None,
    ):
        """Add transition to n-step buffer and main buffer."""
        # Add to n-step buffer
        self.n_step_buffer.append((state, action, reward, next_state, done))

        # Only add to main buffer when n-step buffer is full
        if len(self.n_step_buffer) < self.n_step:
            return

        # Get n-step transition
        n_step_transition = self._get_n_step_info()

        # Set priority
        if priority is None:
            max_priority = self.priorities[:self.size].max() if self.size > 0 else 1.0
            priority = max_priority

        # Add to main buffer
        if len(self.buffer) < self.capacity:
            self.buffer.append(n_step_transition)
        else:
            self.buffer[self.position] = n_step_transition

        self.priorities[self.position] = priority
        self.position = (self.position + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def sample(
        self,
        batch_size: int,
        beta: float = 0.4,
    ) -> Tuple:
        """Sample batch with prioritized sampling."""
        if self.size < batch_size:
            return None

        # Calculate sampling probabilities
        priorities = self.priorities[:self.size]
        probs = priorities ** self.alpha
        probs /= probs.sum()

        # Sample indices
        indices = np.random.choice(self.size, batch_size, p=probs, replace=False)

        # Calculate importance sampling weights
        weights = (self.size * probs[indices]) ** (-beta)
        weights /= weights.max()

        # Get samples
        samples = [self.buffer[idx] for idx in indices]
        states, actions, rewards, next_states, dones = zip(*samples)

        return (
            np.array(states),
            np.array(actions),
            np.array(rewards, dtype=np.float32),
            np.array(next_states),
            np.array(dones, dtype=np.float32),
            weights.astype(np.float32),
            indices,
        )

    def update_priorities(self, indices: np.ndarray, priorities: np.ndarray):
        """Update priorities for sampled transitions."""
        for idx, priority in zip(indices, priorities):
            self.priorities[idx] = priority + 1e-6  # Add small epsilon

    def __len__(self) -> int:
        return self.size
