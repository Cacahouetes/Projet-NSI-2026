import pygame 
from player import Player
from bullet import Bullet

pygame.init()
win = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("jeu nsiissininisissini")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
player = Player((255,0,0), 50)
all_sprites.add(player)
running = True 
dt = 0.1
while running:

    dt = clock.tick(60)  
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_o:
                ddir = 1 
                if player.velocity[0] > 0:
                    ddir = 1 
                else:
                    ddir = -1 

                all_sprites.add(Bullet(player.x, player.y, ddir))
    keys = pygame.key.get_pressed()

    all_sprites.update(dt)
    
    win.fill((0,0,0))

    all_sprites.draw(win)

    pygame.display.flip()

pygame.quit()

"""
player avec des armes 
doit eliminer les ennemis 



"""
