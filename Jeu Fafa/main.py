import pygame 
from player import Player
from entity import Entity
from bullet import Bullet
from tile import Tile
from gun import Gun

import math
pygame.init()
win = pygame.display.set_mode((1280, 736), vsync=1)
pygame.display.set_caption("jeu nsiissininisissini")
clock = pygame.time.Clock()
tiles_img = [pygame.image.load("Assets/jeu arcade/fg.png").convert_alpha(), pygame.image.load("Assets/jeu arcade/bg.png").convert_alpha()
]

entity_sprites = pygame.sprite.Group()
ennemy_sprites = pygame.sprite.Group()

tile_sprites = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()

player = Player((255,0,0), 50, 300, 50)
gun = Gun()
entity_sprites.add(player)

running = True 
dt = 0.1
TILE_SIZE = 32 
for i in range(len(tiles_img)):
    tiles_img[i] = pygame.transform.scale(tiles_img[i], (TILE_SIZE, TILE_SIZE))
tiles = [[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1], 
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         #[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
         [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1]
         ]
tileNumX = len(tiles[0])
tileNumY = len(tiles)

for y in range(len(tiles)):
        for x in range(len(tiles[0])):
            newTile = Tile()
            newTile.x = x * TILE_SIZE
            newTile.y = y * TILE_SIZE
            newTile.rect.x = x * TILE_SIZE
            newTile.rect.y = y * TILE_SIZE
            newTile.tileID = tiles[y][x]
            newTile.image = tiles_img[newTile.tileID].convert()
            tile_sprites.add(newTile)

#spawn entities a des positions aléatoires
for xpos in [100, 250, 500, 444, 602]:
    newent = Entity((xpos%255, 200,200), 20, xpos, 0, (xpos%100)/100)
    ennemy_sprites.add(newent)
    entity_sprites.add(newent)

scroll = pygame.math.Vector2(0,0)

while running:
    isHitPressed = False
    dt = clock.tick(60) 
    keys = pygame.key.get_pressed()
    win.fill((0,0,0))   

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            
            bullet = Bullet(gun.tipx + scroll.x, gun.tipy + scroll.y , msPlDir)
            bullet_sprites.add(bullet)
            gun.shootFlag = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                isHitPressed = True

    #scroll
    scroll.x += (player.posX - scroll.x - 1280//2)//10
    scroll.y += (player.posY - scroll.y - 786//2)//5
    
    tile_sprites.update(scroll)

    #update sprites
    for spr in entity_sprites: 
        if spr.type == 0:
            if spr.posX - player.posX < 0:
                spr.velocity[0] = spr.SPEED
            else:
                spr.velocity[0] = -spr.SPEED 
    for coll in pygame.sprite.spritecollide(player, entity_sprites, False):  
        if isHitPressed and coll != player:
            coll.takedmg(0.1)
    
    entity_sprites.update(dt, tile_sprites, scroll)
    
    #update bullets 
    for bul in bullet_sprites:
        bul.update(dt, scroll)
        for hit_tile in pygame.sprite.spritecollide(bul, tile_sprites, False):
            if hit_tile.tileID > 0: 
                bul.kill()
                break

        for ennemy in ennemy_sprites:
            if ennemy.rect.clipline((bul.rectbefore.x, bul.rectbefore.y), (bul.rect.x, bul.rect.y)):
                ennemy.takedmg(0.1)
                bul.kill()
                break

    tile_sprites.draw(win)
    bullet_sprites.draw(win)
    entity_sprites.draw(win)

    #get angle of player mouse line
    lx = pygame.mouse.get_pos()[0] - player.rect.centerx 
    ly = player.rect.centery -  pygame.mouse.get_pos()[1]
    msPlDir = math.atan2(ly, lx)

    #dessiner le pistolet
    gun.update(win, player, msPlDir*180/3.14159265)

    pygame.display.flip()
pygame.quit()

"""


player avec des armes 
doit eliminer les ennemis 


musique:


"""
