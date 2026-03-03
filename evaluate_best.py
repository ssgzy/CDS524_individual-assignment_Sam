"""评估训练好的模型"""
from ai.rainbow_agent import RainbowDQNAgent
from ai.fixed_env import FixedEnv

print("=" * 70)
print("🎯 评估最佳模型 - Level 2")
print("=" * 70)

env = FixedEnv(level_id=2)
agent = RainbowDQNAgent(
    input_channels=7,
    action_dim=5,
    batch_size=48,
    use_curiosity=True,
)

# 加载最佳模型
agent.load("checkpoints_fixed/best_level2.pt")

print("\n评估50个episodes...")
success_count = 0
total_reward = 0.0
total_steps = 0

for ep in range(50):
    state = env.reset()
    episode_reward = 0.0
    steps = 0
    done = False

    while not done:
        action = agent.select_action(state, eval_mode=True)
        next_state, reward, done, info = env.step(action)
        state = next_state
        episode_reward += reward
        steps += 1

    if info.get('success'):
        success_count += 1

    total_reward += episode_reward
    total_steps += steps

    if (ep + 1) % 10 == 0:
        print(f"  {ep+1}/50 episodes - Success: {success_count}/{ep+1} ({success_count/(ep+1)*100:.1f}%)")

print("\n" + "=" * 70)
print("📊 最终评估结果")
print("=" * 70)
print(f"成功率:     {success_count}/50 ({success_count/50*100:.1f}%)")
print(f"平均奖励:   {total_reward/50:.2f}")
print(f"平均步数:   {total_steps/50:.1f}")
print("=" * 70)
