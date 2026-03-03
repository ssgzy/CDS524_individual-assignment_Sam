#!/bin/bash
cd "$(dirname "$0")/.." || exit
source /opt/homebrew/Caskroom/miniconda/base/bin/activate CDS524
echo "快速训练模式 (120 FPS)"
python train.py --episodes 10000 --render --render-every 1 --render-fps 120 --render-width 1280 --render-height 720 --save-every 500 --log-interval 50
