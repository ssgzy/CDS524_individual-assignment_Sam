#!/bin/bash
cd "$(dirname "$0")/.." || exit
source /opt/homebrew/Caskroom/miniconda/base/bin/activate CDS524
echo "可视化功能测试 (10轮)"
python train.py --episodes 10 --render --render-every 1 --render-fps 30 --render-width 1280 --render-height 720 --log-interval 1
