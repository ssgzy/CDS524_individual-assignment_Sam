# 模块说明：`game/entities.py`

## 1. 模块作用
`entities.py` 定义了 ShadowBox 的基础数据结构和地图编码常量，是环境、渲染器、关卡加载器共同依赖的底层模块。

## 2. 核心功能
- 定义动作空间 `Action`（上、下、左、右、ENTER）
- 定义颜色枚举 `BoxColor`
- 定义地图元素编码（墙、箱子、目标点、传送门、机关等）
- 定义实体数据类：`Player`、`Box`、`Target`、`PortalPair`、`PressurePlate`、`Gate`
- 定义图层状态 `LayerState`，支持外层/子层地图

## 3. 使用到的知识点
- 面向对象建模（实体类）
- `dataclass`（降低模板代码）
- 枚举类型（动作/颜色离散化）
- 强化学习环境中的“状态结构化表示”

## 4. 关键类与函数
- `Action(IntEnum)`：离散动作编号，直接对应 DQN 输出维度
- `LayerState`：单层地图的静态与动态信息容器
- `LayerState.clone_dynamic()`：重置时复制动态对象，避免污染模板

## 5. 变量说明（可调性 + 意义）

| 变量 | 是否可调 | 意义 |
|---|---|---|
| `BoxColor` 枚举项 | 可扩展 | 支持颜色匹配机制；新增颜色需同步关卡和渲染 |
| `Action` 枚举项 | 可调（谨慎） | 定义动作空间大小与语义；改动后需同步 `action_dim` |
| `EMPTY~TARGET_PURPLE` 常量 | 不建议改名，可改值 | 地图编码协议，`levels.py` 会解析这些编码 |
| `BOX_CODE_TO_COLOR` | 可调 | 箱子编码到颜色映射，决定颜色匹配规则 |
| `TARGET_CODE_TO_COLOR` | 可调 | 目标点编码到颜色映射 |
| `Player.x/y` | 运行时变量 | 玩家当前位置 |
| `Box.x/y/color` | 运行时变量 | 箱子位置与颜色属性 |
| `Target.x/y/color` | 关卡配置变量 | 目标点位置与对应颜色 |
| `PortalPair.entrance/exit_pos` | 关卡可调 | 传送门成对映射关系 |
| `PressurePlate.gate_ids` | 可调 | 压力板控制哪些门 |
| `Gate.is_open` | 运行时变量 | 门是否可通行 |
| `SublevelSpec.entrance/layer_name` | 可调 | 子关卡入口与目标图层 |
| `LayerState.width/height` | 关卡可调 | 地图尺寸 |
| `LayerState.static_map` | 关卡可调 | 静态地形矩阵 |
| `LayerState.boxes/targets/...` | 关卡与运行时 | 本层实体集合 |

## 6. 与作业要求对应
- 满足“状态空间与动作空间清晰定义”要求
- 为奖励函数与规则系统提供统一的数据基础
