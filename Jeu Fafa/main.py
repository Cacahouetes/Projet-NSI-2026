import pygame 
import math
from level import Level

running = True 
dt = 0.1

pygame.init()
pygame.font.init()
pygame.mixer.init()
font = pygame.font.SysFont('Arial', 40)

win = pygame.display.set_mode((1280, 736), vsync=1)
pygame.display.set_caption("jeu nsiissininisissini")
clock = pygame.time.Clock()

level = Level()

pygame.mixer.music.load('Assets/jeu arcade/musique/onlyvoicemusic.mp3')
pygame.mixer.music.play(-1) #-1 pour mettre la musique en boucle

#boucle principale du jeu
while running:
    keys = pygame.key.get_pressed()
    dt = clock.tick(60) 
    events = pygame.event.get()
    
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    win.fill((60,48,39))
    level.update(dt, events)
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
