        if(not immortal):
                screen.blit(player.playersuf,player.playerrect)
            elif(immortal and dt%2==0):
                screen.blit(player.playersuf,player.playerrect)
            if (backgrounds[k].rect.right <= x + 250 * unitx):
                fade_surface.set_alpha(alpha)
                alpha += 5
                screen.blit(fade_surface, (0, 0))