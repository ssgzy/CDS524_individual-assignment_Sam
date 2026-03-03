# Docs 文件夹说明

本文件夹包含项目的所有文档，包括模块说明、设计文档和汇报总结。

## 📁 文件结构

```
docs/
├── modules/                    # 模块级详细文档
│   ├── MODULE_INDEX.md        # 模块索引
│   ├── game_*.md              # 游戏模块文档
│   ├── ai_*.md                # AI模块文档
│   └── *_script.md            # 脚本文档
└── 最终汇报总结.md             # 项目汇报总结
```

## 📚 文档分类

### 🎮 游戏模块文档

#### `modules/game_entities.md`
**内容**: 游戏实体定义
- Player, Box, Target等实体类
- 地图代码定义
- 颜色枚举
- 数据结构说明

#### `modules/game_environment.md`
**内容**: 游戏环境实现
- Gym-style API
- 状态空间设计（36维）
- 动作空间设计（5个动作）
- 奖励函数详解
- step()和reset()方法

#### `modules/game_levels.md`
**内容**: 关卡定义
- 5个关卡的详细设计
- 地图布局
- 难度递增策略
- 关卡加载机制

#### `modules/game_mechanics.md`
**内容**: 游戏机制
- 传送门实现
- 压力板+机关门联动
- 子关卡进入/退出
- 碰撞检测

#### `modules/game_renderer.md`
**内容**: 渲染器实现
- 等距渲染器（旧）
- 2D渲染器（新）
- 渲染流程
- UI设计

#### `modules/game_main.md`
**内容**: 游戏主入口
- 独立运行方式
- 测试用途

### 🤖 AI模块文档

#### `modules/ai_dqn_model.md`
**内容**: DQN网络架构
- Dueling DQN结构
- 网络层设计
- 前向传播
- 参数说明

#### `modules/ai_agent.md`
**内容**: DQN Agent实现
- 训练算法
- 动作选择（epsilon-greedy）
- Double DQN更新
- 目标网络同步

#### `modules/ai_replay_buffer.md`
**内容**: 经验回放
- Prioritized Experience Replay
- 优先级计算
- 采样策略
- 重要性采样权重

#### `modules/ai_curriculum.md`
**内容**: 课程学习
- 关卡升级策略
- 胜率阈值
- 最大轮数配置
- 升级判断逻辑

#### `modules/ai_deadlock.md`
**内容**: 死锁检测
- 角落死锁
- 边缘死锁
- 冻结死锁
- 检测算法

### 📜 脚本文档

#### `modules/train_script.md`
**内容**: 训练脚本说明
- train.py功能
- 命令行参数
- 训练流程
- 输出文件

#### `modules/evaluate_script.md`
**内容**: 评估脚本说明
- evaluate.py功能
- 评估指标
- 使用方法

#### `modules/play_script.md`
**内容**: 演示脚本说明
- play.py功能
- 手动模式
- AI模式
- 控制方式

### 📊 汇报文档

#### `最终汇报总结.md`
**内容**: 项目汇报总结
- 项目目标与完成情况
- 与评分Rubric对照
- 关键技术亮点
- 主要知识点
- 超参数总览
- 文件结构与职责
- 运行与复现实验
- 汇报建议结构
- 已完成交付项清单

**用途**:
- 📝 撰写报告的参考
- 🎤 口头汇报的大纲
- ✅ 检查完成度
- 📊 展示项目成果

## 📖 文档特点

### 1. 模块级详细说明
每个模块文档都包含：
- **功能说明**: 模块的作用和目的
- **关键知识点**: 涉及的算法和概念
- **变量解释**: 参数是否可调及其意义
- **代码示例**: 使用方法
- **注意事项**: 常见问题和解决方案

### 2. 中文文档
- 所有文档都是中文
- 便于理解和学习
- 适合中文报告和汇报

### 3. 结构化组织
- 按模块分类
- 清晰的索引
- 便于查找

## 🔍 如何使用文档

### 场景1: 理解某个模块
```bash
# 想了解DQN网络
cat docs/modules/ai_dqn_model.md

# 想了解游戏环境
cat docs/modules/game_environment.md
```

### 场景2: 撰写报告
```bash
# 查看汇报总结
cat docs/最终汇报总结.md

# 参考模块文档
cat docs/modules/MODULE_INDEX.md
```

### 场景3: 调试问题
```bash
# 查看相关模块文档
# 例如：死锁检测不工作
cat docs/modules/ai_deadlock.md
```

### 场景4: 学习算法
```bash
# 学习DQN算法
cat docs/modules/ai_dqn_model.md
cat docs/modules/ai_agent.md
cat docs/modules/ai_replay_buffer.md
```

## 📝 文档索引

### 按功能分类

#### 游戏逻辑
- `game_entities.md` - 实体定义
- `game_environment.md` - 环境实现
- `game_levels.md` - 关卡设计
- `game_mechanics.md` - 游戏机制

#### AI算法
- `ai_dqn_model.md` - 网络架构
- `ai_agent.md` - 训练算法
- `ai_replay_buffer.md` - 经验回放
- `ai_curriculum.md` - 课程学习
- `ai_deadlock.md` - 死锁检测

#### 可视化
- `game_renderer.md` - 渲染器

#### 工具脚本
- `train_script.md` - 训练
- `evaluate_script.md` - 评估
- `play_script.md` - 演示

### 按重要性分类

#### 核心文档 ⭐⭐⭐
- `game_environment.md` - 游戏环境
- `ai_agent.md` - DQN Agent
- `最终汇报总结.md` - 项目总结

#### 重要文档 ⭐⭐
- `ai_dqn_model.md` - 网络架构
- `ai_curriculum.md` - 课程学习
- `game_levels.md` - 关卡设计
- `ai_deadlock.md` - 死锁检测

#### 参考文档 ⭐
- 其他模块文档

## 🎯 文档用途

### 1. 学习理解
- 理解项目架构
- 学习算法原理
- 掌握实现细节

### 2. 开发调试
- 查找API文档
- 理解参数含义
- 解决问题

### 3. 撰写报告
- 参考技术说明
- 提取关键信息
- 组织报告结构

### 4. 口头汇报
- 准备汇报大纲
- 理解技术要点
- 回答问题

## 📊 文档统计

| 类别 | 文件数 | 总字数（估计） |
|------|--------|----------------|
| 游戏模块 | 6个 | ~15000字 |
| AI模块 | 5个 | ~12000字 |
| 脚本模块 | 3个 | ~6000字 |
| 汇报文档 | 1个 | ~3000字 |
| **总计** | **15个** | **~36000字** |

## 🔧 文档维护

### 更新文档
```bash
# 编辑模块文档
nano docs/modules/ai_agent.md

# 更新汇报总结
nano docs/最终汇报总结.md
```

### 添加新文档
```bash
# 创建新模块文档
touch docs/modules/new_module.md

# 更新索引
nano docs/modules/MODULE_INDEX.md
```

### 文档格式
所有文档使用Markdown格式：
- 标题: `#`, `##`, `###`
- 列表: `-`, `1.`
- 代码: ` ``` `
- 强调: `**粗体**`, `*斜体*`

## 📚 相关文档（项目根目录）

### 设计文档
- `../ShadowBox_Game_Design.md` - 完整设计文档
- `../AI_LEARNING_MECHANISM.md` - AI学习机制

### 使用指南
- `../README.md` - 项目总览
- `../TRAINING_GUIDE.md` - 训练指南
- `../NEW_RENDERER_GUIDE.md` - 渲染器指南
- `../CURRICULUM_LEARNING_GUIDE.md` - 课程学习指南

### 问题修复
- `../CURRICULUM_FIX_SUMMARY.md` - 课程学习修复
- `../RENDERER_COMPARISON.md` - 渲染器对比
- `../ALL_FIXES_SUMMARY.md` - 所有修复总结

## 🎓 学习路径

### 初学者
1. 阅读 `最终汇报总结.md` 了解整体
2. 阅读 `game_environment.md` 理解环境
3. 阅读 `ai_agent.md` 理解算法
4. 阅读 `train_script.md` 学习训练

### 进阶者
1. 深入阅读所有AI模块文档
2. 理解算法细节和优化
3. 学习调参技巧
4. 尝试改进算法

### 研究者
1. 阅读完整设计文档
2. 理解架构设计决策
3. 分析性能瓶颈
4. 提出改进方案

## 🆘 常见问题

### Q: 文档太多，从哪里开始？
A: 先读 `MODULE_INDEX.md` 和 `最终汇报总结.md`

### Q: 想快速了解某个功能？
A: 查看对应的模块文档，每个文档都有"功能说明"部分

### Q: 文档和代码不一致？
A: 以代码为准，文档可能有滞后，欢迎更新

### Q: 如何生成PDF文档？
```bash
# 使用pandoc转换
pandoc docs/最终汇报总结.md -o report.pdf

# 或使用在线工具
# https://www.markdowntopdf.com/
```

## 🎉 总结

docs文件夹提供了完整的项目文档：
- ✅ 15个模块级详细文档
- ✅ 中文说明，易于理解
- ✅ 结构化组织，便于查找
- ✅ 涵盖所有核心功能
- ✅ 适合学习、开发和汇报

充分利用这些文档，可以更好地理解和使用ShadowBox项目！
