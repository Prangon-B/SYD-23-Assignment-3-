# Simple 2D Side Scrolling Game using Pygame
import pygame
import random

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animal Hero Side Scroller")

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Game constants
GRAVITY = 1
PLAYER_SPEED = 5
JUMP_POWER = 15
PROJECTILE_SPEED = 10

# Load fonts
font = pygame.font.SysFont("Arial", 24)

# Player class
class Player(pygame.sprite.Sprite):
    def _init_(self):
        super()._init_()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = HEIGHT - 150
        self.vel_y = 0
        self.jumping = False
        self.health = 100
        self.lives = 3
        self.score = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if not self.jumping and keys[pygame.K_SPACE]:
            self.jumping = True
            self.vel_y = -JUMP_POWER

        if self.jumping:
            self.rect.y += self.vel_y
            self.vel_y += GRAVITY
            if self.rect.y >= HEIGHT - 150:
                self.rect.y = HEIGHT - 150
                self.jumping = False

    def shoot(self):
        projectile = Projectile(self.rect.right, self.rect.centery)
        all_sprites.add(projectile)
        projectiles.add(projectile)


# Projectile class
class Projectile(pygame.sprite.Sprite):
    def _init_(self, x, y):
        super()._init_()
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x += PROJECTILE_SPEED
        if self.rect.x > WIDTH:
            self.kill()


# Enemy class
class Enemy(pygame.sprite.Sprite):
    def _init_(self, x):
        super()._init_()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = HEIGHT - 150
        self.health = 30

    def update(self):
        self.rect.x -= 2
        if self.rect.right < 0:
            self.kill()


# Collectible class
class Collectible(pygame.sprite.Sprite):
    def _init_(self, x, kind):
        super()._init_()
        self.image = pygame.Surface((30, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = HEIGHT - 160
        self.kind = kind  # 'health' or 'life'

# Game over screen
def game_over():
    screen.fill(BLACK)
    msg = font.render("Game Over! Press R to Restart", True, WHITE)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False

# Setup
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
collectibles = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

level = 1

# Level function
def spawn_level(level):
    for i in range(level * 5):
        enemy = Enemy(WIDTH + i * 100)
        all_sprites.add(enemy)
        enemies.add(enemy)
    for i in range(level):
        collectible = Collectible(WIDTH + 200 * i, 'health')
        all_sprites.add(collectible)
        collectibles.add(collectible)

spawn_level(level)

# Main loop
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                player.shoot()

    all_sprites.update()

    # Check projectile collisions
    hits = pygame.sprite.groupcollide(enemies, projectiles, False, True)
    for enemy in hits:
        enemy.health -= 10
        if enemy.health <= 0:
            enemy.kill()
            player.score += 10

    # Check player collisions
    for collectible in pygame.sprite.spritecollide(player, collectibles, True):
        if collectible.kind == 'health':
            player.health = min(player.health + 20, 100)
        elif collectible.kind == 'life':
            player.lives += 1

    if pygame.sprite.spritecollide(player, enemies, False):
        player.health -= 1
        if player.health <= 0:
            player.lives -= 1
            player.health = 100
            if player.lives <= 0:
                game_over()
                level = 1
                player.lives = 3
                player.score = 0
                spawn_level(level)

    # Advance level
    if len(enemies) == 0:
        level += 1
        spawn_level(level)

    # Draw
    screen.fill(WHITE)
    all_sprites.draw(screen)

    # UI
    score_text = font.render(f"Score: {player.score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    health_text = font.render(f"Health: {player.health}", True, BLACK)
    screen.blit(health_text, (10, 40))
    lives_text = font.render(f"Lives: {player.lives}", True, BLACK)
    screen.blit(lives_text, (10, 70))

    pygame.display.flip()

pygame.quit()
