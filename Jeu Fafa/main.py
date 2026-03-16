import pygame 
import math

from level import Level

running = True 
dt = 0.1

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Arial', 40)

#pygame.mixer.init()
win = pygame.display.set_mode((1280, 736), vsync=1)
pygame.display.set_caption("jeu nsiissininisissini")
clock = pygame.time.Clock()

level = Level()

#pygame.mixer.music.load('Assets/jeu arcade/musique/onlyvoicemusic.mp3')
#pygame.mixer.music.play(-1) #-1 pour mettre la musique en boucle

#boucle principale du jeu
while running:
    dt = clock.tick(60) 
    keys = pygame.key.get_pressed()
    win.fill((60,48,39))   

    #Entree du jeu (input)
    for event in pygame.event.get():
        
        if not level.player.isDead:
            if event.type == pygame.MOUSEBUTTONDOWN and level.gun.currGunID != 2  and pygame.mouse.get_pressed()[0]:
                level.NewBullet()
            
            if event.type == pygame.MOUSEWHEEL:
                
                if event.y == -1:
                    level.gun.currGunID-=1
                    if level.gun.currGunID <0:
                        level.gun.currGunID = level.gun.unlockedGuns-1
                    
                elif event.y == 1:
                    level.gun.currGunID+=1
                    if level.gun.currGunID >= level.gun.unlockedGuns:
                        level.gun.currGunID = 0

        if event.type == pygame.QUIT:
            running = False
            
    if  pygame.mouse.get_pressed()[0] and level.gun.currGunID == 2:
        level.NewBullet()

    level.update(dt)
    level.draw(win)

    pygame.display.flip()
pygame.quit()

"""
change_gun.wav
jump.wav
get_point.wav
get_health.wav
get_new_gun.wav
new_wave.wav
"""
