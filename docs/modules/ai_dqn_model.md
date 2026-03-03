# 模块说明：`ai/dqn_model.py`

## 1. 模块作用
定义 Dueling DQN 神经网络，用于将 36 维状态映射到 5 个动作的 Q 值。

## 2. 核心功能
- 共享特征层 `feature_layer`
- 价值流 `value_stream` 估计 `V(s)`
- 优势流 `advantage_stream` 估计 `A(s,a)`
- 合并得到 `Q(s,a)=V(s)+A(s,a)-mean(A)`

## 3. 使用到的知识点
- 深度强化学习（DQN）
- Dueling Network 架构
- 全连接神经网络（MLP）

## 4. 变量说明（可调性 + 意义）

| 变量 | 是否可调 | 意义 |
|---|---|---|
| `state_dim=36` | 可调（需同步环境） | 输入维度，来自 `get_state()` |
| `action_dim=5` | 可调（需同步动作空间） | 输出动作Q值个数 |
| `Linear(36->256->128)` | 可调 | 共享特征提取容量 |
| `value_stream 128->64->1` | 可调 | 状态价值估计头 |
| `advantage_stream 128->64->action_dim` | 可调 | 动作优势估计头 |
| `ReLU` | 可调（可替换） | 非线性激活函数 |

## 5. 与作业要求对应
- 实现了 Q-learning 的深度近似模型
- 支持复杂状态空间下的策略学习
