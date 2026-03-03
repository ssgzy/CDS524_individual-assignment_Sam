# ShadowBox 报告模板（1000-1500字）

## 1. Introduction
- 研究背景：为什么 Sokoban 是高难强化学习问题
- 项目目标：解决多机制 ShadowBox 并达到高通关率

## 2. Game Design
- 规则与目标
- 状态空间与动作空间
- 关卡机制：传送门、压力板、机关门、子关卡

## 3. Q-Learning Implementation
- Dueling Double DQN 结构
- PER 与 epsilon-greedy
- 课程学习策略

## 4. Reward Function
- 各奖励项定义与设计动机
- 势能奖励（Reward Shaping）作用

## 5. Deadlock Detection
- 三类死锁定义
- 死锁检测对训练效率的影响

## 6. Evaluation
- 各关通关率、平均步数、死锁率
- 与 Random baseline 对比

## 7. Challenges & Solutions
- 稀疏奖励、复杂状态、探索困难等问题与解决策略

## 8. Conclusion
- 项目总结、局限性、未来改进方向

## 9. References
- 按课程要求列出论文与开源实现引用
