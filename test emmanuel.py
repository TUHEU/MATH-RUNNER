# ... (Keep all imports and previous classes same as commit 16)

# Player jump variables
jump_strength = -15
gravity = 0.8
is_jumping = False
player_vel_y = 0

# Update Player class with jump animation
class Player:
    def __init__(self, x, y, width=50, height=80):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (0, 100, 200)
        self.attacking = False
        self.attack_cooldown = 1000
        self.last_attack_time = 0
        self.is_jumping = False
        self.vel_y = 0

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.vel_y = jump_strength

    def update(self):
        # Gravity
        if self.is_jumping:
            self.vel_y += gravity
            self.rect.y += int(self.vel_y)
            if self.rect.bottom >= screen_height - 50:
                self.rect.bottom = screen_height - 50
                self.is_jumping = False
                self.vel_y = 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        # Optional: add jump color change or animation
        if self.is_jumping:
            pygame.draw.rect(surface, (255, 255, 0), self.rect)  # yellow while jumping
# Check jump input
keys = pygame.key.get_pressed()
if keys[pygame.K_w] or keys[pygame.K_SPACE]:
    player.jump()

# Update player position
player.update()

# Draw player
player.draw(screen)
