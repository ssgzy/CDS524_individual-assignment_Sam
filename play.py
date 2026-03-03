"""Play ShadowBox manually or run trained agent visualization."""

from __future__ import annotations

import argparse
import sys

import pygame

from ai.agent import DQNAgent
from game.entities import Action
from game.environment import ShadowBoxEnv
from game.renderer_2d import TopDownRenderer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play ShadowBox")
    parser.add_argument("--level", type=int, default=1)
    parser.add_argument("--mode", type=str, choices=["human", "agent"], default="human")
    parser.add_argument("--model", type=str, default="")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pygame.init()
    screen = pygame.display.set_mode((args.width, args.height))
    pygame.display.set_caption("ShadowBox - Patrick's Parabox Style")
    clock = pygame.time.Clock()

    env = ShadowBoxEnv(level_id=args.level)
    state = env.reset()

    renderer = TopDownRenderer(screen, cell_size=64, screen_width=args.width, screen_height=args.height)

    agent = None
    if args.mode == "agent" or args.model:
        agent = DQNAgent(state_dim=env.state_dim, action_dim=env.action_space_size)
        if args.model:
            agent.load(args.model)
        agent.epsilon = 0.0

    running = True
    episode_reward = 0.0
    episode_steps = 0

    while running:
        action = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    state = env.reset()
                    episode_reward = 0.0
                    episode_steps = 0
                elif args.mode == "human":
                    if event.key == pygame.K_UP:
                        action = Action.UP
                    elif event.key == pygame.K_DOWN:
                        action = Action.DOWN
                    elif event.key == pygame.K_LEFT:
                        action = Action.LEFT
                    elif event.key == pygame.K_RIGHT:
                        action = Action.RIGHT
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        action = Action.ENTER

        if args.mode == "agent" and agent is not None:
            action = Action(agent.select_action(state))

        info = {}
        if action is not None:
            state, reward, done, info = env.step(int(action))
            episode_reward += reward
            episode_steps += 1

            if done:
                status = "SUCCESS" if info.get("success") else "FAIL"
                print(
                    f"Episode finished | {status} | Steps={episode_steps} | Reward={episode_reward:.2f} | Info={info}"
                )
                state = env.reset()
                episode_reward = 0.0
                episode_steps = 0

        renderer.render(
            env,
            extra_ui={
                "Mode": args.mode,
                "Episode Reward": f"{episode_reward:.2f}",
                "Episode Steps": str(episode_steps),
            },
        )
        clock.tick(args.fps)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
