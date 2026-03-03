# 模块说明：`game/environment.py`

## 1. 模块作用
`environment.py` 是项目的核心 RL 环境，负责：
- 定义 `reset()/step()/get_state()` 交互接口
- 执行推箱子规则与特殊机制
- 计算奖励函数
- 输出终止状态（成功/死锁/超时）

## 2. 核心功能
- 36维状态向量构建
- 5动作离散动作空间（含 `ENTER`）
- 箱子推动、碰撞、传送、机关联动
- 子关卡切换与完成回调
- 奖励项：步惩罚、到位奖励、开门奖励、子关卡奖励、死锁惩罚、超时惩罚、势能奖励
- 死锁检测接入 `DeadlockDetector`

## 3. 使用到的知识点
- 强化学习环境设计（MDP：状态、动作、奖励、终止）
- Reward Shaping（势能奖励）
- 稀疏奖励问题缓解
- 层级任务（Hierarchical Tasks）

## 4. 关键类与方法
- `ShadowBoxEnv`：主环境类
- `load_level()`：切换关卡
- `reset()`：重置环境
- `step(action)`：执行一步
- `get_state()`：构造 36 维向量
- `calculate_reward()`：综合奖励计算
- `_check_terminal()`：成功/死锁/超时判断

## 5. 变量说明（可调性 + 意义）

### 5.1 常量与超参数

| 变量 | 是否可调 | 意义 |
|---|---|---|
| `MAX_BOXES=5` | 可调（需同步模型输入） | 状态向量中箱子槽位上限 |
| `MAX_GATES=3` | 可调（需同步模型输入） | 状态向量中门状态槽位上限 |
| `MAX_PLATES=3` | 可调（需同步模型输入） | 状态向量中压力板槽位上限 |
| `state_dim=36` | 可调（强相关） | DQN 输入维度，改动要同步网络结构 |
| `action_space_size=5` | 可调（强相关） | DQN 输出维度，改动要同步动作枚举 |

### 5.2 环境运行状态变量

| 变量 | 是否可调 | 意义 |
|---|---|---|
| `level_id` | 可调 | 当前关卡编号 |
| `current_layer_name` | 运行时变量 | 当前所在图层（`outer/sub1`） |
| `current_layer` | 运行时变量 | 层级编码（0/1） |
| `layer_stack` | 运行时变量 | 子关卡返回栈 |
| `sublevel_completed` | 运行时变量 | 是否完成子关卡 |
| `max_steps` | 关卡可调 | 本关最大步数上限 |
| `remaining_steps` | 运行时变量 | 剩余可行动步数 |
| `last_action_effective` | 运行时变量 | 动作是否有效，用于无效动作惩罚 |
| `permanently_open_gates` | 运行时变量 | 子关卡完成后永久开启的门集合 |

### 5.3 奖励项权重（最关键可调参数）

| 变量/规则 | 是否可调 | 意义 |
|---|---|---|
| `step penalty = -0.1` | 可调 | 鼓励短路径 |
| `newly placed box = +10` | 可调 | 强正反馈，推进主目标 |
| `newly removed box = -5` | 可调 | 惩罚错误回退 |
| `newly pressed plate = +3` | 可调 | 鼓励机关利用 |
| `newly opened gate = +5` | 可调 | 鼓励阶段性目标 |
| `sublevel complete = +20` | 可调 | 激励层级任务完成 |
| `level success = +100` | 可调 | 终局大奖励 |
| `deadlock = -50` | 可调 | 强惩罚不可逆错误 |
| `timeout = -20` | 可调 | 惩罚拖延 |
| `invalid action = -0.5` | 可调 | 抑制撞墙/乱推 |
| `potential weight = 0.5`（通过势函数实现） | 可调 | 引导箱子向目标移动，缓解稀疏奖励 |

## 6. 与作业要求对应
- 满足“状态空间、动作空间、奖励函数完整实现”
- UI/训练都通过统一环境接口调用
- 支持复杂机制与课程学习下的多关卡训练
