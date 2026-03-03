"""观看训练好的AI玩游戏 - 支持所有关卡"""
import pygame
import time
import argparse
from ai.rainbow_agent import RainbowDQNAgent
from ai.fixed_env import FixedEnv

def watch_ai(level: int = 2, episodes: int = 10):
    """观看AI玩指定关卡"""
    # 初始化pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption(f"AI Playing Level {level}")
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    # 加载环境和agent
    env = FixedEnv(level_id=level)
    agent = RainbowDQNAgent(input_channels=7, action_dim=5, batch_size=48, use_curiosity=True)

    model_path = f"checkpoints_fixed/best_level{level}.pt"
    # Level 3使用final模型
    if level == 3:
        model_path = "checkpoints_fixed/final_level3.pt"

    try:
        agent.load(model_path)
        print(f"✅ 已加载模型: {model_path}")
    except FileNotFoundError:
        print(f"❌ 找不到模型: {model_path}")
        print(f"请先训练Level {level}或使用其他关卡")
        pygame.quit()
        return

    print(f"\n按空格键开始下一局，ESC退出\n")

    episode = 0
    running = True
    playing = False
    action_names = ["NOOP", "UP", "DOWN", "LEFT", "RIGHT"]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    playing = True

        if playing:
            episode += 1
            state = env.reset()
            done = False
            steps = 0
            total_reward = 0

            while not done and running:
                # 处理事件
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        running = False

                # AI选择动作
                action = agent.select_action(state, eval_mode=True)
                next_state, reward, done, info = env.step(action)

                state = next_state
                steps += 1
                total_reward += reward

                # 渲染游戏画面
                screen.fill((20, 20, 30))

                # 绘制地图
                cell_size = 40
                offset_x, offset_y = 50, 100

                # 获取地图尺寸 - 扫描所有墙壁找到真实边界
                max_x = 0
                max_y = 0

                # 扫描墙壁找到地图边界
                for y in range(50):  # 假设地图不超过50x50
                    for x in range(50):
                        if env.env.is_wall((x, y)):
                            max_x = max(max_x, x)
                            max_y = max(max_y, y)

                # 确保包含所有游戏元素
                if env.env.boxes:
                    max_x = max(max_x, max(box.pos[0] for box in env.env.boxes))
                    max_y = max(max_y, max(box.pos[1] for box in env.env.boxes))
                if env.env.targets:
                    max_x = max(max_x, max(target.pos[0] for target in env.env.targets))
                    max_y = max(max_y, max(target.pos[1] for target in env.env.targets))

                max_x = max(max_x, env.env.player.pos[0])
                max_y = max(max_y, env.env.player.pos[1])

                # 加1确保显示完整
                max_x += 1
                max_y += 1

                for y in range(max_y):
                    for x in range(max_x):
                        rect = pygame.Rect(offset_x + x*cell_size, offset_y + y*cell_size,
                                         cell_size, cell_size)

                        # 墙
                        if env.env.is_wall((x, y)):
                            pygame.draw.rect(screen, (100, 100, 100), rect)
                        else:
                            pygame.draw.rect(screen, (40, 40, 50), rect)

                        pygame.draw.rect(screen, (60, 60, 70), rect, 1)

                # 绘制目标
                for target in env.env.targets:
                    tx, ty = target.pos
                    rect = pygame.Rect(offset_x + tx*cell_size + 5,
                                     offset_y + ty*cell_size + 5,
                                     cell_size-10, cell_size-10)
                    pygame.draw.rect(screen, (255, 200, 0), rect)

                # 绘制箱子
                for box in env.env.boxes:
                    bx, by = box.pos
                    on_target = env.env.is_box_on_target(box)
                    color = (0, 255, 0) if on_target else (200, 100, 50)
                    rect = pygame.Rect(offset_x + bx*cell_size + 8,
                                     offset_y + by*cell_size + 8,
                                     cell_size-16, cell_size-16)
                    pygame.draw.rect(screen, color, rect)

                # 绘制玩家
                px, py = env.env.player.pos
                pygame.draw.circle(screen, (100, 150, 255),
                                 (offset_x + px*cell_size + cell_size//2,
                                  offset_y + py*cell_size + cell_size//2),
                                 cell_size//3)

                # 显示信息
                info_texts = [
                    f"Episode: {episode}",
                    f"Steps: {steps}",
                    f"Reward: {total_reward:.1f}",
                    f"Action: {action_names[action]}",
                ]

                for i, text in enumerate(info_texts):
                    surface = small_font.render(text, True, (255, 255, 255))
                    screen.blit(surface, (50, 20 + i*25))

                pygame.display.flip()
                time.sleep(0.1)  # 控制速度

            # 显示结果
            screen.fill((20, 20, 30))
            result = "SUCCESS!" if info.get('success') else "FAILED"
            color = (0, 255, 0) if info.get('success') else (255, 100, 100)

            result_text = font.render(result, True, color)
            stats_text = small_font.render(f"Steps: {steps} | Reward: {total_reward:.1f}", True, (255, 255, 255))
            continue_text = small_font.render("Press SPACE for next episode, ESC to quit", True, (200, 200, 200))

            screen.blit(result_text, (300, 250))
            screen.blit(stats_text, (250, 300))
            screen.blit(continue_text, (200, 350))

            pygame.display.flip()
            playing = False

    pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="观看AI玩游戏")
    parser.add_argument("--level", type=int, default=2, help="关卡 (1-5)")
    parser.add_argument("--episodes", type=int, default=10, help="最多观看局数")

    args = parser.parse_args()
    watch_ai(args.level, args.episodes)
