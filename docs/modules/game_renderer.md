# 模块说明：`game/renderer.py`

## 1. 模块作用
`renderer.py` 负责将网格地图以伪3D等距视角渲染到 Pygame 窗口，提供可视化交互与演示能力。

## 2. 核心功能
- 网格坐标转等距坐标 `grid_to_iso`
- 程序化绘制地板、墙、箱子、玩家、机关门
- 绘制目标点、传送门、压力板、子关卡入口特效
- UI 叠加（关卡、层级、步数、模式等）

## 3. 使用到的知识点
- Isometric Projection（等距投影）
- 渲染层次与深度排序（`x+y` 排序）
- 程序化美术（无外部贴图依赖）

## 4. 关键类
- `IsometricRenderer`
  - `load_sprites()`：生成基础精灵
  - `render(env, extra_ui)`：整帧渲染

## 5. 变量说明（可调性 + 意义）

| 变量 | 是否可调 | 意义 |
|---|---|---|
| `tile_w=64`, `tile_h=32` | 可调 | 等距瓦片尺寸，影响视觉密度 |
| `screen_width`, `screen_height` | 可调 | 窗口分辨率 |
| `origin_x`, `origin_y` | 可调 | 地图在屏幕中的偏移/居中位置 |
| `TARGET_TYPES`, `PORTAL_TYPES` | 可扩展 | 静态元素类型集合 |
| `COLOR_MAP` | 可调 | 箱子颜色主题 |
| `TARGET_COLOR_MAP` | 可调 | 目标点颜色主题 |
| `font`, `small_font` | 可调 | UI字体样式与大小 |
| `draw_queue`（局部） | 运行时变量 | 动态实体深度排序队列 |
| `extra_ui` | 可调 | 训练/演示时自定义状态展示 |

## 6. 与作业要求对应
- 满足“UI显示当前状态、动作结果和交互过程”
- 使用 Pygame 实现可视化环境与演示
