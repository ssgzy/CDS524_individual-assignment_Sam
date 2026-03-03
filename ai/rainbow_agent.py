"""Complete Rainbow DQN Agent with all modern techniques."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F

from ai.dqn_model_enhanced import CNNDQNNetwork
from ai.nstep_replay_buffer import NStepReplayBuffer
from ai.curiosity import IntrinsicCuriosityModule


class RainbowDQNAgent:
    """
    Complete Rainbow DQN implementation with:
    - Dueling DQN ✓
    - Double DQN ✓
    - Prioritized Experience Replay ✓
    - N-step Returns ✓
    - Noisy Networks ✓
    - CNN State Representation ✓
    - Intrinsic Curiosity Module (ICM) ✓
    """

    def __init__(
        self,
        input_channels: int = 7,
        action_dim: int = 5,
        lr: float = 1e-4,
        gamma: float = 0.99,
        batch_size: int = 64,
        buffer_capacity: int = 50000,
        target_update_freq: int = 1000,
        per_alpha: float = 0.6,
        per_beta_start: float = 0.4,
        per_beta_frames: int = 100000,
        n_step: int = 3,
        use_noisy: bool = True,
        use_curiosity: bool = True,
        curiosity_weight: float = 0.5,
        grad_clip: float = 10.0,
    ):
        # Use MPS (Metal) on Mac, CUDA on NVIDIA, otherwise CPU
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")
        print(f"🚀 Rainbow DQN using device: {self.device}")

        # Networks
        self.online_net = CNNDQNNetwork(
            input_channels=input_channels,
            action_dim=action_dim,
            use_noisy=use_noisy,
        ).to(self.device)

        self.target_net = CNNDQNNetwork(
            input_channels=input_channels,
            action_dim=action_dim,
            use_noisy=use_noisy,
        ).to(self.device)

        self.target_net.load_state_dict(self.online_net.state_dict())
        self.target_net.eval()

        # Curiosity module
        self.use_curiosity = use_curiosity
        self.curiosity_weight = curiosity_weight
        if use_curiosity:
            self.curiosity_module = IntrinsicCuriosityModule(
                state_dim=0,  # Not used for CNN
                action_dim=action_dim,
                feature_dim=256,
                use_cnn=True,
                input_channels=input_channels,
            ).to(self.device)
            self.curiosity_optimizer = torch.optim.Adam(
                self.curiosity_module.parameters(), lr=lr
            )

        # Optimizer
        self.optimizer = torch.optim.Adam(self.online_net.parameters(), lr=lr)

        # N-step Replay Buffer with PER
        self.replay_buffer = NStepReplayBuffer(
            capacity=buffer_capacity,
            alpha=per_alpha,
            n_step=n_step,
            gamma=gamma,
        )

        # Hyperparameters
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.grad_clip = grad_clip
        self.action_dim = action_dim
        self.use_noisy = use_noisy

        # PER beta annealing
        self.per_beta_start = per_beta_start
        self.per_beta_frames = per_beta_frames
        self.frame_count = 0

        # No epsilon needed with Noisy Networks
        self.epsilon = 0.0 if use_noisy else 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

        self.step_count = 0

        # Statistics
        self.intrinsic_rewards = []
        self.extrinsic_rewards = []

    def get_beta(self) -> float:
        """Anneal beta from beta_start to 1.0."""
        return min(
            1.0,
            self.per_beta_start
            + (1.0 - self.per_beta_start) * self.frame_count / self.per_beta_frames,
        )

    def select_action(self, state: np.ndarray, eval_mode: bool = False) -> int:
        """
        Select action using the online network.
        With Noisy Networks, exploration is automatic.
        """
        # Convert state to tensor
        state_t = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)

        # Epsilon-greedy (only if not using noisy networks)
        if not self.use_noisy and not eval_mode and random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)

        # Reset noise for exploration
        if self.use_noisy and not eval_mode:
            self.online_net.reset_noise()

        with torch.no_grad():
            q_vals = self.online_net(state_t)

        return int(q_vals.argmax(dim=1).item())

    def store_transition(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ):
        """Store transition in replay buffer."""
        self.replay_buffer.push(state, action, reward, next_state, done)
        self.frame_count += 1

        # Track rewards
        self.extrinsic_rewards.append(reward)

    def train_step(self) -> Optional[dict]:
        """Perform one training step."""
        if len(self.replay_buffer) < self.batch_size:
            return None

        # Sample batch
        beta = self.get_beta()
        sample = self.replay_buffer.sample(self.batch_size, beta=beta)

        if sample is None:
            return None

        states, actions, rewards, next_states, dones, weights, indices = sample

        # Convert to tensors
        states_t = torch.tensor(states, dtype=torch.float32, device=self.device)
        actions_t = torch.tensor(actions, dtype=torch.long, device=self.device)
        rewards_t = torch.tensor(rewards, dtype=torch.float32, device=self.device)
        next_states_t = torch.tensor(next_states, dtype=torch.float32, device=self.device)
        dones_t = torch.tensor(dones, dtype=torch.float32, device=self.device)
        weights_t = torch.tensor(weights, dtype=torch.float32, device=self.device)

        # === Intrinsic Curiosity Module ===
        intrinsic_reward_t = torch.zeros_like(rewards_t)
        curiosity_loss = 0.0

        if self.use_curiosity:
            intrinsic_reward_t, forward_loss, inverse_loss = self.curiosity_module(
                states_t, actions_t, next_states_t
            )

            # Train curiosity module
            curiosity_loss = forward_loss + inverse_loss
            self.curiosity_optimizer.zero_grad()
            curiosity_loss.backward()
            torch.nn.utils.clip_grad_norm_(
                self.curiosity_module.parameters(), self.grad_clip
            )
            self.curiosity_optimizer.step()

            # Track intrinsic rewards
            self.intrinsic_rewards.extend(intrinsic_reward_t.detach().cpu().numpy())

            # Combine extrinsic and intrinsic rewards
            rewards_t = rewards_t + self.curiosity_weight * intrinsic_reward_t.detach()

        # === Double DQN with Dueling Architecture ===
        # Current Q-values
        current_q = self.online_net(states_t).gather(1, actions_t.unsqueeze(1)).squeeze(1)

        # Target Q-values (Double DQN)
        with torch.no_grad():
            # Use online network to select actions
            next_actions = self.online_net(next_states_t).argmax(dim=1)
            # Use target network to evaluate actions
            next_q = self.target_net(next_states_t).gather(1, next_actions.unsqueeze(1)).squeeze(1)
            target_q = rewards_t + self.gamma * next_q * (1.0 - dones_t)

        # TD errors for PER
        td_errors = (current_q - target_q).detach().abs().cpu().numpy()

        # Weighted loss
        loss_per_sample = F.smooth_l1_loss(current_q, target_q, reduction="none")
        loss = (weights_t * loss_per_sample).mean()

        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.online_net.parameters(), self.grad_clip)
        self.optimizer.step()

        # Update priorities
        self.replay_buffer.update_priorities(indices, td_errors)

        # Update target network
        self.step_count += 1
        if self.step_count % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.online_net.state_dict())

        # Decay epsilon (if not using noisy networks)
        if not self.use_noisy:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        return {
            "loss": float(loss.item()),
            "curiosity_loss": float(curiosity_loss) if self.use_curiosity else 0.0,
            "mean_q": float(current_q.mean().item()),
            "beta": beta,
            "epsilon": self.epsilon,
        }

    def get_statistics(self) -> dict:
        """Get training statistics."""
        stats = {}

        if self.extrinsic_rewards:
            stats["mean_extrinsic_reward"] = np.mean(self.extrinsic_rewards[-100:])

        if self.intrinsic_rewards:
            stats["mean_intrinsic_reward"] = np.mean(self.intrinsic_rewards[-100:])

        return stats

    def reset_statistics(self):
        """Reset statistics."""
        self.intrinsic_rewards = []
        self.extrinsic_rewards = []

    def save(self, path: str | Path) -> None:
        """Save agent state."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        save_dict = {
            "online_net": self.online_net.state_dict(),
            "target_net": self.target_net.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "epsilon": self.epsilon,
            "step_count": self.step_count,
            "frame_count": self.frame_count,
        }

        if self.use_curiosity:
            save_dict["curiosity_module"] = self.curiosity_module.state_dict()
            save_dict["curiosity_optimizer"] = self.curiosity_optimizer.state_dict()

        torch.save(save_dict, path)
        print(f"💾 Model saved to {path}")

    def load(self, path: str | Path) -> None:
        """Load agent state."""
        ckpt = torch.load(path, map_location=self.device)

        self.online_net.load_state_dict(ckpt["online_net"])
        self.target_net.load_state_dict(ckpt["target_net"])
        self.optimizer.load_state_dict(ckpt["optimizer"])
        self.epsilon = float(ckpt.get("epsilon", self.epsilon))
        self.step_count = int(ckpt.get("step_count", self.step_count))
        self.frame_count = int(ckpt.get("frame_count", self.frame_count))

        if self.use_curiosity and "curiosity_module" in ckpt:
            self.curiosity_module.load_state_dict(ckpt["curiosity_module"])
            self.curiosity_optimizer.load_state_dict(ckpt["curiosity_optimizer"])

        print(f"📂 Model loaded from {path}")
