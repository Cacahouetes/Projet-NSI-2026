import pygame 
import math

from level import Level

running = True 
dt = 0.1
waveN = 0

pygame.init()
#pygame.mixer.init()
win = pygame.display.set_mode((1280, 736), vsync=1)
pygame.display.set_caption("jeu nsiissininisissini")
clock = pygame.time.Clock()

level = Level()

while running:
    dt = clock.tick(60) 
    keys = pygame.key.get_pressed()
    win.fill((0,0,0))   

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            level.NewBullet()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pass

    level.update(dt)
    level.draw(win)

    pygame.display.flip()
pygame.quit()

"""
player avec des armes 
doit eliminer les ennemis 


musique:


"""
