import pygame 
import math

from level import Level

running = True 
dt = 0.1

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Arial', 40)

pygame.mixer.init()
win = pygame.display.set_mode((1280, 736), vsync=1)
pygame.display.set_caption("jeu nsiissininisissini")
clock = pygame.time.Clock()

level = Level()

pygame.mixer.music.load('Assets/jeu arcade/musique/onlyvoicemusic.mp3')
pygame.mixer.music.play(-1)

while running:
    dt = clock.tick(60) 
    keys = pygame.key.get_pressed()
    win.fill((0,0,0))   

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and level.gun.currGunID != 2:
            level.NewBullet()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pass
                
    if  pygame.mouse.get_pressed()[0] and level.gun.currGunID == 2:
        level.NewBullet()

    level.update(dt)
    level.draw(win)

    win.blit(font.render(f"Score: {level.player.score}", True, (222,222,222)), (600, 30))
    win.blit(font.render(f"Wave: {level.waveN}", True, (222,222,222)), (300, 30))
    pygame.display.flip()
pygame.quit()

"""
player avec des armes 
doit eliminer les ennemis 


musique:


"""
