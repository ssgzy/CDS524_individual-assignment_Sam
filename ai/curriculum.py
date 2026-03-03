"""Curriculum scheduler for multi-level training."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CurriculumScheduler:
    current_level: int = 1
    max_level: int = 5
    upgrade_threshold: float = 0.70  # 降低到70%，更容易升级
    eval_window: int = 10  # 减少到10轮，更快响应
    max_episodes_per_level: Dict[int, int] = field(
        default_factory=lambda: {
            1: 200,   # 第1关最多200轮
            2: 400,   # 第2关最多400轮
            3: 600,   # 第3关最多600轮
            4: 800,   # 第4关最多800轮
            5: 5000,  # 第5关可以训练很久
        }
    )

    recent_results: List[bool] = field(default_factory=list)
    episodes_on_current_level: int = 0

    def record_episode(self, success: bool) -> bool:
        self.recent_results.append(success)
        self.episodes_on_current_level += 1

        if len(self.recent_results) > self.eval_window:
            self.recent_results.pop(0)

        should_upgrade = False

        if len(self.recent_results) == self.eval_window:
            win_rate = sum(self.recent_results) / self.eval_window
            if win_rate >= self.upgrade_threshold:
                should_upgrade = True

        max_ep = self.max_episodes_per_level.get(self.current_level, 2000)
        if self.episodes_on_current_level >= max_ep:
            should_upgrade = True

        if should_upgrade and self.current_level < self.max_level:
            self.current_level += 1
            self.recent_results = []
            self.episodes_on_current_level = 0
            return True

        return False

    def get_current_win_rate(self) -> float:
        if not self.recent_results:
            return 0.0
        return sum(self.recent_results) / len(self.recent_results)
