import pygame 
import math

from eventmanager import EventManager
from soundmanager import SoundManager
from screeneffects import ScreenEffects
from player import Player
from entity import Entity
from collectible import Collectible
from bullet import Bullet
from tile import Tile
from gun import Gun


deleteaftertick = 0
running = True 
dt = 0.1
TILE_SIZE = 32 
scroll = pygame.math.Vector2(0,0)

pygame.init()
#pygame.mixer.init()
win = pygame.display.set_mode((1280, 736), vsync=1)
pygame.display.set_caption("jeu nsiissininisissini")
clock = pygame.time.Clock()
tiles_img = [pygame.image.load("Assets/jeu arcade/fg.png").convert_alpha(), pygame.image.load("Assets/jeu arcade/bg.png").convert_alpha()
]



ennemy_sprites = pygame.sprite.Group()
tile_sprites = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()
collectible_sprites = pygame.sprite.Group()
ent_draw_sprites = pygame.sprite.Group()


gun = Gun()
eventman = EventManager()
soundman = SoundManager(eventman)
player = Player(300, 50, eventman)
scrfx = ScreenEffects()

ent_draw_sprites.add(player)

eventman.eventObjects.append(soundman)
eventman.eventObjects.append(player)
eventman.eventObjects.append(scrfx)

for i in range(len(tiles_img)):
    tiles_img[i] = pygame.transform.scale(tiles_img[i], (TILE_SIZE, TILE_SIZE))

tiles = []
niveau = open("Jeu Fafa/niveau.txt", "r")
while True:
    row = niveau.readline()
    if row == "":
        break

    rowlist = []
    for tile in row:
        if tile in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            rowlist.append(int(tile))
    tiles.append(rowlist)

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
    newent = Entity((xpos%255, 200,200), xpos, 0, eventman)
    newent.type = 0
    ennemy_sprites.add(newent)
    ent_draw_sprites.add(newent)

#spawn random collectible
colc = Collectible(200,650)
collectible_sprites.add(colc)
#ent_draw_sprites.add(colc)

while running:
    isHitPressed = False
    dt = clock.tick(60) 
    keys = pygame.key.get_pressed()
    win.fill((0,0,0))   

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            #tirer une balle
            bullet = Bullet(gun.tipx + scroll.x, gun.tipy + scroll.y , player.msPlDir)
            bullet_sprites.add(bullet)
            gun.shootFlag = True
            eventman.broadcast(eventman.evts['PLAYER_FIRE'])

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                isHitPressed = True

    #mouvement caméra
    scroll.x += (player.posX - scroll.x - 1280//2)//10
    scroll.y += (player.posY - scroll.y - 786//2)//5
    
    tile_sprites.update(scroll)

    player.update(dt, tile_sprites, scroll)

    #mettre à jour les sprites
    ennemy_sprites.update(dt, tile_sprites, scroll, player)
    for sprite in ennemy_sprites:
        for coll_spr in ennemy_sprites:
            if coll_spr != sprite:
                dst = coll_spr.rect.centerx - sprite.rect.centerx
                if abs(dst) < 5:
                        way = 1
                        if dst < 0: way = -1
                        coll_spr.rect.centerx = coll_spr.rect.centerx + 5*way
    
    for coll in pygame.sprite.spritecollide(player, ennemy_sprites, False):  
        if isHitPressed and coll != player:
            coll.takedmg(0.1)
    for colc_coll in pygame.sprite.spritecollide(player, collectible_sprites, False):
        eventman.broadcast(eventman.evts['PLAYER_GET_THING'])
        colc_coll.kill()

    #mettre à jour les bullets
    for bul in bullet_sprites:
        bul.update(dt, scroll)
        for tile in tile_sprites:
            if tile.rect.clipline((bul.rectbefore.x, bul.rectbefore.y), (bul.rect.x, bul.rect.y)):
                if tile.tileID > 0:
                    bul.kill()
                    break

        for ennemy in ennemy_sprites:
            if ennemy.rect.clipline((bul.rectbefore.x, bul.rectbefore.y), (bul.rect.x, bul.rect.y)):
                ennemy.takedmg(0.1)
                bul.kill()
                break

    scrfx.update()
    collectible_sprites.update(scroll, dt)

    tile_sprites.draw(win)
    ent_draw_sprites.draw(win)
    collectible_sprites.draw(win)
    bullet_sprites.draw(win)

    #-----GUI-----
    #dessiner barre de santé
    pygame.draw.rect(win, (255,0,0), pygame.Rect(15,15,200,50))
    pygame.draw.rect(win, (0,255,0), pygame.Rect(15,15,200*player.health, 50))
    #dessiner le pistolet
    gun.update(win, player, player.msPlDir*180/3.14159265)
    
    win.blit(scrfx.image, scrfx.rect)

    pygame.display.flip()
pygame.quit()

"""
player avec des armes 
doit eliminer les ennemis 


musique:


"""
