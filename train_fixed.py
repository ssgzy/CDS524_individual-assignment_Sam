"""使用FixedEnv训练 - 修复后的环境"""

import argparse
from pathlib import Path
import time
import numpy as np

from ai.rainbow_agent import RainbowDQNAgent
from ai.fixed_env import FixedEnv


def train_with_fixed_env(
    level_id: int = 1,
    num_episodes: int = 1000,
    save_freq: int = 100,
    eval_freq: int = 50,
    checkpoint_dir: str = "checkpoints_fixed",
):
    """使用FixedEnv训练"""

    print("=" * 80)
    print(f"🎮 Training with FixedEnv - Level {level_id}")
    print("=" * 80)

    # Create environment
    env = FixedEnv(level_id=level_id)

    # Create agent (final balanced config)
    agent = RainbowDQNAgent(
        input_channels=7,
        action_dim=5,
        lr=1e-4,
        gamma=0.99,
        batch_size=48,  # Balanced
        buffer_capacity=50000,
        target_update_freq=1000,
        n_step=3,
        use_noisy=True,
        use_curiosity=True,  # Re-enable for better exploration
        curiosity_weight=0.5,
    )

    # Create checkpoint directory
    checkpoint_path = Path(checkpoint_dir)
    checkpoint_path.mkdir(parents=True, exist_ok=True)

    # Training statistics
    success_count = 0
    best_success_rate = 0.0

    print(f"📊 Configuration:")
    print(f"   Episodes: {num_episodes}")
    print(f"   Device: {agent.device}")
    print(f"   Max steps: {env.max_steps}")
    print("=" * 80)

    start_time = time.time()

    train_step_counter = 0
    for episode in range(1, num_episodes + 1):
        state = env.reset()
        episode_reward = 0.0
        episode_length = 0
        done = False

        while not done:
            action = agent.select_action(state, eval_mode=False)
            next_state, reward, done, info = env.step(action)
            agent.store_transition(state, action, reward, next_state, done)

            # Train every 4 steps instead of every step (4x speedup)
            train_step_counter += 1
            if train_step_counter % 4 == 0:
                agent.train_step()

            state = next_state
            episode_reward += reward
            episode_length += 1

        if info.get("success"):
            success_count += 1

        # Print progress
        if episode % 10 == 0:
            elapsed = time.time() - start_time
            eps_per_sec = episode / elapsed
            success_rate = (success_count / episode) * 100

            print(f"Episode {episode:4d} | "
                  f"Reward: {episode_reward:7.2f} | "
                  f"Length: {episode_length:3d} | "
                  f"Success: {success_count:3d} ({success_rate:5.1f}%) | "
                  f"Buffer: {len(agent.replay_buffer):6d} | "
                  f"Speed: {eps_per_sec:.2f} eps/s")

        # Evaluation
        if episode % eval_freq == 0:
            eval_success, eval_reward, eval_length = evaluate_agent(agent, env, 10)
            eval_rate = (eval_success / 10) * 100

            print("-" * 80)
            print(f"📈 Evaluation (Episode {episode}):")
            print(f"   Success Rate: {eval_rate:.1f}% ({eval_success}/10)")
            print(f"   Avg Reward: {eval_reward:.2f}")
            print(f"   Avg Length: {eval_length:.1f}")
            print("-" * 80)

            if eval_rate > best_success_rate:
                best_success_rate = eval_rate
                best_path = checkpoint_path / f"best_level{level_id}.pt"
                agent.save(best_path)
                print(f"💾 New best model! Success rate: {eval_rate:.1f}%")

        # Save checkpoint
        if episode % save_freq == 0:
            save_path = checkpoint_path / f"level{level_id}_ep{episode}.pt"
            agent.save(save_path)

    # Final evaluation
    print("\n" + "=" * 80)
    print("🏁 Training Complete!")
    print("=" * 80)

    final_success, final_reward, final_length = evaluate_agent(agent, env, 20)

    print(f"📊 Final Evaluation (20 episodes):")
    print(f"   Success Rate: {(final_success / 20 * 100):.1f}%")
    print(f"   Avg Reward: {final_reward:.2f}")
    print(f"   Avg Length: {final_length:.1f}")
    print(f"   Best Success Rate: {best_success_rate:.1f}%")
    print(f"   Training Time: {(time.time() - start_time) / 60:.1f} minutes")
    print("=" * 80)

    # Save final model
    final_path = checkpoint_path / f"final_level{level_id}.pt"
    agent.save(final_path)

    env.close()


def evaluate_agent(agent, env, num_episodes: int = 10):
    """Evaluate agent"""
    success_count = 0
    total_reward = 0.0
    total_length = 0

    for _ in range(num_episodes):
        state = env.reset()
        episode_reward = 0.0
        episode_length = 0
        done = False

        while not done:
            action = agent.select_action(state, eval_mode=True)
            next_state, reward, done, info = env.step(action)

            state = next_state
            episode_reward += reward
            episode_length += 1

        if info.get("success"):
            success_count += 1

        total_reward += episode_reward
        total_length += episode_length

    avg_reward = total_reward / num_episodes
    avg_length = total_length / num_episodes

    return success_count, avg_reward, avg_length


def main():
    parser = argparse.ArgumentParser(description="Train with FixedEnv")
    parser.add_argument("--level", type=int, default=1, help="Level ID")
    parser.add_argument("--episodes", type=int, default=1000, help="Number of episodes")
    parser.add_argument("--save-freq", type=int, default=100, help="Save frequency")
    parser.add_argument("--eval-freq", type=int, default=50, help="Evaluation frequency")
    parser.add_argument("--checkpoint-dir", type=str, default="checkpoints_fixed", help="Checkpoint directory")

    args = parser.parse_args()

    train_with_fixed_env(
        level_id=args.level,
        num_episodes=args.episodes,
        save_freq=args.save_freq,
        eval_freq=args.eval_freq,
        checkpoint_dir=args.checkpoint_dir,
    )


if __name__ == "__main__":
    main()
