# 模块说明：`ai/replay_buffer.py`

## 1. 模块作用
实现 Prioritized Experience Replay（PER），让关键经验（如死锁、通关）被更高频采样。

## 2. 核心功能
- `push(...)`：存储经验与优先级
- `sample(batch_size, beta)`：按优先级概率采样并返回 IS 权重
- `update_priorities(indices, td_errors)`：按 TD 误差更新优先级

## 3. 使用到的知识点
- Experience Replay
- Prioritized Sampling
- Importance Sampling 修正偏差

## 4. 变量说明（可调性 + 意义）

| 变量 | 是否可调 | 意义 |
|---|---|---|
| `capacity=10000` | 可调 | 回放池容量 |
| `alpha=0.6` | 可调 | 优先级影响强度（0=均匀采样） |
| `beta=0.4` | 可调 | IS修正强度（训练后期可提高） |
| `priority` | 可调（策略级） | 单条经验采样优先级 |
| `buffer` | 运行时变量 | 实际经验存储队列 |
| `priorities` | 运行时变量 | 经验优先级队列 |
| `indices`（采样输出） | 运行时变量 | 用于回写优先级 |
| `weights`（采样输出） | 运行时变量 | 损失加权，减轻采样偏差 |

## 5. 与作业要求对应
- 提升学习效率，增强关键事件学习信号
- 属于 DQN 实现质量提升点
