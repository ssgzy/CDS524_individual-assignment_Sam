"""Watch trained AI play the game in real-time."""

from __future__ import annotations

import argparse
import time
import pygame
import torch

from ai.rainbow_agent import RainbowDQNAgent
from ai.enhanced_env import EnhancedShadowBoxEnv
from game.renderer import IsometricRenderer, COLOR_MAP


def watch_ai_play(
    model_path: str,
    level_id: int = 1,
    num_episodes: int = 10,
    fps: int = 5,
):
    """Watch AI play the game."""

    # Initialize pygame
    pygame.init()
    screen_width, screen_height = 1280, 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(f"🤖 Rainbow DQN Playing - Level {level_id}")
    clock = pygame.time.Clock()

    # Create renderer
    renderer = IsometricRenderer(
        screen,
        tile_w=64,
        tile_h=32,
        screen_width=screen_width,
        screen_height=screen_height,
    )

    # Fonts
    font_large = pygame.font.SysFont("Arial", 36, bold=True)
    font_medium = pygame.font.SysFont("Arial", 24)
    font_small = pygame.font.SysFont("Arial", 18)

    # Colors
    bg_color = (30, 30, 40)
    text_color = (255, 255, 255)
    success_color = (100, 255, 100)
    fail_color = (255, 100, 100)

    # Create environment
    env = EnhancedShadowBoxEnv(level_id=level_id)

    # Create and load agent
    agent = RainbowDQNAgent(
        input_channels=7,
        action_dim=5,
        use_noisy=True,
        use_curiosity=True,
    )

    try:
        agent.load(model_path)
        print(f"✅ Model loaded from {model_path}")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        pygame.quit()
        return

    action_names = ["⬆️ UP", "⬇️ DOWN", "⬅️ LEFT", "➡️ RIGHT", "🚪 ENTER"]

    print("=" * 80)
    print(f"🎮 Watching AI Play Level {level_id}")
    print("=" * 80)
    print("Controls:")
    print("  SPACE - Pause/Resume")
    print("  UP/DOWN - Adjust speed")
    print("  R - Restart episode")
    print("  ESC - Exit")
    print("=" * 80)

    success_count = 0
    paused = False

    try:
        for episode in range(1, num_episodes + 1):
            state = env.reset()
            episode_reward = 0.0
            episode_length = 0
            done = False

            print(f"\n🎮 Episode {episode}/{num_episodes}")

            while not done:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            raise KeyboardInterrupt
                        if event.key == pygame.K_SPACE:
                            paused = not paused
                            print(f"{'⏸️  Paused' if paused else '▶️  Resumed'}")
                        if event.key == pygame.K_UP:
                            fps = min(60, fps + 2)
                            print(f"Speed: {fps} FPS")
                        if event.key == pygame.K_DOWN:
                            fps = max(1, fps - 2)
                            print(f"Speed: {fps} FPS")
                        if event.key == pygame.K_r:
                            print("🔄 Restarting episode...")
                            break

                if paused:
                    time.sleep(0.1)
                    continue

                # Select action (evaluation mode)
                action = agent.select_action(state, eval_mode=True)

                # Take step
                next_state, reward, done, info = env.step(action)

                # Render game
                screen.fill(bg_color)

                # Render map
                render_map(screen, renderer, env.env)

                # Render info panel
                render_info_panel(
                    screen, font_large, font_medium, font_small,
                    episode, num_episodes, episode_length, action_names[action],
                    reward, episode_reward, success_count, done, info,
                    text_color, success_color, fail_color
                )

                pygame.display.flip()
                clock.tick(fps)

                # Update
                state = next_state
                episode_reward += reward
                episode_length += 1

            # Episode finished
            if info.get("success"):
                success_count += 1
                print(f"✅ Success! Reward: {episode_reward:.2f}, Steps: {episode_length}")
            else:
                reason = "Timeout" if info.get("timeout") else "Deadlock" if info.get("deadlock") else "Failed"
                print(f"❌ {reason}. Reward: {episode_reward:.2f}, Steps: {episode_length}")

            # Show result for 2 seconds
            for _ in range(int(fps * 2)):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        raise KeyboardInterrupt

                screen.fill(bg_color)
                render_map(screen, renderer, env.env)
                render_info_panel(
                    screen, font_large, font_medium, font_small,
                    episode, num_episodes, episode_length, action_names[action],
                    reward, episode_reward, success_count, done, info,
                    text_color, success_color, fail_color
                )
                pygame.display.flip()
                clock.tick(fps)

    except KeyboardInterrupt:
        print("\n⚠️  Stopped by user")

    finally:
        print("\n" + "=" * 80)
        print("📊 Final Statistics:")
        print(f"   Episodes Played: {episode}")
        print(f"   Success Count: {success_count}")
        print(f"   Success Rate: {(success_count / episode * 100):.1f}%")
        print("=" * 80)

        pygame.quit()
        env.close()


def render_map(screen, renderer, env):
    """Render the game map."""
    # Draw floor tiles
    for y in range(env.map_height):
        for x in range(env.map_width):
            iso_x, iso_y = renderer.grid_to_iso(x, y)
            screen.blit(renderer.sprites["floor"], (iso_x - 32, iso_y - 16))

            # Draw walls
            if env.is_wall((x, y)):
                screen.blit(renderer.sprites["wall"], (iso_x - 32, iso_y - 48))

    # Draw targets
    for target in env.targets:
        iso_x, iso_y = renderer.grid_to_iso(target.x, target.y)
        color = COLOR_MAP.get(target.color, (200, 200, 200))
        pygame.draw.circle(screen, color, (iso_x, iso_y), 12, 3)

    # Draw gates
    for gate in env.gates:
        iso_x, iso_y = renderer.grid_to_iso(gate.x, gate.y)
        sprite = "gate_open" if gate.is_open else "gate_closed"
        screen.blit(renderer.sprites[sprite], (iso_x - 32, iso_y - 48))

    # Draw pressure plates
    for plate in env.pressure_plates:
        iso_x, iso_y = renderer.grid_to_iso(plate.x, plate.y)
        color = (255, 255, 100) if plate.is_pressed else (150, 150, 150)
        pygame.draw.circle(screen, color, (iso_x, iso_y), 8)

    # Draw boxes
    for box in env.boxes:
        iso_x, iso_y = renderer.grid_to_iso(box.x, box.y)
        sprite_name = f"box_{box.color.name.lower()}"
        screen.blit(renderer.sprites[sprite_name], (iso_x - 32, iso_y - 48))

        # Highlight if on target
        if env.is_box_on_target(box):
            pygame.draw.circle(screen, (100, 255, 100), (iso_x, iso_y - 20), 15, 3)

    # Draw player
    iso_x, iso_y = renderer.grid_to_iso(env.player.x, env.player.y)
    screen.blit(renderer.sprites["player"], (iso_x - 32, iso_y - 64))


def render_info_panel(screen, font_large, font_medium, font_small,
                     episode, num_episodes, step, action, reward, total_reward,
                     success_count, done, info, text_color, success_color, fail_color):
    """Render information panel."""
    panel_x = 20
    panel_y = 20

    # Title
    title = font_large.render("🤖 Rainbow DQN", True, text_color)
    screen.blit(title, (panel_x, panel_y))

    y_offset = 70

    # Episode info
    info_lines = [
        f"Episode: {episode}/{num_episodes}",
        f"Step: {step}",
        f"Action: {action}",
        f"Step Reward: {reward:+.2f}",
        f"Total Reward: {total_reward:+.2f}",
        f"Success: {success_count}/{episode-1 if done else episode}",
    ]

    for line in info_lines:
        text = font_medium.render(line, True, text_color)
        screen.blit(text, (panel_x, panel_y + y_offset))
        y_offset += 35

    # Status
    if done:
        y_offset += 10
        if info.get("success"):
            status = font_large.render("✅ SUCCESS!", True, success_color)
        else:
            reason = "TIMEOUT" if info.get("timeout") else "DEADLOCK" if info.get("deadlock") else "FAILED"
            status = font_large.render(f"❌ {reason}", True, fail_color)
        screen.blit(status, (panel_x, panel_y + y_offset))
        y_offset += 50

    # Controls
    y_offset += 20
    controls = [
        "Controls:",
        "  SPACE - Pause/Resume",
        "  UP/DOWN - Speed",
        "  R - Restart",
        "  ESC - Exit",
    ]

    for line in controls:
        text = font_small.render(line, True, (180, 180, 180))
        screen.blit(text, (panel_x, panel_y + y_offset))
        y_offset += 25


def main():
    parser = argparse.ArgumentParser(description="Watch AI play the game")
    parser.add_argument("--model", type=str, required=True, help="Path to model checkpoint")
    parser.add_argument("--level", type=int, default=1, help="Level ID")
    parser.add_argument("--episodes", type=int, default=10, help="Number of episodes to watch")
    parser.add_argument("--fps", type=int, default=5, help="Playback speed (FPS)")

    args = parser.parse_args()

    watch_ai_play(
        model_path=args.model,
        level_id=args.level,
        num_episodes=args.episodes,
        fps=args.fps,
    )


if __name__ == "__main__":
    main()
