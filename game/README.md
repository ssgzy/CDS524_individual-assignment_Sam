# Game 文件夹说明

本文件夹包含游戏环境的所有核心组件，实现了ShadowBox的游戏逻辑、渲染和关卡定义。

## 📁 文件结构

```
game/
├── __init__.py           # 包初始化文件
├── entities.py           # 游戏实体定义
├── environment.py        # 游戏环境（Gym-style API）
├── levels.py             # 关卡定义和加载
├── mechanics.py          # 游戏机制（传送门、压力板等）
├── renderer.py           # 旧的等距渲染器（已弃用）
├── renderer_2d.py        # 新的2D俯视图渲染器 ⭐
└── main.py               # 游戏主入口（可选）
```

## 📄 文件详解

### `entities.py` - 游戏实体定义
**功能**: 定义所有游戏对象的数据结构

**主要内容**:
- `BoxColor`: 箱子颜色枚举（红、蓝、绿、黄、紫）
- `Action`: 动作枚举（上、下、左、右、进入）
- `Player`: 玩家实体
- `Box`: 箱子实体
- `Target`: 目标点实体
- `PortalPair`: 传送门对
- `PressurePlate`: 压力板
- `Gate`: 机关门
- `LayerState`: 层级状态（支持嵌套关卡）

**地图代码**:
```python
EMPTY = 0              # 空地
WALL = 1               # 墙壁
PLAYER_START = 2       # 玩家起始位置
BOX_RED = 3            # 红色箱子
BOX_BLUE = 4           # 蓝色箱子
BOX_GREEN = 5          # 绿色箱子
BOX_YELLOW = 6         # 黄色箱子
TARGET_RED = 7         # 红色目标点
TARGET_BLUE = 8        # 蓝色目标点
TARGET_GREEN = 9       # 绿色目标点
TARGET_YELLOW = 10     # 黄色目标点
PORTAL_A1 = 11         # 传送门A入口
PORTAL_A2 = 12         # 传送门A出口
PORTAL_B1 = 13         # 传送门B入口
PORTAL_B2 = 14         # 传送门B出口
PRESSURE = 15          # 压力板
GATE = 16              # 机关门
SUBLEVEL_ENTRANCE = 17 # 子关卡入口
BOX_PURPLE = 18        # 紫色箱子
TARGET_PURPLE = 19     # 紫色目标点
```

**关键类**:
```python
@dataclass
class Player:
    x: int
    y: int

@dataclass
class Box:
    x: int
    y: int
    color: BoxColor

@dataclass
class LayerState:
    name: str
    width: int
    height: int
    static_map: List[List[int]]
    boxes: List[Box]
    targets: List[Target]
    # ... 其他属性
```

### `environment.py` - 游戏环境 ⭐ 核心
**功能**: 实现Gym-style的强化学习环境

**主要方法**:
- `reset()`: 重置环境到初始状态
- `step(action)`: 执行动作，返回(state, reward, done, info)
- `get_state()`: 获取当前状态向量（36维）
- `is_box_on_target(box)`: 检查箱子是否在目标上
- `check_win()`: 检查是否通关

**状态向量（36维）**:
```python
[
    当前层级 (1维),
    玩家位置 (2维: x, y),
    箱子信息 (15维: 5个箱子 × 3维[x, y, 是否在目标上]),
    目标点位置 (10维: 5个目标 × 2维[x, y]),
    机关门状态 (3维: 是否打开),
    压力板状态 (3维: 是否被压),
    子关卡完成 (1维),
    剩余步数 (1维)
]
```

**奖励函数**:
```python
箱子到达目标: +10.0
箱子离目标更近: +0.5
箱子离目标更远: -0.5
激活压力板: +5.0
打开机关门: +5.0
完成子关卡: +20.0
通关: +100.0
死锁: -50.0
无效动作: -0.1
超时: -10.0
```

**关键特性**:
- 支持多层嵌套关卡
- 自动死锁检测
- 传送门机制
- 压力板+机关门联动
- 完整的奖励塑形

### `levels.py` - 关卡定义
**功能**: 定义和加载5个关卡

**关卡列表**:
1. **Level 1**: 基础推箱子（1个箱子）
2. **Level 2**: 加入传送门（2个箱子）
3. **Level 3**: 压力板+机关门（2个箱子）
4. **Level 4**: 多机制组合（3个箱子）
5. **Level 5**: 嵌套子关卡（4个箱子）

**关卡结构**:
```python
@dataclass
class ParsedLevel:
    level_id: int
    layers: Dict[str, LayerState]  # 支持多层
    start_layer: str
    max_steps: int
```

**加载方法**:
```python
def load_level(level_id: int) -> ParsedLevel:
    # 返回指定关卡的完整定义
```

### `mechanics.py` - 游戏机制
**功能**: 实现特殊游戏机制

**主要函数**:
- `apply_portal(pos, portals)`: 处理传送门传送
- `update_pressure_plates(plates, boxes, player)`: 更新压力板状态
- `is_gate_blocking(gate, permanently_open)`: 检查门是否阻挡

**机制说明**:
```python
# 传送门
玩家或箱子进入传送门 → 传送到对应出口

# 压力板+门
箱子或玩家站在压力板上 → 对应的门打开
离开压力板 → 门关闭（除非永久打开）

# 子关卡
玩家在入口按Enter → 进入子关卡
完成子关卡 → 返回主关卡，门永久打开
```

### `renderer_2d.py` - 2D渲染器 ⭐ 推荐
**功能**: Patrick's Parabox风格的2D俯视图渲染

**主要类**:
```python
class TopDownRenderer:
    def __init__(self, screen, cell_size=64, ...)
    def render(self, env, extra_ui=None)
```

**渲染元素**:
- 清晰的2D网格
- 颜色对应的箱子和目标点
- 脉冲动画的目标点标记
- 箱子到位显示✓标记
- 完整的左侧UI面板
- 关卡进度条

**颜色方案**:
```python
COLOR_MAP = {
    BoxColor.RED: (255, 92, 92),
    BoxColor.BLUE: (92, 148, 252),
    BoxColor.GREEN: (92, 219, 149),
    BoxColor.YELLOW: (255, 215, 92),
    BoxColor.PURPLE: (198, 120, 255),
}
```

**特点**:
- ✅ 清晰的2D俯视图
- ✅ 现代简约设计
- ✅ 明确的视觉反馈
- ✅ 完整的UI信息

### `renderer.py` - 等距渲染器（已弃用）
**功能**: 旧的伪3D等距视角渲染器

**状态**: 已被`renderer_2d.py`替代

**问题**:
- ❌ 伪3D视角容易混淆
- ❌ 目标点不够明显
- ❌ 有"断层"感
- ❌ UI信息不完整

**保留原因**: 作为参考和对比

### `main.py` - 游戏主入口
**功能**: 独立游戏入口（可选）

**用途**:
- 快速测试游戏环境
- 不依赖训练脚本运行游戏

## 🎮 使用示例

### 创建环境
```python
from game.environment import ShadowBoxEnv

# 创建Level 1环境
env = ShadowBoxEnv(level_id=1)

# 重置环境
state = env.reset()

# 执行动作
action = 0  # UP
next_state, reward, done, info = env.step(action)

# 检查是否通关
if info.get("success"):
    print("通关！")
```

### 使用渲染器
```python
import pygame
from game.environment import ShadowBoxEnv
from game.renderer_2d import TopDownRenderer

pygame.init()
screen = pygame.display.set_mode((1280, 720))
env = ShadowBoxEnv(level_id=1)
renderer = TopDownRenderer(screen)

# 渲染当前状态
renderer.render(env, extra_ui={
    "Episode": "100",
    "Reward": "12.5"
})
```

### 加载关卡
```python
from game.levels import load_level

# 加载Level 3
level = load_level(3)
print(f"关卡ID: {level.level_id}")
print(f"最大步数: {level.max_steps}")
print(f"层级数: {len(level.layers)}")
```

## 🔧 可调参数

### 环境参数
```python
# environment.py
MAX_BOXES = 5          # 最大箱子数
MAX_GATES = 3          # 最大门数
MAX_PLATES = 3         # 最大压力板数
state_dim = 36         # 状态向量维度
action_space_size = 5  # 动作空间大小
```

### 渲染参数
```python
# renderer_2d.py
cell_size = 64         # 格子大小（像素）
screen_width = 1280    # 窗口宽度
screen_height = 720    # 窗口高度
ui_panel_width = 380   # UI面板宽度
```

### 关卡参数
```python
# levels.py
max_steps = 100-200    # 每关最大步数
map_width = 6-10       # 地图宽度
map_height = 6-10      # 地图高度
```

## 📊 性能考虑

### 环境性能
- 状态计算: O(n) where n = 箱子数
- 死锁检测: O(n²) 最坏情况
- 碰撞检测: O(1) 使用网格查找

### 渲染性能
- 2D渲染: ~60-120 FPS
- 等距渲染: ~30-60 FPS
- 建议: 训练时使用2D渲染器

## 🐛 调试技巧

### 打印状态
```python
env = ShadowBoxEnv(level_id=1)
state = env.reset()
print(f"状态向量: {state}")
print(f"玩家位置: ({env.player.x}, {env.player.y})")
print(f"箱子数量: {len(env.boxes)}")
```

### 可视化调试
```python
# 使用慢速渲染观察
python play.py --mode human --level 1 --fps 5
```

### 检查奖励
```python
env = ShadowBoxEnv(level_id=1)
env.reset()
state, reward, done, info = env.step(Action.RIGHT)
print(f"奖励: {reward}")
print(f"信息: {info}")
```

## 📚 相关文档

- `../docs/modules/game_environment.md` - 环境详细说明
- `../docs/modules/game_entities.md` - 实体详细说明
- `../docs/modules/game_levels.md` - 关卡详细说明
- `../docs/modules/game_renderer.md` - 渲染器详细说明
- `../NEW_RENDERER_GUIDE.md` - 新渲染器使用指南
- `../AI_LEARNING_MECHANISM.md` - AI学习机制说明

## 🎯 设计理念

### 模块化设计
- 实体、环境、渲染分离
- 易于扩展和修改
- 清晰的接口定义

### Gym-style API
- 标准的RL环境接口
- 兼容各种RL算法
- 易于集成和测试

### 奖励塑形
- 精心设计的奖励函数
- 引导AI学习
- 加速收敛

### 可视化优先
- 清晰的2D界面
- 完整的UI信息
- 易于观察和调试

## 🚀 扩展建议

### 添加新关卡
1. 在`levels.py`中定义新关卡
2. 设计地图布局
3. 配置箱子和目标点
4. 测试难度和可解性

### 添加新机制
1. 在`entities.py`中定义新实体
2. 在`mechanics.py`中实现逻辑
3. 在`environment.py`中集成
4. 在渲染器中添加可视化

### 优化性能
1. 使用numpy加速状态计算
2. 缓存常用计算结果
3. 优化死锁检测算法
4. 使用GPU加速渲染

## ✅ 测试清单

- [ ] 环境能正常创建和重置
- [ ] 所有动作都能正确执行
- [ ] 奖励函数计算正确
- [ ] 死锁检测工作正常
- [ ] 传送门功能正常
- [ ] 压力板+门联动正常
- [ ] 子关卡进入和退出正常
- [ ] 渲染器显示正确
- [ ] 通关判定正确

## 🎉 总结

game文件夹是整个项目的核心，实现了：
- ✅ 完整的游戏逻辑
- ✅ 标准的RL环境接口
- ✅ 精心设计的奖励函数
- ✅ 清晰的2D可视化
- ✅ 5个难度递增的关卡
- ✅ 多种游戏机制（传送门、压力板、嵌套关卡）

这些组件共同构成了一个高质量的强化学习训练环境！
