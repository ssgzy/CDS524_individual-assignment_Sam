"""Enhanced CNN-based DQN model with Noisy Networks."""

from __future__ import annotations

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class NoisyLinear(nn.Module):
    """Noisy Linear Layer for exploration (Fortunato et al., 2017)."""

    def __init__(self, in_features: int, out_features: int, sigma_init: float = 0.5):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.sigma_init = sigma_init

        # Learnable parameters
        self.weight_mu = nn.Parameter(torch.empty(out_features, in_features))
        self.weight_sigma = nn.Parameter(torch.empty(out_features, in_features))
        self.bias_mu = nn.Parameter(torch.empty(out_features))
        self.bias_sigma = nn.Parameter(torch.empty(out_features))

        # Factorized noise
        self.register_buffer('weight_epsilon', torch.empty(out_features, in_features))
        self.register_buffer('bias_epsilon', torch.empty(out_features))

        self.reset_parameters()
        self.reset_noise()

    def reset_parameters(self):
        mu_range = 1.0 / math.sqrt(self.in_features)
        self.weight_mu.data.uniform_(-mu_range, mu_range)
        self.weight_sigma.data.fill_(self.sigma_init / math.sqrt(self.in_features))
        self.bias_mu.data.uniform_(-mu_range, mu_range)
        self.bias_sigma.data.fill_(self.sigma_init / math.sqrt(self.out_features))

    def reset_noise(self):
        epsilon_in = self._scale_noise(self.in_features)
        epsilon_out = self._scale_noise(self.out_features)
        self.weight_epsilon.copy_(epsilon_out.outer(epsilon_in))
        self.bias_epsilon.copy_(epsilon_out)

    def _scale_noise(self, size: int) -> torch.Tensor:
        x = torch.randn(size, device=self.weight_mu.device)
        return x.sign().mul_(x.abs().sqrt_())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.training:
            weight = self.weight_mu + self.weight_sigma * self.weight_epsilon
            bias = self.bias_mu + self.bias_sigma * self.bias_epsilon
        else:
            weight = self.weight_mu
            bias = self.bias_mu
        return F.linear(x, weight, bias)


class CNNDQNNetwork(nn.Module):
    """CNN-based Dueling DQN with Noisy Networks."""

    def __init__(self, input_channels: int = 7, action_dim: int = 5, use_noisy: bool = True):
        super().__init__()
        self.use_noisy = use_noisy

        # CNN feature extractor
        self.conv_layers = nn.Sequential(
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(),
        )

        # Calculate conv output size (assuming 7x7 input)
        self.conv_output_size = 64 * 7 * 7  # 3136

        # Feature layer
        if use_noisy:
            self.feature_layer = nn.Sequential(
                NoisyLinear(self.conv_output_size, 512),
                nn.ReLU(),
            )

            # Dueling streams with Noisy layers
            self.value_stream = nn.Sequential(
                NoisyLinear(512, 256),
                nn.ReLU(),
                NoisyLinear(256, 1),
            )

            self.advantage_stream = nn.Sequential(
                NoisyLinear(512, 256),
                nn.ReLU(),
                NoisyLinear(256, action_dim),
            )
        else:
            self.feature_layer = nn.Sequential(
                nn.Linear(self.conv_output_size, 512),
                nn.ReLU(),
            )

            self.value_stream = nn.Sequential(
                nn.Linear(512, 256),
                nn.ReLU(),
                nn.Linear(256, 1),
            )

            self.advantage_stream = nn.Sequential(
                nn.Linear(512, 256),
                nn.ReLU(),
                nn.Linear(256, action_dim),
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch, channels, height, width)
        conv_out = self.conv_layers(x)
        conv_out = conv_out.view(conv_out.size(0), -1)  # Flatten

        features = self.feature_layer(conv_out)
        value = self.value_stream(features)
        advantage = self.advantage_stream(features)

        # Dueling aggregation
        q_values = value + advantage - advantage.mean(dim=1, keepdim=True)
        return q_values

    def reset_noise(self):
        """Reset noise for all NoisyLinear layers."""
        if self.use_noisy:
            for module in self.modules():
                if isinstance(module, NoisyLinear):
                    module.reset_noise()


class DQNNetwork(nn.Module):
    """Original FC-based Dueling DQN (fallback)."""

    def __init__(self, state_dim: int = 36, action_dim: int = 5):
        super().__init__()

        self.feature_layer = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
        )

        self.value_stream = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

        self.advantage_stream = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.feature_layer(x)
        value = self.value_stream(features)
        advantage = self.advantage_stream(features)
        return value + advantage - advantage.mean(dim=1, keepdim=True)
