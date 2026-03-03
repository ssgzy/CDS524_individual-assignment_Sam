"""Intrinsic Curiosity Module (ICM) for exploration."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class IntrinsicCuriosityModule(nn.Module):
    """
    Intrinsic Curiosity Module (Pathak et al., 2017)

    Provides intrinsic reward based on prediction error of state transitions.
    Encourages exploration in sparse reward environments.
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        feature_dim: int = 256,
        use_cnn: bool = False,
        input_channels: int = 7,
    ):
        super().__init__()
        self.use_cnn = use_cnn
        self.feature_dim = feature_dim

        if use_cnn:
            # CNN feature encoder
            self.feature_encoder = nn.Sequential(
                nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.Conv2d(32, 64, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.Flatten(),
                nn.Linear(64 * 7 * 7, feature_dim),
                nn.ReLU(),
            )
        else:
            # FC feature encoder
            self.feature_encoder = nn.Sequential(
                nn.Linear(state_dim, 256),
                nn.ReLU(),
                nn.Linear(256, feature_dim),
                nn.ReLU(),
            )

        # Forward model: predicts next state features from current features and action
        self.forward_model = nn.Sequential(
            nn.Linear(feature_dim + action_dim, 256),
            nn.ReLU(),
            nn.Linear(256, feature_dim),
        )

        # Inverse model: predicts action from current and next state features
        self.inverse_model = nn.Sequential(
            nn.Linear(feature_dim * 2, 256),
            nn.ReLU(),
            nn.Linear(256, action_dim),
        )

    def encode_state(self, state: torch.Tensor) -> torch.Tensor:
        """Encode state to feature representation."""
        return self.feature_encoder(state)

    def forward(
        self,
        state: torch.Tensor,
        action: torch.Tensor,
        next_state: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Compute ICM losses and intrinsic reward.

        Returns:
            intrinsic_reward: Prediction error as curiosity reward
            forward_loss: Forward model loss
            inverse_loss: Inverse model loss
        """
        # Encode states
        state_features = self.encode_state(state)
        next_state_features = self.encode_state(next_state)

        # Forward model: predict next state features
        action_onehot = F.one_hot(action, num_classes=self.inverse_model[-1].out_features).float()
        forward_input = torch.cat([state_features, action_onehot], dim=1)
        predicted_next_features = self.forward_model(forward_input)

        # Forward loss (intrinsic reward)
        forward_loss = F.mse_loss(predicted_next_features, next_state_features.detach(), reduction='none')
        intrinsic_reward = forward_loss.mean(dim=1)  # Per-sample reward
        forward_loss = forward_loss.mean()  # Scalar loss for backprop

        # Inverse model: predict action
        inverse_input = torch.cat([state_features, next_state_features], dim=1)
        predicted_action_logits = self.inverse_model(inverse_input)
        inverse_loss = F.cross_entropy(predicted_action_logits, action)

        return intrinsic_reward, forward_loss, inverse_loss

    def compute_intrinsic_reward(
        self,
        state: torch.Tensor,
        action: torch.Tensor,
        next_state: torch.Tensor,
    ) -> torch.Tensor:
        """Compute only intrinsic reward (for inference)."""
        with torch.no_grad():
            intrinsic_reward, _, _ = self.forward(state, action, next_state)
        return intrinsic_reward
