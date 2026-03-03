"""Enhanced DQN Agent with all modern techniques."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import torch.nn.functional as F

from ai.dqn_model_enhanced import CNNDQNNetwork, DQNNetwork
from ai.nstep_replay_buffer import NStepReplayBuffer
from ai.curiosity import IntrinsicCuriosityModule


class EnhancedDQNAgent:
    """
    Enhanced DQN Agent with:
    - CNN state representation
    - Noisy Networks for exploration
    - N-step Returns
    - Intrinsic Curiosity Module (ICM)
    - Dueling Double DQN
    - Prioritized Experience Replay
    """

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
        # New parameters
        use_cnn: bool = True,
        use_noisy: bool = True,
        use_curiosity: bool = True,
        n_step: int = 3,
        curiosity_beta: float = 0.2,
        input_channels: int = 7,
    ):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.use_cnn = use_cnn
        self.use_noisy = use_noisy
        self.use_curiosity = use_curiosity
        self.curiosity_beta = curiosity_beta

        # Create networks
        if use_cnn:
            self.online_net = CNNDQNNetwork(input_channels, action_dim, use_noisy).to(self.device)
            self.target_net = CNNDQNNetwork(input_channels, action_dim, use_noisy).to(self.device)
        else:
            self.online_net = DQNNetwork(state_dim, action_dim).to(self.device)
            self.target_net = DQNNetwork(state_dim, action_dim).to(self.device)

        self.target_net.load_state_dict(self.online_net.state_dict())
        self.target_net.eval()

        # Curiosity module
        if use_curiosity:
            self.curiosity_module = IntrinsicCuriosityModule(
                state_dim, action_dim, use_cnn=use_cnn, input_channels=input_channels
            ).to(self.device)
            # Optimizer for both Q-network and curiosity
            self.optimizer = torch.optim.Adam(
                list(self.online_net.parameters()) + list(self.curiosity_module.parameters()),
                lr=lr
            )
        else:
            self.curiosity_module = None
            self.optimizer = torch.optim.Adam(self.online_net.parameters(), lr=lr)

        # N-step replay buffer
        self.replay_buffer = NStepReplayBuffer(
            capacity=buffer_capacity,
            alpha=per_alpha,
            n_step=n_step,
            gamma=gamma,
        )

        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.per_beta = per_beta
        self.grad_clip = grad_clip
        self.n_step = n_step

        # Epsilon for epsilon-greedy (only used if not using noisy networks)
        self.epsilon = epsilon_start if not use_noisy else 0.0
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        self.action_dim = action_dim
        self.step_count = 0

    def select_action(self, state: np.ndarray) -> int:
        """Select action using epsilon-greedy or noisy networks."""
        # If using noisy networks, no epsilon-greedy needed
        if self.use_noisy:
            state_t = self._prepare_state(state).unsqueeze(0)
            with torch.no_grad():
                q_vals = self.online_net(state_t)
            return int(q_vals.argmax(dim=1).item())

        # Otherwise use epsilon-greedy
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)

        state_t = self._prepare_state(state).unsqueeze(0)
        with torch.no_grad():
            q_vals = self.online_net(state_t)
        return int(q_vals.argmax(dim=1).item())

    def _prepare_state(self, state: np.ndarray) -> torch.Tensor:
        """Prepare state tensor based on CNN or FC mode."""
        if self.use_cnn:
            # State should be (C, H, W) for CNN
            return torch.tensor(state, dtype=torch.float32, device=self.device)
        else:
            # State should be (D,) for FC
            return torch.tensor(state, dtype=torch.float32, device=self.device)

    def train_step(self) -> Optional[dict]:
        """Training step with curiosity and n-step returns."""
        if len(self.replay_buffer) < self.batch_size:
            return None

        # Sample batch
        batch = self.replay_buffer.sample(self.batch_size, beta=self.per_beta)
        if batch is None:
            return None

        states, actions, rewards, next_states, dones, weights, indices = batch

        # Prepare tensors
        if self.use_cnn:
            states_t = torch.tensor(states, dtype=torch.float32, device=self.device)
            next_states_t = torch.tensor(next_states, dtype=torch.float32, device=self.device)
        else:
            states_t = torch.tensor(states, dtype=torch.float32, device=self.device)
            next_states_t = torch.tensor(next_states, dtype=torch.float32, device=self.device)

        actions_t = torch.tensor(actions, dtype=torch.long, device=self.device)
        rewards_t = torch.tensor(rewards, dtype=torch.float32, device=self.device)
        dones_t = torch.tensor(dones, dtype=torch.float32, device=self.device)
        weights_t = torch.tensor(weights, dtype=torch.float32, device=self.device)

        # Compute intrinsic reward if using curiosity
        if self.use_curiosity:
            intrinsic_reward, forward_loss, inverse_loss = self.curiosity_module(
                states_t, actions_t, next_states_t
            )
            # Combine extrinsic and intrinsic rewards
            total_rewards = rewards_t + self.curiosity_beta * intrinsic_reward.detach()
        else:
            total_rewards = rewards_t
            forward_loss = torch.tensor(0.0)
            inverse_loss = torch.tensor(0.0)

        # Double DQN
        current_q = self.online_net(states_t).gather(1, actions_t.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            # Online network selects action
            next_actions = self.online_net(next_states_t).argmax(dim=1)
            # Target network evaluates action
            next_q = self.target_net(next_states_t).gather(1, next_actions.unsqueeze(1)).squeeze(1)
            # N-step target (gamma^n is already in the buffer)
            target_q = total_rewards + (self.gamma ** self.n_step) * next_q * (1.0 - dones_t)

        # TD error for priority update
        td_errors = (current_q - target_q).detach().abs().cpu().numpy()

        # Q-learning loss
        loss_per_sample = F.smooth_l1_loss(current_q, target_q, reduction="none")
        q_loss = (weights_t * loss_per_sample).mean()

        # Total loss
        if self.use_curiosity:
            total_loss = q_loss + forward_loss + 0.2 * inverse_loss
        else:
            total_loss = q_loss

        # Optimize
        self.optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.online_net.parameters(), self.grad_clip)
        if self.use_curiosity:
            torch.nn.utils.clip_grad_norm_(self.curiosity_module.parameters(), self.grad_clip)
        self.optimizer.step()

        # Reset noise in noisy networks
        if self.use_noisy:
            self.online_net.reset_noise()
            self.target_net.reset_noise()

        # Update priorities
        self.replay_buffer.update_priorities(indices, td_errors)

        # Update target network
        self.step_count += 1
        if self.step_count % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.online_net.state_dict())

        return {
            "q_loss": float(q_loss.item()),
            "forward_loss": float(forward_loss.item()) if self.use_curiosity else 0.0,
            "inverse_loss": float(inverse_loss.item()) if self.use_curiosity else 0.0,
            "total_loss": float(total_loss.item()),
            "mean_q": float(current_q.mean().item()),
        }

    def decay_epsilon(self) -> None:
        """Decay epsilon (only used if not using noisy networks)."""
        if not self.use_noisy:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        save_dict = {
            "online_net": self.online_net.state_dict(),
            "target_net": self.target_net.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "epsilon": self.epsilon,
            "step_count": self.step_count,
        }
        if self.use_curiosity:
            save_dict["curiosity"] = self.curiosity_module.state_dict()
        torch.save(save_dict, path)

    def load(self, path: str | Path) -> None:
        ckpt = torch.load(path, map_location=self.device)
        self.online_net.load_state_dict(ckpt["online_net"])
        self.target_net.load_state_dict(ckpt["target_net"])
        self.optimizer.load_state_dict(ckpt["optimizer"])
        self.epsilon = float(ckpt.get("epsilon", self.epsilon))
        self.step_count = int(ckpt.get("step_count", self.step_count))
        if self.use_curiosity and "curiosity" in ckpt:
            self.curiosity_module.load_state_dict(ckpt["curiosity"])
