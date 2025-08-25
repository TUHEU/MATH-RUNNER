import pygame
import sys

# Initialize pygame
pygame.init()

# Get screen size
window = pygame.display.Info()
screen_width = window.current_w
screen_height = window.current_h

# Create the game window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Math Runner - Player Added")

# Clock to control frame rate
clock = pygame.time.Clock()
FPS = 60

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

# Create instances
background = Background()
player = Player(screen_width//2 - 25, screen_height - 100)

# Game loop
running = True
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle player input
    player.handle_input(keys)

    # Draw everything
    background.draw(screen)
    player.draw(screen)

    # Update the display
    pygame.display.update()

    # Maintain 60 FPS
    clock.tick(FPS)

# Quit pygame
pygame.quit()
sys.exit()
