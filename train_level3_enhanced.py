"""Level 3迁移学习 + 增强奖励训练"""
from ai.rainbow_agent import RainbowDQNAgent
from ai.level3_enhanced_env import Level3EnhancedEnv
import time

print("=" * 80)
print("Level 3 迁移学习 + 增强奖励训练")
print("=" * 80)
print("策略:")
print("  1. 从Level 2成功权重开始（迁移学习）")
print("  2. 使用增强奖励函数（Portal引导 + 距离奖励 + 探索奖励）")
print("  3. 防止重复动作循环")
print("  4. 训练3000轮")
print("=" * 80)

# 1. 创建agent并加载Level 2权重
agent = RainbowDQNAgent(
    input_channels=7,
    action_dim=5,
    lr=5e-5,  # 微调学习率
    gamma=0.99,
    batch_size=48,
    buffer_capacity=50000,
    target_update_freq=2000,
    n_step=3,
    use_noisy=True,
    use_curiosity=True,
    curiosity_weight=1.0,  # 加倍好奇心
)

print("\n📂 加载Level 2权重...")
agent.load('checkpoints_fixed/best_level2.pt')
print("✅ Level 2权重加载成功")

# 2. 重置探索参数
print("\n🔄 重置探索参数...")
agent.epsilon = 0.5  # 高探索率
agent.epsilon_min = 0.05
agent.epsilon_decay = 0.9995
print(f"  Epsilon: {agent.epsilon}")
print(f"  Curiosity weight: {agent.curiosity_weight}")

# 3. 创建增强环境
env = Level3EnhancedEnv(level_id=3)
print(f"\n🎮 Level 3增强环境")
print(f"  Max steps: {env.max_steps}")
print(f"  Boxes: {len(env.env.boxes)}")
print(f"  Portals: {len(env.env.portals)}")
print("\n增强奖励:")
print("  ✅ Portal使用: +20")
print("  ✅ 箱子放置: +100")
print("  ✅ 距离改进: +2 per unit")
print("  ✅ 探索新位置: +1")
print("  ❌ 重复动作: -5")

# 4. 训练
print("\n" + "=" * 80)
print("开始训练 3000轮")
print("=" * 80)

start_time = time.time()
success_count = 0
best_success_rate = 0
portal_usage_count = 0

for episode in range(1, 3001):
    state = env.reset()
    done = False
    episode_reward = 0
    steps = 0

    while not done:
        action = agent.select_action(state, eval_mode=False)
        next_state, reward, done, info = env.step(action)
        agent.store_transition(state, action, reward, next_state, done)

        # 每4步训练一次
        if steps % 4 == 0:
            agent.train_step()

        state = next_state
        episode_reward += reward
        steps += 1

    if info.get('success'):
        success_count += 1

    portal_usage_count += env.portal_used_count

    # 每100轮打印进度
    if episode % 100 == 0:
        elapsed = time.time() - start_time
        eps_per_sec = episode / elapsed
        success_rate = success_count / episode * 100
        avg_portal_usage = portal_usage_count / episode

        print(f"Episode {episode:4d} | "
              f"Reward: {episode_reward:7.1f} | "
              f"Steps: {steps:3d} | "
              f"Success: {success_count:3d}/{episode:4d} ({success_rate:5.1f}%) | "
              f"Portal: {avg_portal_usage:.2f}/ep | "
              f"ε: {agent.epsilon:.3f} | "
              f"Speed: {eps_per_sec:.2f} eps/s")

    # 每500轮评估
    if episode % 500 == 0:
        print("-" * 80)
        print(f"📊 评估 (Episode {episode})...")

        eval_success = 0
        eval_reward = 0
        eval_steps = 0
        eval_portal_usage = 0

        for _ in range(10):
            state = env.reset()
            done = False
            ep_steps = 0
            ep_reward = 0

            while not done and ep_steps < 300:
                action = agent.select_action(state, eval_mode=True)
                next_state, reward, done, info = env.step(action)
                state = next_state
                ep_steps += 1
                ep_reward += reward

            if info.get('success'):
                eval_success += 1
            eval_reward += ep_reward
            eval_steps += ep_steps
            eval_portal_usage += env.portal_used_count

        eval_rate = eval_success / 10 * 100
        print(f"  Success Rate: {eval_rate:.0f}% ({eval_success}/10)")
        print(f"  Avg Reward: {eval_reward/10:.1f}")
        print(f"  Avg Steps: {eval_steps/10:.1f}")
        print(f"  Avg Portal Usage: {eval_portal_usage/10:.1f}")

        # 保存checkpoint
        agent.save(f'checkpoints_fixed/level3_enhanced_ep{episode}.pt')
        print(f"  💾 Saved: level3_enhanced_ep{episode}.pt")

        # 保存最佳模型
        if eval_rate > best_success_rate:
            best_success_rate = eval_rate
            agent.save('checkpoints_fixed/best_level3_enhanced.pt')
            print(f"  ⭐ New best! Success rate: {eval_rate:.0f}%")

        print("-" * 80)

# 5. 保存最终模型
print("\n" + "=" * 80)
print("训练完成!")
print("=" * 80)

total_time = time.time() - start_time
final_success_rate = success_count / 3000 * 100

print(f"总训练时间: {total_time/60:.1f}分钟")
print(f"最终成功率: {final_success_rate:.1f}% ({success_count}/3000)")
print(f"最佳评估成功率: {best_success_rate:.0f}%")
print(f"平均Portal使用: {portal_usage_count/3000:.2f}次/episode")

agent.save('checkpoints_fixed/level3_enhanced_final.pt')
print(f"\n💾 最终模型已保存: level3_enhanced_final.pt")

# 6. 最终评估
print("\n" + "=" * 80)
print("最终评估 (50轮)")
print("=" * 80)

final_success = 0
final_reward = 0
final_steps = 0
final_portal = 0

for ep in range(50):
    state = env.reset()
    done = False
    steps = 0
    reward_sum = 0

    while not done and steps < 300:
        action = agent.select_action(state, eval_mode=True)
        next_state, reward, done, info = env.step(action)
        state = next_state
        steps += 1
        reward_sum += reward

    if info.get('success'):
        final_success += 1
    final_reward += reward_sum
    final_steps += steps
    final_portal += env.portal_used_count

    if (ep + 1) % 10 == 0:
        print(f"  {ep+1}/50 - Success: {final_success}/{ep+1} ({final_success/(ep+1)*100:.1f}%)")

print("\n" + "=" * 80)
print("📊 最终结果")
print("=" * 80)
print(f"成功率: {final_success}/50 ({final_success/50*100:.1f}%)")
print(f"平均奖励: {final_reward/50:.1f}")
print(f"平均步数: {final_steps/50:.1f}")
print(f"平均Portal使用: {final_portal/50:.1f}")
print("=" * 80)
