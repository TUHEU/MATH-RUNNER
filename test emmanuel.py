current_time = pygame.time.get_ticks()

# Player attack input
if keys[pygame.K_SPACE]:
    player.attack(current_time)

# Collision check with enemies
for enemy in enemies:
    if player.attacking and player.rect.colliderect(enemy.rect):
        enemy.die()
        player.attacking = False
