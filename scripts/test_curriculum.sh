#!/bin/bash
cd "$(dirname "$0")/.." || exit
source /opt/homebrew/Caskroom/miniconda/base/bin/activate CDS524
echo "课程学习快速测试 (500轮)"
python train.py --episodes 500 --curriculum-threshold 0.5 --curriculum-window 5 --render --render-every 1 --render-fps 120 --render-width 1280 --render-height 720 --log-interval 10
