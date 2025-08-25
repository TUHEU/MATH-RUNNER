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
pygame.display.set_caption("Math Runner - Main Loop Added")

# Clock to control frame rate
clock = pygame.time.Clock()
FPS = 60

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill background with black
    screen.fill((0, 0, 0))

    # Update the display
    pygame.display.update()

    # Maintain 60 FPS
    clock.tick(FPS)

# Quit pygame
pygame.quit()
sys.exit()
