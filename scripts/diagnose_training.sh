#!/bin/bash
# 训练结果诊断脚本

cd "$(dirname "$0")/.." || exit

echo "=========================================="
echo "  训练结果诊断"
echo "=========================================="
echo ""

# 检查训练日志
if [ -f "results/training_log.json" ]; then
    echo "📊 训练统计："
    echo ""
    python3 << 'EOF'
import json
with open('results/training_log.json', 'r') as f:
    log = json.load(f)

print(f"总轮数: {log['total_episodes']}")
print(f"最终关卡: Level {log['curriculum_final_level']}/5")
print(f"最终Epsilon: {log['final_epsilon']:.3f}")
print()
print("各关卡表现:")
print("-" * 50)
for level in range(1, 6):
    stats = log['win_rates_by_level'][str(level)]
    if stats['total_episodes'] > 0:
        print(f"Level {level}: {stats['total_episodes']:3d}轮 | 胜率 {stats['win_rate']:6.1%} | 通关 {stats['total_wins']:3d}次")
    else:
        print(f"Level {level}: 未训练")
print()

# 诊断
print("🔍 诊断结果:")
print("-" * 50)
if log['total_episodes'] < 1000:
    print("⚠️  训练轮数太少（<1000轮）")
    print("   建议: 运行 ./train_with_viz.sh 进行完整训练")

if log['curriculum_final_level'] < 5:
    print(f"⚠️  未完成所有关卡（当前Level {log['curriculum_final_level']}）")
    print("   建议: 增加训练轮数")

for level in range(1, 4):
    stats = log['win_rates_by_level'][str(level)]
    if stats['total_episodes'] > 0 and stats['win_rate'] < 0.5:
        print(f"⚠️  Level {level}胜率过低（{stats['win_rate']:.1%}）")
        print(f"   建议: 降低curriculum_threshold或增加训练时间")

if log['curriculum_final_level'] == 5:
    final_level_stats = log['win_rates_by_level']['5']
    if final_level_stats['win_rate'] >= 0.6:
        print("✅ 训练成功！所有关卡都达到了良好的表现")
    else:
        print("⚠️  Level 5胜率较低，建议继续训练")
EOF
else
    echo "❌ 未找到训练日志"
    echo "   请先运行训练脚本"
fi

echo ""
echo "=========================================="
echo ""
echo "📁 可用的模型检查点:"
ls -lh checkpoints/*.pth 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'

echo ""
echo "🎮 测试不同关卡:"
echo "  python play.py --mode human --level 1"
echo "  python play.py --mode human --level 2"
echo "  python play.py --mode human --level 3"
echo ""
echo "🤖 观看AI演示:"
echo "  python play.py --mode agent --model checkpoints/level_1_final.pth --level 1"
echo "  python play.py --mode agent --model checkpoints/level_2_final.pth --level 2"
echo ""
echo "📊 查看训练图表:"
echo "  open results/training_results.png"
echo ""
