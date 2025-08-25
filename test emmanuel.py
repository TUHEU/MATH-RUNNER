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
pygame.display.set_caption("Math Runner - Initial Setup")

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill background with black
    screen.fill((0, 0, 0))

    pygame.display.update()

# Quit pygame
pygame.quit()
sys.exit()
