# play_progressive.py 使用说明

## ✅ 问题已修复

**问题**: `AttributeError: 'ShadowBoxEnv' object has no attribute 'step_count'`

**原因**: 游戏环境没有内置的step_count属性

**解决**: 在游戏类中添加了step_count跟踪器

## 🎮 使用方法

```bash
conda activate CDS524
python play_progressive.py
```

## 🕹️ 游戏特性

### 自动升级系统
- 从Level 1开始
- 完成当前关卡后自动升级到下一关
- 支持Level 1-5

### 控制方式

| 按键 | 功能 |
|------|------|
| ↑/W | 向上移动 |
| ↓/S | 向下移动 |
| ←/A | 向左移动 |
| →/D | 向右移动 |
| R | 重置当前关卡 |
| N | 跳到下一关 |
| P | 回到上一关 |
| H | 显示/隐藏帮助 |
| SPACE | 暂停/继续 |
| ESC | 退出游戏 |

### 游戏界面

**显示信息**:
- Level: 当前关卡/总关卡数
- Steps: 当前步数/最大步数
- Boxes: 已放置箱子数/总箱子数

**颜色说明**:
- 灰色方块: 墙壁
- 黄色方块: 目标位置
- 棕色方块: 未放置的箱子
- 绿色方块: 已放置在目标上的箱子
- 蓝色圆圈: 玩家

## 🎯 游戏目标

将所有箱子推到目标位置（黄色方块）上。

## 📝 注意事项

1. **箱子只能推，不能拉**
2. **不能同时推两个箱子**
3. **小心死锁** - 箱子推到角落可能无法移动
4. **步数限制** - 每关有最大步数限制

## 🏆 通关提示

### Level 1 (简单)
- 1个箱子
- 直接推到目标即可

### Level 2 (中等)
- 2个箱子
- 注意推箱子的顺序
- 有Gate和Pressure Plate机制

### Level 3 (困难)
- 3个箱子
- 有Portal传送门
- 需要规划路线

### Level 4-5 (挑战)
- 更复杂的机制
- 需要仔细思考

## 🐛 故障排除

### 如果游戏无法启动

1. 检查conda环境
```bash
conda activate CDS524
```

2. 检查依赖
```bash
pip install pygame numpy
```

3. 检查Python版本
```bash
python --version  # 应该是3.11+
```

### 如果画面显示不正常

- 尝试调整窗口大小
- 检查显示器分辨率

## 🎓 与AI对比

玩完游戏后，可以观看AI的表现：

```bash
# 观看Level 2 AI (100%成功率)
python watch_game.py --level 2

# 观看Level 3 AI (挑战性)
python watch_game.py --level 3
```

对比人类和AI的策略差异！

---
修复时间: 2026-03-03 09:10
