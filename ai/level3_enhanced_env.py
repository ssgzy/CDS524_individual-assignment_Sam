"""改进的Level 3环境 - 添加Portal引导奖励"""
from __future__ import annotations
from typing import Tuple, Dict
import numpy as np
from game.environment import ShadowBoxEnv

class Level3EnhancedEnv:
    """
    Level 3增强环境 - 针对Portal机制的特殊奖励设计

    关键改进:
    1. Portal使用奖励 - 鼓励探索传送门
    2. 箱子-目标距离奖励 - 引导箱子朝目标移动
    3. 探索奖励 - 鼓励访问新位置
    4. 防止重复动作惩罚 - 避免陷入循环
    """

    def __init__(self, level_id: int = 3, local_view_size: int = 7):
        self.env = ShadowBoxEnv(level_id=level_id)
        self.local_view_size = local_view_size
        self.action_space_size = self.env.action_space_size

        # 跟踪状态用于奖励计算
        self.prev_boxes_on_target = 0
        self.prev_box_distances = []
        self.visited_positions = set()
        self.last_actions = []  # 记录最近的动作
        self.portal_used_count = 0
        self.prev_player_pos = None

    def reset(self) -> np.ndarray:
        """重置环境"""
        self.env.reset()
        self.prev_boxes_on_target = sum(1 for box in self.env.boxes if self.env.is_box_on_target(box))
        self.prev_box_distances = self._compute_box_target_distances()
        self.visited_positions = {self.env.player.pos}
        self.last_actions = []
        self.portal_used_count = 0
        self.prev_player_pos = self.env.player.pos
        return self._get_cnn_state()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """执行动作并返回增强的奖励"""
        prev_player_pos = self.env.player.pos

        # 执行动作
        _, base_reward, done, info = self.env.step(action)
        next_state = self._get_cnn_state()

        # === 增强奖励函数 ===
        reward = 0.0

        # 1. 基础步数惩罚（鼓励效率）
        reward -= 0.1

        # 2. 箱子放置奖励（最重要）
        curr_boxes_on_target = sum(1 for box in self.env.boxes if self.env.is_box_on_target(box))
        if curr_boxes_on_target > self.prev_boxes_on_target:
            reward += 100.0  # 巨大奖励
            print(f"  ✅ 箱子放置成功! 奖励: +100")
        elif curr_boxes_on_target < self.prev_boxes_on_target:
            reward -= 50.0  # 严重惩罚
        self.prev_boxes_on_target = curr_boxes_on_target

        # 3. 成功奖励
        if info.get('success'):
            reward += 200.0
            print(f"  🎉 关卡完成! 总奖励: +200")

        # 4. 失败惩罚
        if info.get('deadlock'):
            reward -= 50.0
        if info.get('timeout'):
            reward -= 20.0

        # 5. Portal使用奖励（关键！）
        curr_player_pos = self.env.player.pos
        if self._player_used_portal(prev_player_pos, curr_player_pos):
            reward += 20.0  # 鼓励使用portal
            self.portal_used_count += 1
            print(f"  🌀 使用Portal! 奖励: +20 (总计: {self.portal_used_count}次)")

        # 6. 箱子-目标距离改进奖励
        curr_distances = self._compute_box_target_distances()
        if self.prev_box_distances and curr_distances:
            distance_improvement = sum(self.prev_box_distances) - sum(curr_distances)
            if distance_improvement > 0:
                reward += 2.0 * distance_improvement  # 箱子靠近目标
            elif distance_improvement < 0:
                reward += 0.5 * distance_improvement  # 箱子远离目标（小惩罚）
        self.prev_box_distances = curr_distances

        # 7. 探索奖励（鼓励访问新位置）
        if curr_player_pos not in self.visited_positions:
            reward += 1.0
            self.visited_positions.add(curr_player_pos)

        # 8. 防止重复动作循环
        self.last_actions.append(action)
        if len(self.last_actions) > 10:
            self.last_actions.pop(0)
            # 检查是否在重复同一个动作
            if len(set(self.last_actions[-5:])) == 1:  # 最近5步都是同一动作
                reward -= 5.0  # 惩罚重复

        self.prev_player_pos = curr_player_pos

        return next_state, reward, done, info

    def _player_used_portal(self, prev_pos, curr_pos) -> bool:
        """检测玩家是否使用了portal（位置跳跃）"""
        if not self.env.portals:
            return False

        # 计算曼哈顿距离
        distance = abs(curr_pos[0] - prev_pos[0]) + abs(curr_pos[1] - prev_pos[1])

        # 如果距离大于1，说明使用了portal
        return distance > 1

    def _compute_box_target_distances(self) -> list:
        """计算每个箱子到最近目标的距离"""
        if not self.env.boxes or not self.env.targets:
            return []

        distances = []
        for box in self.env.boxes:
            min_dist = min(
                abs(box.pos[0] - target.pos[0]) + abs(box.pos[1] - target.pos[1])
                for target in self.env.targets
            )
            distances.append(min_dist)

        return distances

    def _get_cnn_state(self) -> np.ndarray:
        """获取CNN状态表示"""
        size = self.local_view_size
        half_size = size // 2

        # 初始化7个通道
        state = np.zeros((7, size, size), dtype=np.float32)

        px, py = self.env.player.pos

        for dy in range(-half_size, half_size + 1):
            for dx in range(-half_size, half_size + 1):
                world_x = px + dx
                world_y = py + dy
                local_x = dx + half_size
                local_y = dy + half_size

                # 边界外 = 墙
                if not self.env.in_bounds((world_x, world_y)):
                    state[0, local_y, local_x] = 1.0
                    continue

                # 墙
                if self.env.is_wall((world_x, world_y)):
                    state[0, local_y, local_x] = 1.0

                # 箱子
                box = self.env.get_box_at((world_x, world_y))
                if box:
                    if self.env.is_box_on_target(box):
                        state[1, local_y, local_x] = 2.0  # 在目标上的箱子
                    else:
                        state[1, local_y, local_x] = 1.0  # 普通箱子

                # 目标
                for target in self.env.targets:
                    if target.pos == (world_x, world_y):
                        state[2, local_y, local_x] = 1.0

                # Portal（重要！）
                for portal in self.env.portals:
                    if hasattr(portal, 'entrance') and portal.entrance == (world_x, world_y):
                        state[6, local_y, local_x] = 1.0  # 入口
                    elif hasattr(portal, 'exit') and portal.exit == (world_x, world_y):
                        state[6, local_y, local_x] = 0.5  # 出口

        # 玩家（中心）
        state[3, half_size, half_size] = 1.0

        return state

    def load_level(self, level_id: int):
        """加载关卡"""
        self.env.load_level(level_id)

    def close(self):
        """关闭环境"""
        self.env.close()

    @property
    def level_id(self):
        return self.env.level_id

    @property
    def max_steps(self):
        return self.env.max_steps
