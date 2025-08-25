import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Get screen size
window = pygame.display.Info()
screen_width = window.current_w
screen_height = window.current_h

# Create the game window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Math Runner - Enemies Added")

# Clock to control frame rate
clock = pygame.time.Clock()
FPS = 60

# Font for displaying equations
font = pygame.font.SysFont(None, 50)

# Background class
class Background:
    def __init__(self, color=(50, 150, 200)):
        self.color = color

    def draw(self, surface):
        surface.fill(self.color)

# Player class
class Player:
    def __init__(self, x, y, width=50, height=80, color=(255, 50, 50)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.vel_x = 5  # Horizontal movement speed

    def handle_input(self, keys):
        if keys[pygame.K_a]:
            self.rect.x -= self.vel_x
        if keys[pygame.K_d]:
            self.rect.x += self.vel_x

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Equation class
class Equation:
    def __init__(self):
        self.equation = ""
        self.answer = 0

    def generate(self):
        num1 = random.randint(1, 50)
        num2 = random.randint(1, 50)
        op = random.choice(["+", "-", "*", "/"])
        if op == "/":
            num2 = random.randint(1, 10)
            self.answer = round(num1 / num2, 2)
        else:
            self.answer = eval(f"{num1}{op}{num2}")
        self.equation = f"{num1} {op} {num2} = {self.answer}"
        return self.equation

    def draw(self, surface, x, y):
        text = font.render(self.equation, True, (0, 0, 0))
        surface.blit(text, (x, y))

# Enemy class
class Enemy:
    def __init__(self, x, y, width=40, height=60, color=(0, 0, 0), speed=5):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed  # Move left

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Create instances
background = Background()
player = Player(screen_width//2 - 25, screen_height - 100)
equation = Equation()
equation.generate()

enemies = []

# Game loop
running = True
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle player input
    player.handle_input(keys)

    # Spawn enemies randomly
    if random.randint(0, 100) < 2:  # 2% chance each frame
        enemy_y = screen_height - 100  # same level as player
        enemies.append(Enemy(screen_width, enemy_y))

    # Update enemies
    for enemy in enemies:
        enemy.update()

    # Remove off-screen enemies
    enemies = [e for e in enemies if e.rect.right > 0]

    # Draw everything
    background.draw(screen)
    player.draw(screen)
    equation.draw(screen, 50, 50)
    for enemy in enemies:
        enemy.draw(screen)

    # Update the display
    pygame.display.update()

    # Maintain 60 FPS
    clock.tick(FPS)

# Quit pygame
pygame.quit()
sys.exit()
