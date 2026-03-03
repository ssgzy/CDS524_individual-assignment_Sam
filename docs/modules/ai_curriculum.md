# 模块说明：`ai/curriculum.py`

## 1. 模块作用
管理课程学习（Curriculum Learning）流程：从简单关卡逐步升级到复杂关卡。

## 2. 核心功能
- 记录每局是否通关
- 在滑动窗口内统计通关率
- 达到阈值自动升级关卡
- 避免卡关：每关设置最大训练局数强制升级

## 3. 使用到的知识点
- Curriculum Learning
- 在线评估窗口（moving window）
- 自适应训练调度

## 4. 变量说明（可调性 + 意义）

| 变量 | 是否可调 | 意义 |
|---|---|---|
| `current_level` | 运行时变量 | 当前训练关卡 |
| `max_level=5` | 可调 | 最大关卡上限 |
| `upgrade_threshold=0.80` | 核心可调 | 升级所需通关率阈值 |
| `eval_window=20` | 核心可调 | 通关率统计窗口大小 |
| `max_episodes_per_level` | 可调 | 防止某关训练过久 |
| `recent_results` | 运行时变量 | 最近窗口内成功/失败记录 |
| `episodes_on_current_level` | 运行时变量 | 当前关卡已训练局数 |

## 5. 与作业要求对应
- 满足文档中的“课程学习策略”要求
- 支持跨关卡训练与报告中的难度递增分析
