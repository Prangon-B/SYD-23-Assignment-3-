
import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hero vs Robots")

# Load images and scale them
heart_img = pygame.image.load("heart.png")
heart_img = pygame.transform.scale(heart_img, (30, 30))

player_img = pygame.image.load("player.png")
player_img = pygame.transform.scale(player_img, (80, 80))

robot_img = pygame.image.load("robot.png")
robot_img = pygame.transform.scale(robot_img, (60, 60))

boss_img = pygame.image.load("alien.png")
boss_img = pygame.transform.scale(boss_img, (150, 150))

health_booster_img = pygame.image.load("health_booster.png")
health_booster_img = pygame.transform.scale(health_booster_img, (30, 30))

# Load sounds
shoot_sound = pygame.mixer.Sound("shoot.wav")
pygame.mixer.music.load("background.wav")
pause_music = "pause_music.wav"

# Fonts
font = pygame.font.SysFont("Arial", 30)
big_font = pygame.font.SysFont("Arial", 50)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Clock
clock = pygame.time.Clock()

# Global Variables
gravity = 1
level = 1
score = 0
game_paused = False
game_running = True
player_lives = 3

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = HEIGHT - 120
        self.vel_y = 0
        self.jumping = False
        self.health = 3

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
        if not self.jumping and keys[pygame.K_SPACE]:
            self.jumping = True
            self.vel_y = -15

        if self.jumping:
            self.rect.y += self.vel_y
            self.vel_y += gravity
            if self.rect.y >= HEIGHT - 120:
                self.rect.y = HEIGHT - 120
                self.jumping = False

    def draw(self):
        screen.blit(self.image, self.rect)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x + 60, y + 20))

    def update(self):
        self.rect.x += 10
        if self.rect.x > WIDTH:
            self.kill()

# Enemy class
class Robot(pygame.sprite.Sprite):
    def __init__(self, x, y, is_boss=False):
        super().__init__()
        self.is_boss = is_boss
        self.image = boss_img if is_boss else robot_img
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 20 if is_boss else 2

    def update(self):
        self.rect.x -= 2

    def draw(self):
        screen.blit(self.image, self.rect)

# Collectible class
class HealthBooster(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = health_booster_img
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self):
        screen.blit(self.image, self.rect)

# Show instructions at start
def show_start_screen():
    screen.fill(BLACK)
    lines = [
        "HOW TO PLAY:",
        "→ Move with arrow keys",
        "→ Press SPACE to jump",
        "→ Press F to shoot",
        "→ Defeat enemies to progress levels",
        "→ Collect green boosts for health",
        "→ Press P to pause and resume",
        "Press any key to start..."
    ]
    for i, line in enumerate(lines):
        text = font.render(line, True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 100 + i * 40))
    pygame.display.flip()
    wait_for_key()

# Transition screen
def show_transition(level_num):
    screen.fill(BLACK)
    msg = f"LEVEL {level_num} - Press 'R' to start"
    text = big_font.render(msg, True, WHITE)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                waiting = False

# Victory screen
def show_victory():
    screen.fill((80, 80, 80))
    msg = "🎉 YOU WIN! Press 'R' to restart"
    text = big_font.render(msg, True, BLACK)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                waiting = False

# Wait for key
def wait_for_key():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# Draw health and level
def draw_health(health, level):
    for i in range(health):
        screen.blit(heart_img, (10 + i * 35, 10))
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (10, 45))

# Main game loop
def run_game():
    global level, score, player_lives, game_paused

    player = Player()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    boosters = pygame.sprite.Group()

    pygame.mixer.music.play(-1)

    def spawn_enemies(level):
        count = 5 if level == 1 else 10
        for _ in range(count):
            x = random.randint(WIDTH, WIDTH + 500)
            y = HEIGHT - 100
            enemies.add(Robot(x, y))
        if level == 3:
            enemies.add(Robot(WIDTH + 600, HEIGHT - 150, is_boss=True))

    spawn_enemies(level)

    running = True
    while running:
        clock.tick(60)
        screen.fill((30 * level, 30 * level, 30 * level))  # Different solid colors

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    bullets.add(Bullet(player.rect.x, player.rect.y))
                    shoot_sound.play()
                if event.key == pygame.K_p:
                    game_paused = not game_paused
                    if game_paused:
                        pygame.mixer.music.pause()
                        pygame.mixer.music.load(pause_music)
                        pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("background.wav")
                        pygame.mixer.music.play(-1)

        if game_paused:
            text = big_font.render("PAUSED", True, WHITE)
            screen.blit(text, (WIDTH//2 - 100, HEIGHT//2))
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()
        player.update(keys)

        bullets.update()
        enemies.update()

        for bullet in bullets:
            for enemy in enemies:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.health -= 1
                    bullet.kill()
                    if enemy.health <= 0:
                        enemy.kill()
                        score += 10

        for booster in boosters:
            if player.rect.colliderect(booster.rect):
                if player.health < 3:
                    player.health += 1
                booster.kill()

        if len(enemies) == 0:
            level += 1
            if level > 3:
                show_victory()
                level = 1
                score = 0
                player_lives = 3
                return run_game()
            show_transition(level)
            spawn_enemies(level)

        player.draw()
        bullets.draw(screen)

        for enemy in enemies:
            enemy.draw()
        for booster in boosters:
            booster.draw()

        draw_health(player.health, level)

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH - 150, 10))

        pygame.display.flip()

# Run everything
show_start_screen()
run_game()
