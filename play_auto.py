"""Play ShadowBox with auto-level progression - Patrick's Parabox Style"""

from __future__ import annotations

import pygame
from game.entities import Action
from game.environment import ShadowBoxEnv
from game.renderer_2d import TopDownRenderer


def main() -> None:
    # 配置
    WIDTH, HEIGHT = 1280, 720
    FPS = 30
    CELL_SIZE = 64

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ShadowBox - 自动升级模式")
    clock = pygame.time.Clock()

    # 游戏状态
    current_level = 1
    max_level = 5
    env = ShadowBoxEnv(level_id=current_level)
    state = env.reset()
    renderer = TopDownRenderer(screen, cell_size=CELL_SIZE, screen_width=WIDTH, screen_height=HEIGHT)

    running = True
    episode_reward = 0.0
    episode_steps = 0

    print("\n" + "="*60)
    print("🎮 ShadowBox - 自动升级模式")
    print("="*60)
    print("从 Level 1 开始，完成后自动升级！")
    print("\n控制:")
    print("  方向键 - 移动")
    print("  R - 重置  N - 下一关  P - 上一关")
    print("  ESC - 退出")
    print("="*60)

    while running:
        action = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_r:
                    # 重置当前关卡
                    state = env.reset()
                    episode_reward = 0.0
                    episode_steps = 0
                    print(f"🔄 重置 Level {current_level}")

                elif event.key == pygame.K_n:
                    # 下一关
                    if current_level < max_level:
                        current_level += 1
                        env.close()
                        env = ShadowBoxEnv(level_id=current_level)
                        state = env.reset()
                        episode_reward = 0.0
                        episode_steps = 0
                        print(f"⬆️  切换到 Level {current_level}")
                    else:
                        print("已经是最后一关！")

                elif event.key == pygame.K_p:
                    # 上一关
                    if current_level > 1:
                        current_level -= 1
                        env.close()
                        env = ShadowBoxEnv(level_id=current_level)
                        state = env.reset()
                        episode_reward = 0.0
                        episode_steps = 0
                        print(f"⬇️  切换到 Level {current_level}")
                    else:
                        print("已经是第一关！")

                # 移动控制
                elif event.key == pygame.K_UP:
                    action = Action.UP
                elif event.key == pygame.K_DOWN:
                    action = Action.DOWN
                elif event.key == pygame.K_LEFT:
                    action = Action.LEFT
                elif event.key == pygame.K_RIGHT:
                    action = Action.RIGHT
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    action = Action.ENTER

        # 执行动作
        info = {}
        if action is not None:
            state, reward, done, info = env.step(int(action))
            episode_reward += reward
            episode_steps += 1

            if done:
                if info.get("success"):
                    print(f"🎉 Level {current_level} 完成！")
                    print(f"   步数: {episode_steps}")
                    print(f"   奖励: {episode_reward:.2f}")

                    # 自动升级
                    if current_level < max_level:
                        print(f"⬆️  自动升级到 Level {current_level + 1}")
                        pygame.time.wait(1500)  # 等待1.5秒

                        current_level += 1
                        env.close()
                        env = ShadowBoxEnv(level_id=current_level)
                        state = env.reset()
                        episode_reward = 0.0
                        episode_steps = 0
                    else:
                        print("🏆 恭喜！你完成了所有关卡！")
                        pygame.time.wait(2000)
                        running = False
                else:
                    # 失败
                    status = "DEADLOCK" if info.get("deadlock") else "TIMEOUT"
                    print(f"❌ {status} | 步数={episode_steps} | 按R重置")
                    state = env.reset()
                    episode_reward = 0.0
                    episode_steps = 0

        # 渲染
        renderer.render(
            env,
            extra_ui={
                "Level": f"{current_level}/{max_level}",
                "Steps": str(episode_steps),
                "Reward": f"{episode_reward:.2f}",
                "Boxes": f"{sum(1 for b in env.boxes if env.is_box_on_target(b))}/{len(env.boxes)}",
            },
        )

        pygame.display.flip()
        clock.tick(FPS)

    env.close()
    pygame.quit()
    print("\n游戏结束！")


if __name__ == "__main__":
    main()
