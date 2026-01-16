import pygame 
from player import Player
from bullet import Bullet

pygame.init()
win = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("jeu nsiissininisissini")
clock = pygame.time.Clock()
tiles_img = [pygame.image.load("/home/pc/Documents/NSI/Projet-NSI-2026/Assets/jeu arcade/bg.png").convert_alpha(), pygame.image.load("/home/pc/Documents/NSI/Projet-NSI-2026/Assets/jeu arcade/bg.png").convert_alpha()
]
all_sprites = pygame.sprite.Group()
player = Player((255,0,0), 50)
all_sprites.add(player)
running = True 
dt = 0.1

tiles = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
         ]

while running:

    #load tiles
    for y in len(tiles):
        for x in len(tiles[0]):
            
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
