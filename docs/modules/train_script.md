# 模块说明：`train.py`

## 1. 模块作用
`train.py` 是训练入口，整合环境、Agent、课程学习、模型保存和训练结果可视化。

## 2. 核心流程
1. 初始化随机种子
2. 创建环境与 DQN Agent
3. 按课程学习关卡训练
4. 每步交互并写入回放池
5. 调用 `train_step` 更新网络
6. 记录奖励/步数/通关率
7. 保存 checkpoint 与训练曲线

## 3. 使用到的知识点
- 端到端 RL 训练循环
- PER 优先级策略（通关/死锁样本加权）
- 训练过程可视化

## 4. 关键参数说明（可调性 + 意义）

| 参数 | 是否可调 | 意义 |
|---|---|---|
| `--episodes` | 核心可调 | 总训练局数 |
| `--seed` | 可调 | 随机种子，控制复现性 |
| `--resume` | 可调 | 断点恢复模型路径 |
| `--learning-rate` | 核心可调 | 学习率 |
| `--gamma` | 核心可调 | 折扣因子 |
| `--batch-size` | 可调 | 每次训练样本数 |
| `--buffer-capacity` | 可调 | 回放池容量 |
| `--target-update-freq` | 可调 | 目标网络更新频率 |
| `--grad-clip` | 可调 | 梯度裁剪阈值 |
| `--epsilon-start/end/decay` | 核心可调 | 探索-利用平衡策略 |
| `--per-alpha/beta` | 可调 | PER采样与偏差修正强度 |
| `--curriculum-threshold/window` | 核心可调 | 关卡升级判据 |
| `--checkpoint-dir` | 可调 | 模型保存目录 |
| `--results-dir` | 可调 | 图表与指标保存目录 |
| `--save-every` | 可调 | checkpoint 保存间隔 |
| `--log-interval` | 可调 | 控制日志打印频率 |

## 5. 输出文件
- `checkpoints/final_model.pth`
- `checkpoints/episode_*.pth`
- `results/training_results.png`
- `results/training_metrics.npz`

## 6. 与作业要求对应
- 满足“策略学习、参数控制、训练结果可视化、模型持久化”要求
