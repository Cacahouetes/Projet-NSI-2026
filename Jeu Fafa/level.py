import pygame
from eventmanager import EventManager
from soundmanager import SoundManager
from screeneffects import ScreenEffects
from player import Player
from entity import Entity
from collectible import Collectible
from bullet import Bullet
from tile import Tile
from gun import Gun
import random
class Level():

    def __init__(self):
        self.TILE_SIZE = 32 
        self.scroll = pygame.math.Vector2(0,0)
        self.ennemy_sprites = pygame.sprite.Group()
        self.tile_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.collectible_sprites = pygame.sprite.Group()
        self.ent_draw_sprites = pygame.sprite.Group()
        self.waveN = 0
        
        self.tiles = []
        self.tiles_img = [pygame.image.load("Assets/jeu arcade/fg.png").convert_alpha(), pygame.image.load("Assets/jeu arcade/bg.png").convert_alpha()]

        self.readLevelFile("Jeu Fafa/niveau.txt")
        self.LoadTileTexts()
        self.LoadTileSprites()
        
        self.eventman = EventManager()
        self.gun = Gun(self.eventman)
        self.soundman = SoundManager(self.eventman)
        self.player = Player(300, 50, self.eventman)
        self.scrfx = ScreenEffects()

        #relier les objets au système d'evenements pour qu'ils les captent
        self.eventman.eventObjects.append(self.soundman)
        self.eventman.eventObjects.append(self.player)
        self.eventman.eventObjects.append(self.scrfx)
        self.eventman.eventObjects.append(self.gun)
        self.eventman.eventObjects.append(self)

        self.ent_draw_sprites.add(self.player)

        self.NewWave()
        
        self.newCollectible(400, 500)
    
    def readLevelFile(self, path):
        niveau = open(path, "r")
        while True:
            row = niveau.readline()
            if row == "":
                break

            rowlist = []
            for tile in row:
                if tile in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    rowlist.append(int(tile))
            self.tiles.append(rowlist)

    def newEntity(self, xpos):
        newent = Entity((xpos%255, 200,200), xpos, 0, self.eventman)
        newent.type = 0
        self.ennemy_sprites.add(newent)
        self.ent_draw_sprites.add(newent)
    
    def LoadTileTexts(self):
        for i in range(len(self.tiles_img)):
            self.tiles_img[i] = pygame.transform.scale(self.tiles_img[i], (self.TILE_SIZE, self.TILE_SIZE))
    
    def LoadTileSprites(self):
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[0])):
                newTile = Tile()
                newTile.x = x * self.TILE_SIZE
                newTile.y = y * self.TILE_SIZE
                newTile.rect.x = x * self.TILE_SIZE
                newTile.rect.y = y * self.TILE_SIZE
                newTile.tileID = self.tiles[y][x]
                newTile.image = self.tiles_img[newTile.tileID].convert()
                self.tile_sprites.add(newTile)

    def newCollectible(self, xpos, ypos):
        self.collectible_sprites.add(Collectible(xpos, ypos))
    
    def NewBullet(self):
        bullet = Bullet(self.gun.tipx + self.scroll.x, self.gun.tipy + self.scroll.y , self.player.msPlDir)
        self.bullet_sprites.add(bullet)
        self.eventman.broadcast(self.eventman.evts['PLAYER_FIRE'])

    def updSprites(self, dt):
        self.ennemy_sprites.update(dt, self.tile_sprites, self.scroll, self.player)
        for sprite in self.ennemy_sprites:
            for coll_spr in self.ennemy_sprites:
                if coll_spr != sprite:
                    dst = coll_spr.rect.centerx - sprite.rect.centerx
                    if abs(dst) < 5:
                            way = 1
                            if dst < 0: way = -1
                            coll_spr.rect.centerx = coll_spr.rect.centerx + 5*way
                
            if sprite.state.value == sprite.states['DEAD'].value:
                sprposx = sprite.posX 
                sprposy = sprite.posY 
                sprite.kill()
                self.newCollectible(sprposx, sprposy)

    def updBullets(self, dt):
        for bul in self.bullet_sprites:
            bul.update(dt, self.scroll)
            for tile in self.tile_sprites:
                if tile.rect.clipline((bul.rectbefore.x, bul.rectbefore.y), (bul.rect.x, bul.rect.y)):
                    if tile.tileID > 0:
                        bul.kill()
                        break

            for ennemy in self.ennemy_sprites:
                if ennemy.rect.clipline((bul.rectbefore.x, bul.rectbefore.y), (bul.rect.x, bul.rect.y)):
                    ennemy.takedmg(0.5)
                    bul.kill()
                    break
            
            if abs(bul.vPos[1]) > 4000:
                bul.kill()

    def updPlayer(self):
        #for coll in pygame.sprite.spritecollide(self.player, self.ennemy_sprites, False):  
        #    if isHitPressed and coll != player:
        #        coll.takedmg(0.1)
        
        for colc_coll in pygame.sprite.spritecollide(self.player, self.collectible_sprites, False):
            self.eventman.broadcast(self.eventman.evts['PLAYER_GET_THING'])
            colc_coll.kill()

    def update(self, dt):
        self.scroll.x += (self.player.posX - self.scroll.x - 1280//2)//10
        self.scroll.y += (self.player.posY - self.scroll.y - 786//2)//5

        self.tile_sprites.update(self.scroll)
        self.player.update(dt, self.tile_sprites, self.scroll)

        alldead = True
        for enn in self.ennemy_sprites:
            if enn.state.value != enn.states['DEAD'].value:
                alldead = False 
                break
        if alldead:
            self.eventman.broadcast(self.eventman.evts['NEW_WAVE'])
            
        self.updSprites(dt)
        self.updPlayer()
        self.updBullets(dt)

        self.scrfx.update()
        self.collectible_sprites.update(self.scroll, dt)

    def NewWave(self):
        self.waveN += 1
        for i in range(4**self.waveN):
            self.newEntity(random.randrange(100,2500))
        

    def eventGet(self, event):
        if event.value == self.eventman.evts['NEW_WAVE'].value:
            self.NewWave()

    def draw(self, win):
        self.tile_sprites.draw(win)
        self.ent_draw_sprites.draw(win)
        self.collectible_sprites.draw(win)
        self.bullet_sprites.draw(win)

        #-----GUI-----
        #dessiner barre de santé
        pygame.draw.rect(win, (255,0,0), pygame.Rect(15,15,200,50))
        pygame.draw.rect(win, (0,255,0), pygame.Rect(15,15,200*self.player.health, 50))

        #dessiner le pistolet
        self.gun.update(win, self.player, self.player.msPlDir*180/3.14159265)
        
        win.blit(self.scrfx.image, self.scrfx.rect)