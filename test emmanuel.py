import pygame

# Background class
class Background:
    def __init__(self, image_path, speed):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(0,0))
        self.speed = speed
        self.width = self.rect.width

    def update(self, moving_right=True):
        if moving_right:
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed

        # Loop the background for continuous scroll
        if self.rect.right <= screen_width:
            self.rect.left = 0
        if self.rect.left >= 0:
            self.rect.right = self.width

    def draw(self, surface):
        surface.blit(self.image, self.rect)
# Initialize background
background = Background("Assets/Backgrounds/1.png", speed=3)

# In main game loop
keys = pygame.key.get_pressed()
if keys[pygame.K_d]:
    background.update(moving_right=True)
elif keys[pygame.K_a]:
    background.update(moving_right=False)

background.draw(screen)
