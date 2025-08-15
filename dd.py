import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Example background color
screen.fill((100, 150, 200))
pygame.display.flip()

# Create a black overlay surface
fade_surface = pygame.Surface((800, 600))
fade_surface.fill((0, 0, 0))  # Black
fade_surface.set_alpha(0)     # Start fully transparent

# Fade-out loop
for alpha in range(0, 255, 5):  # Increase alpha gradually
    fade_surface.set_alpha(alpha)
    screen.fill((100, 150, 200))  # Redraw background (or your game scene)
    screen.blit(fade_surface, (0, 0))
    pygame.display.update()
    clock.tick(30)  # Control fade speed

pygame.quit()
sys.exit()