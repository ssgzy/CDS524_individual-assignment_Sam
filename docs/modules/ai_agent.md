# 模块说明：`ai/agent.py`

## 1. 模块作用
`agent.py` 封装 DQN Agent 的完整行为：动作选择、经验存储、网络训练、目标网络同步、模型保存加载。

## 2. 核心功能
- Epsilon-greedy 动作选择
- Double DQN 目标计算
- PER 加权 Huber 损失训练
- 梯度裁剪
- 目标网络定期硬更新

## 3. 使用到的知识点
- Q-learning with function approximation
- Double DQN（缓解Q值过估计）
- Dueling DQN（网络结构）
- PER + IS weight
- 梯度稳定化（clip grad）

## 4. 关键方法
- `select_action(state)`
- `train_step()`
- `decay_epsilon()`
- `save(path)` / `load(path)`

## 5. 变量说明（可调性 + 意义）

| 变量 | 是否可调 | 意义 |
|---|---|---|
| `lr=5e-4` | 核心可调 | 学习率 |
| `gamma=0.99` | 核心可调 | 折扣因子，平衡长期/短期奖励 |
| `batch_size=64` | 可调 | 每次训练采样量 |
| `buffer_capacity=10000` | 可调 | 回放池规模 |
| `epsilon_start=1.0` | 可调 | 初始探索率 |
| `epsilon_min=0.05` | 可调 | 最小探索率 |
| `epsilon_decay=0.995` | 可调 | 每局探索衰减 |
| `target_update_freq=500` | 可调 | 目标网络同步频率 |
| `per_alpha=0.6` | 可调 | PER优先级指数 |
| `per_beta=0.4` | 可调 | IS修正指数 |
| `grad_clip=1.0` | 可调 | 梯度裁剪阈值 |
| `device` | 自动选择 | CPU/GPU 运行设备 |
| `online_net` | 运行时对象 | 当前训练网络 |
| `target_net` | 运行时对象 | 计算TD目标的稳定网络 |
| `optimizer` | 可替换 | 参数优化器（当前 Adam） |
| `step_count` | 运行时变量 | 记录训练步数用于同步目标网络 |
| `action_dim` | 可调（需同步环境） | 动作数量 |

## 6. 与作业要求对应
- 满足“Q-learning算法实现、ε-greedy、学习率、折扣因子”评分点
- 包含可复现训练流程与模型持久化
