"""DQN agent for ShadowBox."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import torch.nn.functional as F

from ai.dqn_model import DQNNetwork
from ai.replay_buffer import ReplayBuffer


class DQNAgent:
    def __init__(
        self,
        state_dim: int = 36,
        action_dim: int = 5,
        lr: float = 5e-4,
        gamma: float = 0.99,
        batch_size: int = 64,
        buffer_capacity: int = 10000,
        epsilon_start: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.995,
        target_update_freq: int = 500,
        per_alpha: float = 0.6,
        per_beta: float = 0.4,
        grad_clip: float = 1.0,
    ):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.online_net = DQNNetwork(state_dim, action_dim).to(self.device)
        self.target_net = DQNNetwork(state_dim, action_dim).to(self.device)
        self.target_net.load_state_dict(self.online_net.state_dict())
        self.target_net.eval()

        self.optimizer = torch.optim.Adam(self.online_net.parameters(), lr=lr)
        self.replay_buffer = ReplayBuffer(capacity=buffer_capacity, alpha=per_alpha)

        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.per_beta = per_beta
        self.grad_clip = grad_clip

        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        self.action_dim = action_dim
        self.step_count = 0

    def select_action(self, state: np.ndarray) -> int:
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)

        state_t = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            q_vals = self.online_net(state_t)
        return int(q_vals.argmax(dim=1).item())

    def train_step(self) -> Optional[float]:
        if len(self.replay_buffer) < self.batch_size:
            return None

        (
            states,
            actions,
            rewards,
            next_states,
            dones,
            weights,
            indices,
        ) = self.replay_buffer.sample(self.batch_size, beta=self.per_beta)

        states_t = torch.tensor(states, dtype=torch.float32, device=self.device)
        actions_t = torch.tensor(actions, dtype=torch.long, device=self.device)
        rewards_t = torch.tensor(rewards, dtype=torch.float32, device=self.device)
        next_states_t = torch.tensor(next_states, dtype=torch.float32, device=self.device)
        dones_t = torch.tensor(dones, dtype=torch.float32, device=self.device)
        weights_t = torch.tensor(weights, dtype=torch.float32, device=self.device)

        current_q = self.online_net(states_t).gather(1, actions_t.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            next_actions = self.online_net(next_states_t).argmax(dim=1)
            next_q = self.target_net(next_states_t).gather(1, next_actions.unsqueeze(1)).squeeze(1)
            target_q = rewards_t + self.gamma * next_q * (1.0 - dones_t)

        td_errors = (current_q - target_q).detach().abs().cpu().numpy()
        loss_per_sample = F.smooth_l1_loss(current_q, target_q, reduction="none")
        loss = (weights_t * loss_per_sample).mean()

        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.online_net.parameters(), self.grad_clip)
        self.optimizer.step()

        self.replay_buffer.update_priorities(indices, td_errors)

        self.step_count += 1
        if self.step_count % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.online_net.state_dict())

        return float(loss.item())

    def decay_epsilon(self) -> None:
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "online_net": self.online_net.state_dict(),
                "target_net": self.target_net.state_dict(),
                "optimizer": self.optimizer.state_dict(),
                "epsilon": self.epsilon,
                "step_count": self.step_count,
            },
            path,
        )

    def load(self, path: str | Path) -> None:
        ckpt = torch.load(path, map_location=self.device)
        self.online_net.load_state_dict(ckpt["online_net"])
        self.target_net.load_state_dict(ckpt["target_net"])
        self.optimizer.load_state_dict(ckpt["optimizer"])
        self.epsilon = float(ckpt.get("epsilon", self.epsilon))
        self.step_count = int(ckpt.get("step_count", self.step_count))
