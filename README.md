# ShadowBox - CDS524 Assignment 1

强化学习推箱子游戏AI训练项目。

## 🎯 项目成果

### Level 2 - 完美表现 ⭐
- **成功率**: 100% (50/50测试)
- **平均步数**: 15步 (接近人类13步)
- **训练时间**: 6分钟 (1000轮)
- **模型**: `checkpoints_fixed/best_level2.pt`

### 训练优化
- **速度提升**: 3.7倍 (0.27 → 1.0 eps/s)
- **MPS GPU加速**: 成功应用
- **训练策略**: 每4步训练 + batch_size优化

### Level 3 - 挑战性分析
- **尝试**: 迁移学习 + 增强奖励函数
- **结果**: 详见 `FINAL_REPORT.md`
- **价值**: 深入的问题分析和策略设计

## 📁 项目结构

详细结构见 `PROJECT_STRUCTURE.md`

## 🚀 快速开始

### 观看AI演示
```bash
conda activate CDS524
python watch_game.py --level 2
```

### 评估模型
```bash
python evaluate_best.py
```

## 🔬 技术实现

- Rainbow DQN (Dueling + Double + PER + N-step + Noisy + Curiosity)
- MPS GPU加速
- 迁移学习
- 增强奖励函数

## 📊 训练结果

| 关卡 | 成功率 | 平均步数 |
|------|--------|----------|
| Level 2 | **100%** | 15步 |
| Level 3 | 0% | 见报告 |

## 📝 文档

- **FINAL_REPORT.md** - 完整报告
- **LEVEL3_ANALYSIS.md** - Level 3分析
- **PROJECT_STRUCTURE.md** - 项目结构

## 🎓 学术价值

展示了完整的RL实现、性能优化、问题分析和策略设计能力。

---
CDS524 Machine Learning for Business - 2026-03-03
