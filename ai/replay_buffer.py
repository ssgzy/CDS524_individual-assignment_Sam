"""Prioritized Experience Replay buffer."""

from __future__ import annotations

from collections import deque
from typing import Deque, List, Tuple

import numpy as np


class ReplayBuffer:
    def __init__(self, capacity: int = 10000, alpha: float = 0.6):
        self.buffer: Deque[Tuple[np.ndarray, int, float, np.ndarray, bool]] = deque(maxlen=capacity)
        self.priorities: Deque[float] = deque(maxlen=capacity)
        self.alpha = alpha

    def push(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        priority: float | None = None,
    ) -> None:
        if priority is None:
            priority = max(self.priorities, default=1.0)
        self.buffer.append((state, action, reward, next_state, done))
        self.priorities.append(float(priority))

    def sample(self, batch_size: int, beta: float = 0.4):
        priorities = np.array(self.priorities, dtype=np.float32) ** self.alpha
        probs = priorities / priorities.sum()

        indices = np.random.choice(len(self.buffer), batch_size, p=probs, replace=False)
        samples = [self.buffer[i] for i in indices]
        states, actions, rewards, next_states, dones = zip(*samples)

        weights = (len(self.buffer) * probs[indices]) ** (-beta)
        weights /= weights.max()

        return (
            np.array(states, dtype=np.float32),
            np.array(actions, dtype=np.int64),
            np.array(rewards, dtype=np.float32),
            np.array(next_states, dtype=np.float32),
            np.array(dones, dtype=np.float32),
            np.array(weights, dtype=np.float32),
            indices,
        )

    def update_priorities(self, indices, td_errors) -> None:
        for idx, err in zip(indices, td_errors):
            self.priorities[idx] = float(abs(err) + 1e-6)

    def __len__(self) -> int:
        return len(self.buffer)
