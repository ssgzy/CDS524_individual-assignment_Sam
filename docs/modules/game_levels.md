# 模块说明：`game/levels.py`

## 1. 模块作用
`levels.py` 负责定义 5 个主关卡 + 子关卡地图，并把二维编码矩阵解析成可运行的 `LayerState`。

## 2. 核心功能
- 提供 `load_level(level_id)`：返回关卡对象 `ParsedLevel`
- 提供 `list_levels()`：返回 `[1,2,3,4,5]`
- 解析地图编码：玩家、箱子、目标点、门、压力板、传送门、子关卡入口
- 支持压力板到机关门的链接关系（`plate_links`）

## 3. 使用到的知识点
- 规则驱动环境建模（Rule-based Environment）
- 课程学习（由简到难的关卡构造）
- 图层化状态管理（outer/sublevel）

## 4. 关键函数
- `_parse_layer(...)`：核心解析器
- `load_level(level_id)`：课程学习的关卡工厂函数

## 5. 变量说明（可调性 + 意义）

| 变量 | 是否可调 | 意义 |
|---|---|---|
| `LEVEL_1_OUTER` ~ `LEVEL_5_OUTER` | 可调 | 主关卡地图，控制难度与机制组合 |
| `LEVEL_4_SUB`, `LEVEL_5_SUB` | 可调 | 子关卡地图，触发嵌套机制 |
| `ParsedLevel.max_steps` | 强烈建议调参 | 每关步数上限，影响探索深度与超时惩罚 |
| `plate_links` | 可调 | 压力板控制门的映射关系 |
| `sublevel_layer` | 可调 | 入口连接到哪个子层 |
| `portal_a1/a2`, `portal_b1/b2` | 关卡可调 | 传送门空间映射位置 |
| `_parse_layer.width/height` | 自动推导 | 地图尺寸 |
| `_parse_layer.static_map` | 自动构建 | 静态地图，动态实体会被剥离为对象 |
| `walls/boxes/targets/gates/plates` | 自动构建 | 供环境运行时直接使用的实体列表 |

## 6. 与作业要求对应
- 实现了“关卡难度递增设计”
- 包含“大地图、多箱子、传送门、压力板、子关卡”全部机制
- 可直接支持 Curriculum Learning
