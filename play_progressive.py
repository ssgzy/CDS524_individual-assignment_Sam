"""手动玩ShadowBox游戏 - 从Level 1到Level 5自动升级"""
import pygame
import sys
from game.environment import ShadowBoxEnv

class ShadowBoxGame:
    """ShadowBox游戏主类"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("ShadowBox - 手动游戏")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.current_level = 1
        self.max_level = 5
        self.env = None
        self.step_count = 0  # 添加步数计数器
        self.load_level(self.current_level)

        # 游戏状态
        self.running = True
        self.paused = False
        self.show_help = False

    def load_level(self, level_id):
        """加载关卡"""
        if self.env:
            self.env.close()
        self.env = ShadowBoxEnv(level_id=level_id)
        self.env.reset()
        self.current_level = level_id
        self.step_count = 0  # 重置步数
        print(f"\n🎮 加载 Level {level_id}")
        print(f"   Max steps: {self.env.max_steps}")
        print(f"   Boxes: {len(self.env.boxes)}")

    def handle_input(self):
        """处理输入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_h:
                    self.show_help = not self.show_help

                elif event.key == pygame.K_r:
                    self.env.reset()
                    self.step_count = 0  # 重置步数
                    print(f"🔄 重置 Level {self.current_level}")

                elif event.key == pygame.K_n:
                    # 下一关
                    if self.current_level < self.max_level:
                        self.load_level(self.current_level + 1)
                    else:
                        print("已经是最后一关！")

                elif event.key == pygame.K_p:
                    # 上一关
                    if self.current_level > 1:
                        self.load_level(self.current_level - 1)
                    else:
                        print("已经是第一关！")

                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                # 移动控制
                elif not self.paused:
                    action = None
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        action = 1  # UP
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        action = 2  # DOWN
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        action = 3  # LEFT
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        action = 4  # RIGHT

                    if action is not None:
                        _, reward, done, info = self.env.step(action)
                        self.step_count += 1  # 增加步数

                        if info.get('success'):
                            print(f"🎉 Level {self.current_level} 完成！")
                            print(f"   步数: {self.step_count}")

                            # 自动升级到下一关
                            if self.current_level < self.max_level:
                                print(f"⬆️  自动升级到 Level {self.current_level + 1}")
                                pygame.time.wait(1000)  # 等待1秒
                                self.load_level(self.current_level + 1)
                            else:
                                print("🏆 恭喜！你完成了所有关卡！")
                                pygame.time.wait(2000)
                                self.running = False

                        elif done:
                            if info.get('deadlock'):
                                print("❌ 死锁！按R重置")
                            elif info.get('timeout'):
                                print("⏱️  超时！按R重置")

    def render(self):
        """渲染游戏画面"""
        self.screen.fill((20, 20, 30))

        # 绘制地图
        cell_size = 40
        offset_x, offset_y = 50, 100

        # 获取地图尺寸
        max_x = 0
        max_y = 0
        for y in range(50):
            for x in range(50):
                if self.env.is_wall((x, y)):
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)

        if self.env.boxes:
            max_x = max(max_x, max(box.pos[0] for box in self.env.boxes))
            max_y = max(max_y, max(box.pos[1] for box in self.env.boxes))
        if self.env.targets:
            max_x = max(max_x, max(target.pos[0] for target in self.env.targets))
            max_y = max(max_y, max(target.pos[1] for target in self.env.targets))

        max_x = max(max_x, self.env.player.pos[0]) + 1
        max_y = max(max_y, self.env.player.pos[1]) + 1

        # 绘制格子
        for y in range(max_y):
            for x in range(max_x):
                rect = pygame.Rect(offset_x + x*cell_size, offset_y + y*cell_size,
                                 cell_size, cell_size)

                if self.env.is_wall((x, y)):
                    pygame.draw.rect(self.screen, (100, 100, 100), rect)
                else:
                    pygame.draw.rect(self.screen, (40, 40, 50), rect)

                pygame.draw.rect(self.screen, (60, 60, 70), rect, 1)

        # 绘制目标
        for target in self.env.targets:
            tx, ty = target.pos
            rect = pygame.Rect(offset_x + tx*cell_size + 5,
                             offset_y + ty*cell_size + 5,
                             cell_size-10, cell_size-10)
            pygame.draw.rect(self.screen, (255, 200, 0), rect)

        # 绘制箱子
        for box in self.env.boxes:
            bx, by = box.pos
            on_target = self.env.is_box_on_target(box)
            color = (0, 255, 0) if on_target else (200, 100, 50)
            rect = pygame.Rect(offset_x + bx*cell_size + 8,
                             offset_y + by*cell_size + 8,
                             cell_size-16, cell_size-16)
            pygame.draw.rect(self.screen, color, rect)

        # 绘制玩家
        px, py = self.env.player.pos
        pygame.draw.circle(self.screen, (100, 150, 255),
                         (offset_x + px*cell_size + cell_size//2,
                          offset_y + py*cell_size + cell_size//2),
                         cell_size//3)

        # 显示信息
        info_texts = [
            f"Level: {self.current_level}/{self.max_level}",
            f"Steps: {self.step_count}/{self.env.max_steps}",
            f"Boxes: {sum(1 for b in self.env.boxes if self.env.is_box_on_target(b))}/{len(self.env.boxes)}",
        ]

        for i, text in enumerate(info_texts):
            surface = self.small_font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (50, 20 + i*25))

        # 显示帮助
        if self.show_help:
            help_texts = [
                "控制:",
                "  方向键/WASD - 移动",
                "  R - 重置关卡",
                "  N - 下一关",
                "  P - 上一关",
                "  H - 显示/隐藏帮助",
                "  ESC - 退出",
            ]
            help_y = 200
            for text in help_texts:
                surface = self.small_font.render(text, True, (255, 255, 100))
                self.screen.blit(surface, (500, help_y))
                help_y += 25
        else:
            hint = self.small_font.render("按 H 显示帮助", True, (150, 150, 150))
            self.screen.blit(hint, (500, 20))

        # 暂停提示
        if self.paused:
            pause_text = self.font.render("PAUSED", True, (255, 100, 100))
            self.screen.blit(pause_text, (350, 300))

        pygame.display.flip()

    def run(self):
        """主游戏循环"""
        print("\n" + "="*60)
        print("🎮 ShadowBox - 手动游戏")
        print("="*60)
        print("从 Level 1 开始，完成后自动升级到下一关！")
        print("\n控制:")
        print("  方向键/WASD - 移动")
        print("  R - 重置  N - 下一关  P - 上一关")
        print("  H - 帮助  ESC - 退出")
        print("="*60)

        while self.running:
            self.handle_input()
            self.render()
            self.clock.tick(60)

        self.env.close()
        pygame.quit()
        print("\n游戏结束！")


if __name__ == "__main__":
    game = ShadowBoxGame()
    game.run()
