#!/bin/bash
# ShadowBox 可视化训练启动脚本

# 切换到项目根目录
cd "$(dirname "$0")/.." || exit

# 激活conda环境
source /opt/homebrew/Caskroom/miniconda/base/bin/activate CDS524

echo "=========================================="
echo "  ShadowBox 可视化训练"
echo "=========================================="
echo "环境: CDS524"
echo "可视化: 开启"
echo "渲染频率: 每个episode"
echo "FPS: 60 (可调整)"
echo ""
echo "提示："
echo "  - 关闭窗口可随时停止训练"
echo "  - 训练进度会自动保存"
echo "  - 按Ctrl+C也可停止"
echo "=========================================="
echo ""

# 启动训练（带可视化）
python train.py \
    --episodes 10000 \
    --render \
    --render-every 1 \
    --render-fps 60 \
    --render-width 1280 \
    --render-height 720 \
    --save-every 500 \
    --log-interval 50

echo ""
echo "训练完成！检查点和结果已保存到："
echo "  - checkpoints/"
echo "  - results/"
