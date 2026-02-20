import pygame 
from player import Player
from entity import Entity
from bullet import Bullet
from tile import Tile
pygame.init()
win = pygame.display.set_mode((1280, 736), vsync=1)
pygame.display.set_caption("jeu nsiissininisissini")
clock = pygame.time.Clock()
tiles_img = [pygame.image.load("/home/pc/Documents/NSI/Projet-NSI-2026/Assets/jeu arcade/fg.png").convert_alpha(), pygame.image.load("/home/pc/Documents/NSI/Projet-NSI-2026/Assets/jeu arcade/bg.png").convert_alpha()
]
all_sprites = pygame.sprite.Group()
tile_sprites = pygame.sprite.Group()

player = Player((255,0,0), 50, 300, 50)
all_sprites.add(player)

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
    all_sprites.add(newent)

scroll = pygame.math.Vector2(0,0)

while running:
    isHitPressed = False

    dt = clock.tick(60) 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                isHitPressed = True

            if event.key == pygame.K_o:
                ddir = 1 
                if player.velocity[0] > 0:
                    ddir = 1 
                else:
                    ddir = -1 
                
                all_sprites.add(Bullet(player.rect.centerx, player.rect.centery, ddir))
    keys = pygame.key.get_pressed()

    win.fill((0,0,0))    
    #update sprites
    for spr in all_sprites: 
        if spr.type == 0:
            if spr.posX - player.posX < 0:
                spr.velocity[0] = spr.SPEED
            else:
                spr.velocity[0] = -spr.SPEED
        
    for coll in pygame.sprite.spritecollide(player, all_sprites, False):  
        if isHitPressed and coll != player:
            coll.takedmg(0.1)
    
    scroll.x += (player.posX - scroll.x - 1280//2)//10
    scroll.y += (player.posY - scroll.y - 786//2)//5

    tile_sprites.update(scroll)

    all_sprites.update(dt, tile_sprites, scroll)
    
    tile_sprites.draw(win)
    all_sprites.draw(win)

    pygame.display.flip()
pygame.quit()

"""

à faire avant lundi:
-smooth sprite scrolling (regarder tuto daflufflypotato)
-working collision

player avec des armes 
doit eliminer les ennemis 


musique:


"""
