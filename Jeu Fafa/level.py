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
from math import sin, cos,ceil, sqrt
from enum import Enum

import random
def loadimg(path):
        return pygame.image.load("Assets/jeu arcade/" + path).convert_alpha()
class Level():
    
    def NewGame(self):
        self.ennemy_sprites = pygame.sprite.Group()
        
        self.bullet_sprites = pygame.sprite.Group()
        self.collectible_sprites = pygame.sprite.Group()
        self.ent_draw_sprites = pygame.sprite.Group()
        self.waveN = 0

        self.changeTick = 0 #temps depuis le dernier changement d'état en secondes
        self.currState = self.lvlStates['NORMAL']

        self.eventman = EventManager()
        self.gun = Gun(self.eventman)
        self.soundman = SoundManager(self.eventman)
        self.player = Player(300, 150, self.eventman)
        self.scrfx = ScreenEffects(self.eventman, self)

        #relier les objets au système d'evenements pour qu'ils les captent
        self.eventman.eventObjects.append(self.soundman)
        self.eventman.eventObjects.append(self.player)
        self.eventman.eventObjects.append(self.scrfx)
        self.eventman.eventObjects.append(self.scrfx)
        self.eventman.eventObjects.append(self.gun)
        self.eventman.eventObjects.append(self)

        self.ent_draw_sprites.add(self.player)

        self.NewWave()

    def __init__(self):
        self.TILE_SIZE = 32 
        self.scroll = pygame.math.Vector2(0,0)
        self.tile_sprites = pygame.sprite.Group()

        self.lvlStates = Enum('lvlState', [('NORMAL', 0), ('WAVE_END', 1),('WAVE_START', 2)])
        self.currState = self.lvlStates['NORMAL']

        self.tiles = []
        self.tiles_img = [loadimg("bg.png"), loadimg("fg.png"), loadimg("fgright.png"), loadimg("fgleft.png")]

        self.readLevelFile("Jeu Fafa/niveau.txt")
        self.LoadTileTexts()
        self.LoadTileSprites()
        
        self.NewGame()
    
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

    def newEntity(self, xpos, isStrong):
        newent = Entity((xpos%255, 200,200), xpos, 150, self.eventman, isStrong)
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
        val=0
        rand=random.randint(0,9)
        if rand >=8: #30% de probabilité
            rand = random.randint(0,9)
            if rand >= 8 and self.gun.unlockedGuns!=3: #??% de probabilité
                if self.gun.unlockedGuns==1:
                    val=2 #nouv. arme fly
                else:
                    val=3 #nouv. arme ak-47
            else:
                val=1 #upgrade santé
        self.collectible_sprites.add(Collectible(xpos, ypos, val))
    
    def NewBullet(self):
        seconds = pygame.time.get_ticks()/1000
        tgap = seconds - self.gun.lastFireTime
        if (self.gun.currGunID == 1 and tgap > 0.2) or (self.gun.currGunID == 2 and tgap > 0.08) or (self.gun.currGunID == 0 and tgap > 0.1): 
            self.gun.lastFireTime = seconds
            bullet = Bullet(self.gun.tipx + self.scroll.x, self.gun.tipy + self.scroll.y , self.player.msPlDir, self.gun.currGunID)
            self.bullet_sprites.add(bullet)
            if self.gun.currGunID == 1:
                self.player.velocity[1] -= sin(self.player.msPlDir)/1.5
            
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
                sprposx = sprite.posX + sprite.rect.width/2
                sprposy = sprite.posY + sprite.rect.height/2
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
                    ennemy.takedmg(bul.dmgnum)
                    bul.kill()
                    break
            
            if abs(bul.vPos[1]) > 4000:
                bul.kill()

    def updPlayer(self):
        #for coll in pygame.sprite.spritecollide(self.player, self.ennemy_sprites, False):  
        #    if isHitPressed and coll != player:
        #        coll.takedmg(0.1)
        
        for colc_coll in pygame.sprite.spritecollide(self.player, self.collectible_sprites, False):
            if colc_coll.ctype == 0:
                self.eventman.broadcast(self.eventman.evts['PLAYER_GET_PT'])
            elif colc_coll.ctype == 1:
                self.eventman.broadcast(self.eventman.evts['PLAYER_GET_HEALTH'])
            elif colc_coll.ctype == 2:
                self.eventman.broadcast(self.eventman.evts['PLAYER_GET_NEW_FLY'])
            elif colc_coll.ctype == 3:
                self.eventman.broadcast(self.eventman.evts['PLAYER_GET_NEW_AK'])
            colc_coll.kill()

    def isAllDead(self) -> bool:
        """True si tous les ennemis sont morts, sinon False. Servi pour le fonctionnement des vagues"""
        alldead = True
        for enn in self.ennemy_sprites:
            if enn.state.value != enn.states['DEAD'].value:
                alldead = False 
        return alldead

    def update(self, dt):
        
        self.scroll.x += (self.player.posX - self.scroll.x - 1280//2)//10
        self.scroll.y += (self.player.posY - self.scroll.y - 786//2)//5

        self.tile_sprites.update(self.scroll)
        self.player.update(dt, self.tile_sprites, self.scroll)
            
        self.updSprites(dt)
        self.updPlayer()
        self.updBullets(dt)
        self.gun.update()

        self.scrfx.update()
        self.collectible_sprites.update(self.scroll, dt)
        self.changeTick += dt/1000
    
        match self.currState:
            case self.lvlStates.NORMAL:
                if self.isAllDead():
                    self.eventman.broadcast(self.eventman.evts['WAVE_END'])

            case self.lvlStates.WAVE_START:
                pass
                
            case self.lvlStates.WAVE_END:
                
                if self.changeTick > 4:
                    self.eventman.broadcast(self.eventman.evts['NEW_WAVE'])
        keys = pygame.key.get_pressed()
        if self.player.isDead and keys[pygame.K_r]:
            self.NewGame()

    def NewWave(self):
        self.waveN += 1
        ennemyNum = ceil(sqrt(self.waveN*8)) #vitesse d'augmentation des ennemis qui ralentit au fil des vagues
        strongEnnemyNum = ceil(0.1*(self.waveN+3)**2 - (self.waveN+3)+2) #fonction du second degré (enfin les maths qui servent à une chose), a un moment il dépasse le nombre d'ennemis moyens
        strongEnnemyNum = min(strongEnnemyNum, ennemyNum)

        for i in range(strongEnnemyNum):
            self.newEntity(random.randrange(100,2500), True)
        
        for i in range(ennemyNum-strongEnnemyNum):
            self.newEntity(random.randrange(100,2500), False)
    
    def eventGet(self, event):
        if event.value == self.eventman.evts['WAVE_END'].value:
            self.changeTick = 0
            self.currState = self.lvlStates['WAVE_END']
        
        if event.value == self.eventman.evts['NEW_WAVE'].value:
            self.NewWave()
            self.changeTick = 0
            self.currState = self.lvlStates['NORMAL']

    def draw(self, win):
        self.tile_sprites.draw(win)
        self.ent_draw_sprites.draw(win)
        self.collectible_sprites.draw(win)
        self.bullet_sprites.draw(win)

        #-----GUI-----

        #dessiner barre de santé
        pygame.draw.rect(win, (93,49,49), pygame.Rect(15,15,200,50))
        pygame.draw.rect(win, (55,101,54), pygame.Rect(15,15,200*self.player.health, 50))

        if not self.player.isDead:
            #dessiner le pistolet (si le joueur n'est pas mort)
            self.gun.draw(win, self.player, self.player.msPlDir*180/3.14159265)
           
        win.blit(self.scrfx.image, self.scrfx.rect)

        #dessiner ui pistolets
        for i in range(self.gun.unlockedGuns):
            img = pygame.transform.scale_by(self.gun.imgs[i], 1.5)
            alpha = 180 if i==self.gun.currGunID else 90
            img.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)

            win.blit(img, (32 + i*128, 48))

        