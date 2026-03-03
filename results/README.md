# Results 文件夹说明

本文件夹存储所有训练结果，包括图表、指标数据和详细日志。

## 📁 文件结构

训练完成后，本文件夹将包含以下文件：

```
results/
├── training_results.png      # 训练结果可视化图表
├── training_metrics.npz       # NumPy格式的指标数据
├── training_log.json          # 详细的训练日志（JSON格式）
└── episode_details.json       # 每个episode的详细记录
```

## 📄 文件说明

### `training_results.png` - 训练结果图表 ⭐
**格式**: PNG图片（1400×1000像素，150 DPI）

**内容**: 4个子图展示训练过程

#### 子图1: Episode Reward (Moving Average)
- **横轴**: Episode编号
- **纵轴**: 总奖励
- **内容**: 奖励的移动平均（窗口=100）
- **用途**: 观察训练趋势，判断是否收敛

**理想曲线**:
```
奖励
 ↑
 |     ╱────────  (收敛)
 |   ╱
 | ╱
 |╱
 └──────────────→ Episode
```

#### 子图2: Episode Steps (Moving Average)
- **横轴**: Episode编号
- **纵轴**: 步数
- **内容**: 步数的移动平均（窗口=100）
- **用途**: 观察AI效率，步数减少说明策略优化

**理想曲线**:
```
步数
 ↑
 |\
 | \
 |  \
 |   ────────  (稳定)
 └──────────────→ Episode
```

#### 子图3: Win Rate by Level
- **横轴**: 关卡编号（1-5）
- **纵轴**: 胜率（0-1）
- **内容**: 每个关卡的平均胜率
- **颜色**: 绿色(≥80%) / 橙色(<80%)
- **用途**: 评估每个关卡的掌握程度

**理想结果**:
```
胜率
1.0 ┤ ██ ██ ██ ██ ██  (全部≥80%)
0.8 ┤ ██ ██ ██ ██ ██
0.6 ┤ ██ ██ ██ ██ ██
0.4 ┤ ██ ██ ██ ██ ██
0.2 ┤ ██ ██ ██ ██ ██
0.0 └─────────────────
     L1 L2 L3 L4 L5
```

#### 子图4: Epsilon Decay Curve
- **横轴**: Episode编号
- **纵轴**: Epsilon值（探索率）
- **内容**: Epsilon的衰减曲线
- **用途**: 验证探索-利用平衡

**理想曲线**:
```
Epsilon
1.0 ┤\
0.8 ┤ \
0.6 ┤  \
0.4 ┤   \
0.2 ┤    ────────  (稳定在0.05)
0.0 └──────────────→ Episode
```

### `training_metrics.npz` - NumPy指标数据
**格式**: NumPy压缩文件

**内容**:
```python
{
    'rewards': np.array([...]),  # 每个episode的总奖励
    'steps': np.array([...]),    # 每个episode的步数
}
```

**使用方法**:
```python
import numpy as np

# 加载数据
data = np.load('results/training_metrics.npz')
rewards = data['rewards']
steps = data['steps']

# 分析
print(f"平均奖励: {rewards.mean():.2f}")
print(f"最大奖励: {rewards.max():.2f}")
print(f"平均步数: {steps.mean():.2f}")

# 绘图
import matplotlib.pyplot as plt
plt.plot(rewards)
plt.title("Training Rewards")
plt.show()
```

### `training_log.json` - 详细训练日志 ⭐ 新增
**格式**: JSON文件

**内容**: 完整的训练统计信息

```json
{
  "total_episodes": 10000,
  "final_epsilon": 0.05,
  "curriculum_final_level": 5,
  "win_rates_by_level": {
    "1": {
      "total_episodes": 150,
      "win_rate": 0.85,
      "total_wins": 128
    },
    "2": {
      "total_episodes": 300,
      "win_rate": 0.78,
      "total_wins": 234
    },
    ...
  },
  "final_stats": {
    "avg_reward_last_100": 45.67,
    "avg_steps_last_100": 78.5,
    "max_reward": 120.0,
    "min_reward": -50.0
  },
  "hyperparameters": {
    "learning_rate": 0.0005,
    "gamma": 0.99,
    "batch_size": 64,
    ...
  }
}
```

**用途**:
- 📊 快速查看训练结果
- 🔍 分析每个关卡的表现
- ⚙️ 记录超参数配置
- 📝 生成报告

**使用方法**:
```python
import json

# 加载日志
with open('results/training_log.json', 'r') as f:
    log = json.load(f)

# 查看统计
print(f"总轮数: {log['total_episodes']}")
print(f"最终关卡: {log['curriculum_final_level']}")

# 查看各关卡胜率
for level, stats in log['win_rates_by_level'].items():
    print(f"Level {level}: {stats['win_rate']:.1%}")
```

### `episode_details.json` - Episode详细记录 ⭐ 新增
**格式**: JSON文件

**内容**: 每个episode的详细数据

```json
[
  {
    "episode": 1,
    "reward": -15.5,
    "steps": 100
  },
  {
    "episode": 2,
    "reward": -8.3,
    "steps": 95
  },
  ...
]
```

**用途**:
- 📈 绘制自定义图表
- 🔬 详细分析训练过程
- 📊 导出到Excel/CSV
- 🎯 定位问题episode

**使用方法**:
```python
import json
import pandas as pd

# 加载详细记录
with open('results/episode_details.json', 'r') as f:
    details = json.load(f)

# 转换为DataFrame
df = pd.DataFrame(details)

# 分析
print(df.describe())

# 找出最佳episode
best_episode = df.loc[df['reward'].idxmax()]
print(f"最佳Episode: {best_episode['episode']}")
print(f"奖励: {best_episode['reward']}")

# 导出CSV
df.to_csv('results/training_details.csv', index=False)
```

## 📊 数据分析示例

### 1. 计算学习曲线
```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
data = np.load('results/training_metrics.npz')
rewards = data['rewards']

# 计算移动平均
window = 100
moving_avg = np.convolve(rewards, np.ones(window)/window, mode='valid')

# 绘图
plt.figure(figsize=(10, 6))
plt.plot(moving_avg)
plt.title('Learning Curve')
plt.xlabel('Episode')
plt.ylabel('Average Reward')
plt.grid(True)
plt.savefig('results/learning_curve.png')
```

### 2. 分析关卡表现
```python
import json

with open('results/training_log.json', 'r') as f:
    log = json.load(f)

# 打印关卡统计
print("关卡表现分析:")
print("-" * 50)
for level, stats in sorted(log['win_rates_by_level'].items()):
    print(f"Level {level}:")
    print(f"  训练轮数: {stats['total_episodes']}")
    print(f"  胜率: {stats['win_rate']:.1%}")
    print(f"  通关次数: {stats['total_wins']}")
    print()
```

### 3. 对比不同训练
```python
import json
import matplotlib.pyplot as plt

# 加载多次训练的日志
logs = []
for i in range(1, 4):
    with open(f'results/training_log_{i}.json', 'r') as f:
        logs.append(json.load(f))

# 对比胜率
levels = range(1, 6)
for i, log in enumerate(logs):
    win_rates = [log['win_rates_by_level'][str(l)]['win_rate']
                 for l in levels]
    plt.plot(levels, win_rates, label=f'Training {i+1}')

plt.xlabel('Level')
plt.ylabel('Win Rate')
plt.legend()
plt.grid(True)
plt.savefig('results/comparison.png')
```

## 📈 预期结果

### 成功训练的标志

#### 奖励曲线
- ✅ 整体上升趋势
- ✅ 最终收敛到正值
- ✅ 波动逐渐减小

#### 步数曲线
- ✅ 整体下降趋势
- ✅ 最终稳定在较低值
- ✅ 说明策略优化

#### 关卡胜率
- ✅ Level 1-3: ≥80%
- ✅ Level 4: ≥70%
- ✅ Level 5: ≥60%

#### Epsilon衰减
- ✅ 从1.0平滑衰减到0.05
- ✅ 符合指数衰减曲线

### 问题诊断

#### 奖励不收敛
```
可能原因:
- 学习率太高
- Gamma设置不当
- 奖励函数设计问题

解决方案:
- 降低learning_rate
- 调整gamma
- 检查奖励函数
```

#### 步数不减少
```
可能原因:
- 探索率衰减太慢
- 训练轮数不够
- 死锁检测失效

解决方案:
- 增大epsilon_decay
- 增加训练轮数
- 检查死锁检测
```

#### 关卡胜率低
```
可能原因:
- 升级阈值太低
- 训练时间不足
- 关卡太难

解决方案:
- 提高curriculum_threshold
- 增加max_episodes_per_level
- 简化关卡设计
```

## 🔧 自定义分析

### 创建自定义图表
```python
import json
import matplotlib.pyplot as plt
import numpy as np

# 加载数据
with open('results/training_log.json', 'r') as f:
    log = json.load(f)

with open('results/episode_details.json', 'r') as f:
    details = json.load(f)

# 自定义分析
# ... 你的代码 ...

# 保存图表
plt.savefig('results/custom_analysis.png', dpi=150)
```

### 导出报告
```python
import json

with open('results/training_log.json', 'r') as f:
    log = json.load(f)

# 生成Markdown报告
report = f"""
# 训练报告

## 基本信息
- 总轮数: {log['total_episodes']}
- 最终关卡: {log['curriculum_final_level']}
- 最终Epsilon: {log['final_epsilon']:.3f}

## 关卡表现
"""

for level, stats in sorted(log['win_rates_by_level'].items()):
    report += f"\n### Level {level}\n"
    report += f"- 训练轮数: {stats['total_episodes']}\n"
    report += f"- 胜率: {stats['win_rate']:.1%}\n"
    report += f"- 通关次数: {stats['total_wins']}\n"

with open('results/REPORT.md', 'w') as f:
    f.write(report)
```

## 📝 注意事项

1. **文件覆盖**: 每次训练会覆盖之前的结果，建议备份重要数据
2. **磁盘空间**: episode_details.json可能较大（10000轮≈1MB）
3. **JSON格式**: 可以用任何文本编辑器查看
4. **NumPy数据**: 需要Python环境加载

## 🆘 常见问题

### Q: 没有生成结果文件？
A: 确保训练完成，检查results目录权限

### Q: 图表显示不正常？
A: 可能是数据不足，至少需要100轮训练

### Q: JSON文件太大？
A: 可以删除episode_details.json，只保留汇总数据

### Q: 如何对比多次训练？
A: 重命名结果文件，如training_log_1.json, training_log_2.json

## 📚 相关文档

- `../TRAINING_GUIDE.md` - 训练指南
- `../CURRICULUM_LEARNING_GUIDE.md` - 课程学习说明
- `../scripts/README.md` - 训练脚本说明

## 🎯 使用建议

### 训练中
- 定期检查training_results.png
- 观察奖励曲线是否上升
- 确认关卡能正常升级

### 训练后
- 查看training_log.json了解整体表现
- 分析episode_details.json找出问题
- 使用数据生成报告

### 调试时
- 对比不同超参数的结果
- 找出最佳配置
- 记录实验结果

## 🚀 快速开始

```bash
# 1. 运行训练
cd scripts
./train_with_viz.sh

# 2. 训练完成后，查看结果
cd ../results
ls -lh

# 3. 查看图表
open training_results.png

# 4. 查看日志
cat training_log.json | python -m json.tool

# 5. 分析数据
python
>>> import numpy as np
>>> data = np.load('training_metrics.npz')
>>> print(f"平均奖励: {data['rewards'].mean():.2f}")
```

## 🎉 总结

results文件夹提供了完整的训练结果记录：
- ✅ 可视化图表（PNG）
- ✅ 原始数据（NPZ）
- ✅ 详细日志（JSON）
- ✅ Episode记录（JSON）

这些数据可以用于：
- 📊 评估训练效果
- 🔍 分析问题原因
- 📝 撰写报告
- 🎯 优化超参数

充分利用这些数据，可以更好地理解和改进你的强化学习模型！
