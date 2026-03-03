# AI 文件夹说明

本文件夹包含所有深度强化学习算法的实现，包括DQN网络、Agent、经验回放、课程学习和死锁检测。

## 📁 文件结构

```
ai/
├── __init__.py          # 包初始化文件
├── dqn_model.py         # Dueling DQN网络架构
├── agent.py             # DQN Agent（训练和决策）
├── replay_buffer.py     # 优先经验回放（PER）
├── curriculum.py        # 课程学习调度器
└── deadlock.py          # 死锁检测算法
```

## 📄 文件详解

### `dqn_model.py` - Dueling DQN网络 ⭐
**功能**: 实现Dueling Double DQN神经网络架构

**网络结构**:
```python
输入层: 36维状态向量
  ↓
全连接层1: 128个神经元 + ReLU
  ↓
全连接层2: 128个神经元 + ReLU
  ↓
分流:
  ├─ Value Stream: 64 → 1 (状态价值V)
  └─ Advantage Stream: 64 → 5 (动作优势A)
  ↓
合并: Q(s,a) = V(s) + (A(s,a) - mean(A(s,·)))
  ↓
输出层: 5个Q值（对应5个动作）
```

**关键特性**:
- **Dueling架构**: 分离状态价值和动作优势
- **Double DQN**: 使用目标网络减少过估计
- **优势**: 更稳定的训练，更快的收敛

**代码示例**:
```python
class DuelingDQN(nn.Module):
    def __init__(self, state_dim=36, action_dim=5):
        # 共享层
        self.fc1 = nn.Linear(state_dim, 128)
        self.fc2 = nn.Linear(128, 128)

        # Value stream
        self.value_fc = nn.Linear(128, 64)
        self.value_out = nn.Linear(64, 1)

        # Advantage stream
        self.advantage_fc = nn.Linear(128, 64)
        self.advantage_out = nn.Linear(64, action_dim)
```

**参数**:
- `state_dim`: 状态维度（默认36）
- `action_dim`: 动作维度（默认5）
- 隐藏层大小: 128, 64
- 激活函数: ReLU

### `agent.py` - DQN Agent ⭐ 核心
**功能**: 实现完整的DQN训练和决策逻辑

**主要方法**:
```python
class DQNAgent:
    def __init__(self, state_dim, action_dim, lr, gamma, ...)
    def select_action(self, state)           # 选择动作（epsilon-greedy）
    def train_step(self)                     # 训练一步
    def decay_epsilon(self)                  # 衰减探索率
    def save(self, path)                     # 保存模型
    def load(self, path)                     # 加载模型
```

**核心算法**:
1. **Epsilon-Greedy策略**:
   ```python
   if random() < epsilon:
       action = random_action()  # 探索
   else:
       action = argmax(Q(state))  # 利用
   ```

2. **Double DQN更新**:
   ```python
   # 在线网络选择动作
   next_action = argmax(online_net(next_state))

   # 目标网络评估Q值
   target_q = reward + gamma * target_net(next_state)[next_action]

   # 更新在线网络
   loss = (Q(state, action) - target_q)²
   ```

3. **目标网络更新**:
   ```python
   # 每N步软更新
   if step % target_update_freq == 0:
       target_net.load_state_dict(online_net.state_dict())
   ```

**超参数**:
```python
learning_rate = 5e-4      # 学习率
gamma = 0.99              # 折扣因子
epsilon_start = 1.0       # 初始探索率
epsilon_min = 0.05        # 最小探索率
epsilon_decay = 0.995     # 探索率衰减
batch_size = 64           # 批次大小
target_update_freq = 500  # 目标网络更新频率
grad_clip = 1.0           # 梯度裁剪
```

**关键特性**:
- ✅ Epsilon-greedy探索策略
- ✅ Double DQN减少过估计
- ✅ 目标网络稳定训练
- ✅ 梯度裁剪防止爆炸
- ✅ 优先经验回放（PER）

### `replay_buffer.py` - 优先经验回放
**功能**: 实现Prioritized Experience Replay（PER）

**原理**:
```python
# 普通经验回放: 均匀采样
sample = random.choice(buffer)

# 优先经验回放: 按TD误差采样
priority = |TD_error| + ε
probability = priority^α / Σ(priority^α)
sample = weighted_choice(buffer, probability)
```

**主要方法**:
```python
class ReplayBuffer:
    def __init__(self, capacity, alpha=0.6):
        self.capacity = capacity  # 缓冲区容量
        self.alpha = alpha        # 优先级指数

    def push(self, state, action, reward, next_state, done, priority=1.0):
        # 添加经验，带优先级

    def sample(self, batch_size, beta=0.4):
        # 采样batch，返回(经验, 权重, 索引)

    def update_priorities(self, indices, priorities):
        # 更新优先级（基于TD误差）
```

**参数**:
- `capacity`: 缓冲区大小（默认10000）
- `alpha`: 优先级指数（0=均匀，1=完全优先）
- `beta`: 重要性采样权重（0.4→1.0）

**优势**:
- ✅ 更多采样重要经验
- ✅ 加速学习
- ✅ 提高样本效率

**使用示例**:
```python
buffer = ReplayBuffer(capacity=10000, alpha=0.6)

# 添加经验（高优先级）
buffer.push(state, action, reward, next_state, done, priority=5.0)

# 采样训练
batch, weights, indices = buffer.sample(batch_size=64, beta=0.4)

# 更新优先级
td_errors = compute_td_errors(batch)
buffer.update_priorities(indices, td_errors)
```

### `curriculum.py` - 课程学习调度器
**功能**: 实现从简单到困难的渐进式学习

**原理**:
```python
Level 1 (简单) → Level 2 (中等) → Level 3 (困难) → Level 4 (很难) → Level 5 (极难)
```

**升级条件**:
1. **达到胜率**: 最近N轮达到阈值胜率
2. **达到最大轮数**: 防止卡关太久

**主要方法**:
```python
class CurriculumScheduler:
    def __init__(self, current_level=1, max_level=5,
                 upgrade_threshold=0.7, eval_window=10):
        self.current_level = current_level
        self.upgrade_threshold = upgrade_threshold  # 70%胜率
        self.eval_window = eval_window              # 10轮窗口

    def record_episode(self, success):
        # 记录episode结果，判断是否升级
        # 返回True表示升级

    def get_current_win_rate(self):
        # 获取当前胜率
```

**升级策略**:
```python
# 条件1: 胜率达标
if win_rate >= 0.7 and episodes >= 10:
    upgrade_to_next_level()

# 条件2: 达到最大轮数
if episodes >= max_episodes_per_level[current_level]:
    upgrade_to_next_level()
```

**最大轮数配置**:
```python
max_episodes_per_level = {
    1: 200,   # Level 1最多200轮
    2: 400,   # Level 2最多400轮
    3: 600,   # Level 3最多600轮
    4: 800,   # Level 4最多800轮
    5: 5000,  # Level 5可以训练很久
}
```

**优势**:
- ✅ 从简单开始，逐步增加难度
- ✅ 避免一开始就面对困难任务
- ✅ 提高学习效率
- ✅ 更好的收敛性

### `deadlock.py` - 死锁检测
**功能**: 检测推箱子游戏中的无解状态

**死锁类型**:

1. **角落死锁（Corner Deadlock）**:
   ```
   ■ ■ ■
   ■ □ ·  ← 箱子在角落，无法推出
   ■ · ·
   ```

2. **边缘死锁（Edge Deadlock）**:
   ```
   ■ ■ ■ ■
   ■ □ □ ·  ← 两个箱子靠墙，无法推出
   · · · ·
   ```

3. **冻结死锁（Freeze Deadlock）**:
   ```
   · □ ·
   □ □ ·  ← 箱子相互阻挡，无法移动
   · □ ·
   ```

**主要方法**:
```python
class DeadlockDetector:
    def is_deadlock(self, env):
        # 检查是否死锁

    def is_corner_deadlock(self, box, env):
        # 检查角落死锁

    def is_edge_deadlock(self, boxes, env):
        # 检查边缘死锁

    def is_freeze_deadlock(self, boxes, env):
        # 检查冻结死锁
```

**检测逻辑**:
```python
def is_deadlock(self, env):
    for box in env.boxes:
        if box.pos in target_positions:
            continue  # 已在目标上，跳过

        # 检查角落死锁
        if is_corner_deadlock(box):
            return True

    # 检查边缘和冻结死锁
    if is_edge_deadlock(boxes) or is_freeze_deadlock(boxes):
        return True

    return False
```

**优势**:
- ✅ 提前终止无解状态
- ✅ 节省训练时间
- ✅ 避免AI学习错误策略
- ✅ 提供负反馈（-50.0奖励）

## 🎓 算法原理

### DQN（Deep Q-Network）
```
Q-Learning: Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
                                    a'

DQN: 用神经网络近似Q函数
     Q(s,a) ≈ Neural_Network(s)[a]
```

### Double DQN
```
普通DQN: target = r + γ max Q_target(s',a')
                        a'

Double DQN: target = r + γ Q_target(s', argmax Q_online(s',a'))
                                          a'

优势: 减少Q值过估计
```

### Dueling DQN
```
普通DQN: Q(s,a) = Network(s)[a]

Dueling DQN: Q(s,a) = V(s) + A(s,a) - mean(A(s,·))
                      ↑      ↑
                   状态价值  动作优势

优势: 更好地评估状态价值
```

### Prioritized Experience Replay
```
普通回放: P(i) = 1/N  (均匀采样)

PER: P(i) = p_i^α / Σ p_j^α
     p_i = |TD_error_i| + ε

优势: 更多采样重要经验
```

## 🔧 可调参数

### Agent参数
```python
learning_rate = 5e-4      # 学习率（可调：1e-5 ~ 1e-3）
gamma = 0.99              # 折扣因子（可调：0.95 ~ 0.99）
epsilon_start = 1.0       # 初始探索率（固定）
epsilon_min = 0.05        # 最小探索率（可调：0.01 ~ 0.1）
epsilon_decay = 0.995     # 探索率衰减（可调：0.99 ~ 0.999）
batch_size = 64           # 批次大小（可调：32 ~ 128）
target_update_freq = 500  # 目标网络更新频率（可调：100 ~ 1000）
grad_clip = 1.0           # 梯度裁剪（可调：0.5 ~ 2.0）
```

### 经验回放参数
```python
buffer_capacity = 10000   # 缓冲区大小（可调：5000 ~ 50000）
per_alpha = 0.6           # 优先级指数（可调：0.4 ~ 0.8）
per_beta = 0.4            # 重要性采样（可调：0.4 ~ 1.0）
```

### 课程学习参数
```python
upgrade_threshold = 0.7   # 胜率阈值（可调：0.5 ~ 0.9）
eval_window = 10          # 评估窗口（可调：5 ~ 20）
max_episodes = {          # 最大轮数（可调）
    1: 200,
    2: 400,
    3: 600,
    4: 800,
    5: 5000,
}
```

## 📊 训练流程

```python
# 1. 初始化
agent = DQNAgent(state_dim=36, action_dim=5)
buffer = ReplayBuffer(capacity=10000)
scheduler = CurriculumScheduler()

# 2. 训练循环
for episode in range(10000):
    # 加载当前关卡
    env.load_level(scheduler.current_level)
    state = env.reset()

    while not done:
        # 选择动作
        action = agent.select_action(state)

        # 执行动作
        next_state, reward, done, info = env.step(action)

        # 存储经验
        buffer.push(state, action, reward, next_state, done)

        # 训练
        agent.train_step()

        state = next_state

    # 衰减探索率
    agent.decay_epsilon()

    # 记录结果，判断是否升级
    upgraded = scheduler.record_episode(success)
    if upgraded:
        print(f"🎉 LEVEL UP! {scheduler.current_level-1} → {scheduler.current_level}")
```

## 🐛 调试技巧

### 查看Q值
```python
agent = DQNAgent(state_dim=36, action_dim=5)
state = env.get_state()
q_values = agent.policy_net(torch.FloatTensor(state))
print(f"Q值: {q_values}")
print(f"最佳动作: {q_values.argmax()}")
```

### 监控训练
```python
# 打印训练信息
print(f"Episode {episode}")
print(f"Epsilon: {agent.epsilon:.3f}")
print(f"Buffer size: {len(agent.replay_buffer)}")
print(f"Loss: {loss:.4f}")
```

### 可视化Q值
```python
import matplotlib.pyplot as plt

q_values_history = []
for episode in range(1000):
    # ... 训练 ...
    q_values_history.append(agent.policy_net(state).max().item())

plt.plot(q_values_history)
plt.title("Max Q-value over time")
plt.show()
```

## 📚 相关文档

- `../docs/modules/ai_dqn_model.md` - DQN网络详细说明
- `../docs/modules/ai_agent.md` - Agent详细说明
- `../docs/modules/ai_replay_buffer.md` - 经验回放详细说明
- `../docs/modules/ai_curriculum.md` - 课程学习详细说明
- `../docs/modules/ai_deadlock.md` - 死锁检测详细说明
- `../CURRICULUM_LEARNING_GUIDE.md` - 课程学习使用指南
- `../AI_LEARNING_MECHANISM.md` - AI学习机制说明

## 🎯 设计理念

### 稳定性优先
- Double DQN减少过估计
- 目标网络稳定训练
- 梯度裁剪防止爆炸

### 效率优化
- 优先经验回放
- 课程学习策略
- 死锁提前检测

### 可扩展性
- 模块化设计
- 清晰的接口
- 易于调整参数

## 🚀 性能优化建议

### 加速训练
1. 增大batch_size（64 → 128）
2. 减小buffer_capacity（10000 → 5000）
3. 增大target_update_freq（500 → 1000）

### 提高质量
1. 增大buffer_capacity（10000 → 50000）
2. 减小learning_rate（5e-4 → 1e-4）
3. 增大eval_window（10 → 20）

### 平衡两者
使用当前默认参数（已优化）

## ✅ 测试清单

- [ ] Agent能正常创建和初始化
- [ ] 能正确选择动作（epsilon-greedy）
- [ ] 训练步骤正常执行
- [ ] 探索率正常衰减
- [ ] 模型能保存和加载
- [ ] 经验回放正常工作
- [ ] 优先级采样正确
- [ ] 课程学习能正常升级
- [ ] 死锁检测准确

## 🎉 总结

ai文件夹实现了完整的DQN算法栈：
- ✅ Dueling Double DQN网络
- ✅ 完整的训练和决策逻辑
- ✅ 优先经验回放（PER）
- ✅ 课程学习策略
- ✅ 死锁检测机制

这些组件共同构成了一个高效、稳定的强化学习训练系统！
