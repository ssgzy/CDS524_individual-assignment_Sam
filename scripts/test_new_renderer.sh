#!/bin/bash
cd "$(dirname "$0")/.." || exit
source /opt/homebrew/Caskroom/miniconda/base/bin/activate CDS524
echo "测试新渲染器 (手动游玩)"
python play.py --mode human --level 1 --fps 30
