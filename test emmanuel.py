# ... (Keep all imports and initial setup same as commit 10)

# Enemy class with death animation
class Enemy:
    def __init__(self, x, y, width=40, height=60, color=(0, 0, 0), speed=5):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = speed
        self.alive = True
        self.dying = False
        self.death_timer = 0
        self.max_death_time = 15  # frames for death animation

    def update(self):
        if self.alive and not self.dying:
            self.rect.x -= self.speed
        elif self.dying:
            self.death_timer += 1
            if self.death_timer >= self.max_death_time:
                self.alive = False
                self.dying = False

    def draw(self, surface):
        if self.alive:
            # Draw enemy normally
            pygame.draw.rect(surface, self.color, self.rect)
        elif self.dying:
            # Draw fading death animation
            alpha = max(0, 255 - int((self.death_timer/self.max_death_time)*255))
            death_surface = pygame.Surface((self.rect.width, self.rect.height))
            death_surface.fill((255,0,0))
            death_surface.set_alpha(alpha)
            surface.blit(death_surface, (self.rect.x, self.rect.y))

    def die(self):
        self.dying = True
        self.death_timer = 0

# ... (Keep Player, Equation, Background classes same as commit 10)

# Collision check for attack
for enemy in enemies:
    if player.attacking and player.attack_rect.colliderect(enemy.rect):
        enemy.die()  # trigger death animation
        player.attacking = False
