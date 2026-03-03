"""Evaluation script for trained ShadowBox model."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np

from ai.agent import DQNAgent
from game.environment import ShadowBoxEnv
from game.levels import list_levels


def evaluate_level(agent: DQNAgent, level: int, num_episodes: int = 100) -> Dict[str, float]:
    env = ShadowBoxEnv(level_id=level)

    original_eps = agent.epsilon
    agent.epsilon = 0.0

    successes = 0
    steps_on_success = []
    deadlocks = 0

    for _ in range(num_episodes):
        env.load_level(level)
        state = env.reset()
        done = False
        steps = 0
        info = {}

        while not done:
            action = agent.select_action(state)
            state, _, done, info = env.step(action)
            steps += 1

        if info.get("success"):
            successes += 1
            steps_on_success.append(steps)
        if info.get("deadlock"):
            deadlocks += 1

    agent.epsilon = original_eps

    return {
        "win_rate": successes / num_episodes,
        "avg_steps": float(np.mean(steps_on_success)) if steps_on_success else float("inf"),
        "deadlock_rate": deadlocks / num_episodes,
    }


def evaluate_random_baseline(level: int, num_episodes: int = 100) -> Dict[str, float]:
    env = ShadowBoxEnv(level_id=level)
    successes = 0

    for _ in range(num_episodes):
        env.load_level(level)
        env.reset()
        done = False
        info = {}

        while not done:
            action = np.random.randint(0, env.action_space_size)
            _, _, done, info = env.step(action)

        if info.get("success"):
            successes += 1

    return {"win_rate": successes / num_episodes}


def save_eval_plot(results: Dict[int, Dict[str, float]], random_results: Dict[int, Dict[str, float]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    levels = sorted(results.keys())
    win_rates = [results[l]["win_rate"] for l in levels]
    deadlock_rates = [results[l]["deadlock_rate"] for l in levels]
    random_win_rates = [random_results[l]["win_rate"] for l in levels]

    x = np.arange(len(levels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width / 2, win_rates, width=width, label="DQN Win Rate", color="#4CAF50")
    ax.bar(x + width / 2, random_win_rates, width=width, label="Random Win Rate", color="#9E9E9E")
    ax.plot(x, deadlock_rates, marker="o", color="#D32F2F", label="Deadlock Rate")

    ax.set_xticks(x)
    ax.set_xticklabels([f"L{l}" for l in levels])
    ax.set_ylim(0, 1.0)
    ax.set_title("ShadowBox Evaluation Results")
    ax.set_ylabel("Rate")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.25)

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate trained ShadowBox model")
    parser.add_argument("--model", type=str, default="checkpoints/final_model.pth")
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--results-dir", type=str, default="results")
    args = parser.parse_args()

    env = ShadowBoxEnv(level_id=1)
    agent = DQNAgent(state_dim=env.state_dim, action_dim=env.action_space_size)
    agent.load(args.model)

    all_results: Dict[int, Dict[str, float]] = {}
    random_results: Dict[int, Dict[str, float]] = {}

    for level in list_levels():
        res = evaluate_level(agent, level=level, num_episodes=args.episodes)
        rand_res = evaluate_random_baseline(level=level, num_episodes=args.episodes)
        all_results[level] = res
        random_results[level] = rand_res

        print(f"\n=== Level {level} ({args.episodes} episodes) ===")
        print(f"Win Rate     : {res['win_rate']:.1%}")
        print(f"Avg Steps    : {res['avg_steps']:.1f}")
        print(f"Deadlock Rate: {res['deadlock_rate']:.1%}")
        print(f"Random Win   : {rand_res['win_rate']:.1%}")

    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    save_eval_plot(all_results, random_results, results_dir / "evaluation_results.png")

    np.savez(
        results_dir / "evaluation_metrics.npz",
        levels=np.array(sorted(all_results.keys())),
        win_rates=np.array([all_results[l]["win_rate"] for l in sorted(all_results.keys())]),
        deadlock_rates=np.array([all_results[l]["deadlock_rate"] for l in sorted(all_results.keys())]),
        random_win_rates=np.array([random_results[l]["win_rate"] for l in sorted(all_results.keys())]),
    )


if __name__ == "__main__":
    main()
