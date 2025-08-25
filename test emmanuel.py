current_time = pygame.time.get_ticks()

# Player attack input
if keys[pygame.K_SPACE]:
    player.attack(current_time)

# Collision check with enemies
for enemy in enemies:
    if player.attacking and player.rect.colliderect(enemy.rect):
        enemy.die()
        player.attacking = False
# ... (Keep all imports and existing classes same as commit 13)

# Initialize score
score = 0
font_score = pygame.font.Font(None, 40)  # default font, size 40

# In main loop, after checking enemy deaths
for enemy in enemies:
    if not enemy.alive and not enemy.dying:
        score += 10  # Increase score for each defeated enemy
        enemies.remove(enemy)  # Remove enemy from list
