#!/bin/bash
cd "$(dirname "$0")/.." || exit
source /opt/homebrew/Caskroom/miniconda/base/bin/activate CDS524
echo "无可视化训练模式 (最快)"
python train.py --episodes 10000 --save-every 500 --log-interval 50
