# Scripts 文件夹说明

本文件夹包含所有用于训练、测试和演示的便捷脚本。

## 📋 脚本分类

### 🎮 测试脚本

#### `test_new_renderer.sh`
**用途**: 测试新的2D渲染器
**模式**: 手动游玩
**时长**: 随意
**说明**:
- 启动手动游玩模式
- 体验Patrick's Parabox风格的2D界面
- 了解游戏机制和控制方式
- 推荐首次使用时运行

**使用**:
```bash
cd scripts
./test_new_renderer.sh
```

#### `test_viz.sh`
**用途**: 测试可视化功能
**模式**: AI训练
**时长**: 约1-2分钟
**说明**:
- 训练10轮
- 确认环境和依赖正常
- 验证可视化窗口能正常显示

**使用**:
```bash
./test_viz.sh
```

#### `test_curriculum.sh`
**用途**: 测试课程学习机制
**模式**: AI训练（快速升级）
**时长**: 约10-20分钟
**说明**:
- 训练500轮
- 使用50%胜率阈值（容易升级）
- 快速看到AI从Level 1升级到Level 5
- 验证课程学习是否正常工作

**使用**:
```bash
./test_curriculum.sh
```

### 🚀 训练脚本

#### `train_with_viz.sh` ⭐ 推荐
**用途**: 标准可视化训练
**FPS**: 60
**时长**: 2-4小时
**说明**:
- 平衡速度和观察效果
- 每个episode都渲染
- 适合观察AI学习过程
- 使用优化后的课程学习参数

**使用**:
```bash
./train_with_viz.sh
```

**参数**:
- Episodes: 10000
- 胜率阈值: 70%
- 评估窗口: 10轮
- 渲染FPS: 60

#### `train_fast.sh`
**用途**: 快速可视化训练
**FPS**: 120
**时长**: 1.5-3小时
**说明**:
- 更快的渲染速度
- 适合快速观察AI学习趋势
- 牺牲一些观察细节换取速度

**使用**:
```bash
./train_fast.sh
```

#### `train_slow.sh`
**用途**: 慢速可视化训练
**FPS**: 10
**时长**: 4-6小时
**说明**:
- 慢速渲染
- 适合仔细观察每一步操作
- 用于调试和理解AI决策

**使用**:
```bash
./train_slow.sh
```

#### `train_no_viz.sh`
**用途**: 无可视化训练
**FPS**: N/A
**时长**: 1-2小时
**说明**:
- 最快训练速度
- 适合长时间训练
- 追求最佳性能
- 后台运行

**使用**:
```bash
./train_no_viz.sh
```

### 📖 信息脚本

#### `show_training_options.sh`
**用途**: 显示所有训练选项
**说明**:
- 列出所有可用脚本
- 显示课程学习说明
- 显示新渲染器特点
- 提供快速开始指南

**使用**:
```bash
./show_training_options.sh
```

#### `QUICK_START.sh`
**用途**: 快速启动指南
**说明**:
- 完整的使用流程
- 详细的功能说明
- 常见问题解答
- 文档索引

**使用**:
```bash
./QUICK_START.sh
```

## 🎯 推荐使用流程

### 首次使用
```bash
# 1. 查看快速启动指南
./QUICK_START.sh

# 2. 测试新渲染器（手动游玩）
./test_new_renderer.sh

# 3. 测试课程学习（快速验证）
./test_curriculum.sh

# 4. 开始正式训练
./train_with_viz.sh
```

### 快速验证
```bash
# 测试环境
./test_viz.sh

# 测试课程学习
./test_curriculum.sh
```

### 正式训练
```bash
# 标准训练（推荐）
./train_with_viz.sh

# 或快速训练
./train_fast.sh

# 或最快训练（无可视化）
./train_no_viz.sh
```

## 📊 脚本对比

| 脚本 | 可视化 | FPS | 训练轮数 | 预计时间 | 适用场景 |
|------|--------|-----|----------|----------|----------|
| test_viz.sh | ✓ | 30 | 10 | 1-2分钟 | 环境测试 |
| test_curriculum.sh | ✓ | 120 | 500 | 10-20分钟 | 课程学习测试 |
| train_with_viz.sh | ✓ | 60 | 10000 | 2-4小时 | 标准训练 |
| train_fast.sh | ✓ | 120 | 10000 | 1.5-3小时 | 快速训练 |
| train_slow.sh | ✓ | 10 | 10000 | 4-6小时 | 详细观察 |
| train_no_viz.sh | ✗ | N/A | 10000 | 1-2小时 | 最快训练 |

## ⚙️ 自定义参数

所有训练脚本都调用 `train.py`，你可以直接修改脚本中的参数：

### 常用参数
```bash
--episodes 10000              # 训练轮数
--curriculum-threshold 0.7    # 胜率阈值（0.7 = 70%）
--curriculum-window 10        # 评估窗口（轮数）
--render                      # 开启可视化
--render-fps 60               # 渲染FPS
--render-every 1              # 每N轮渲染一次
--cell-size 64                # 格子大小（像素）
--learning-rate 0.0005        # 学习率
--gamma 0.99                  # 折扣因子
--epsilon-start 1.0           # 初始探索率
--epsilon-end 0.05            # 最终探索率
--batch-size 64               # 批次大小
```

### 示例：自定义训练
```bash
# 创建自己的训练脚本
cd scripts
cp train_with_viz.sh my_custom_train.sh

# 编辑参数
nano my_custom_train.sh

# 运行
./my_custom_train.sh
```

## 🔧 脚本结构

所有训练脚本都遵循相同的结构：

```bash
#!/bin/bash
# 激活conda环境
source /opt/homebrew/Caskroom/miniconda/base/bin/activate CDS524

# 显示信息
echo "=========================================="
echo "  脚本名称和说明"
echo "=========================================="

# 运行训练
python train.py \
    --episodes 10000 \
    --render \
    --render-fps 60 \
    # ... 其他参数

# 完成提示
echo "训练完成！"
```

## 📝 注意事项

1. **conda环境**: 所有脚本都会自动激活CDS524环境
2. **执行权限**: 脚本已设置执行权限，可直接运行
3. **相对路径**: 脚本使用相对路径，需要在项目根目录或scripts目录运行
4. **中断训练**: 可以随时关闭窗口或按Ctrl+C停止训练
5. **进度保存**: 训练进度会自动保存到checkpoints目录

## 🆘 常见问题

### Q: 脚本无法执行？
```bash
# 添加执行权限
chmod +x scripts/*.sh
```

### Q: conda环境未激活？
```bash
# 手动激活
conda activate CDS524

# 然后运行脚本
cd scripts
./train_with_viz.sh
```

### Q: 想修改训练参数？
```bash
# 方法1: 直接编辑脚本
nano scripts/train_with_viz.sh

# 方法2: 手动运行train.py
conda activate CDS524
python train.py --episodes 5000 --render --render-fps 120
```

### Q: 训练太慢？
```bash
# 使用无可视化模式
./train_no_viz.sh

# 或减少训练轮数
python train.py --episodes 2000
```

## 📚 相关文档

- `../README.md` - 项目总览
- `../TRAINING_GUIDE.md` - 训练详细指南
- `../CURRICULUM_LEARNING_GUIDE.md` - 课程学习说明
- `../NEW_RENDERER_GUIDE.md` - 新渲染器说明

## 🚀 快速开始

```bash
# 从项目根目录
cd scripts
./QUICK_START.sh
```

或者直接：
```bash
# 测试新界面
scripts/test_new_renderer.sh

# 开始训练
scripts/train_with_viz.sh
```
