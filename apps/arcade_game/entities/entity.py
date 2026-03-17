import pygame
import os
from enum import Enum

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "..", "assets", "arcade_game"))


class Entity(pygame.sprite.Sprite):
    def loadimg(self, path):
        return pygame.image.load(path).convert_alpha()

    def __init__(self, clr, posx, posy, events, isStrong):
        pygame.sprite.Sprite.__init__(self)
        
        self.eventMan = events
        self.isStrong = isStrong 
        self.clr = clr

        self.animdict = {
            "walk" : ["walk/ennemyWalk1.png", "walk/ennemyWalk2.png"],
            "hit" : ["hit/ennemyHit1.png", "hit/ennemyHit2.png", "hit/ennemyHit3.png", "hit/ennemyHit4.png", "hit/ennemyHit5.png"],
            "hurt" : ["hurt/ennemyHurt1.png", "hurt/ennemyHurt2.png"]
        }
        
        #charger les animations (meme code que dans player.py)
        self.images = {}
        self.images_orig = {}
        for anim in self.animdict:
            self.images[anim] = []
            self.images_orig[anim] = []
            for i in range(len(self.animdict[anim])):
                self.images[anim].append(self.loadimg(os.path.join(ASSETS_DIR, "ennemy", self.animdict[anim][i])))
                self.images[anim][i] = pygame.transform.scale_by(self.images[anim][i], 3 if self.isStrong else 2)
                self.images_orig[anim].append(self.images[anim][i])
        
        self.curranim = "walk" 

        self.image = self.images["walk"][0]
        self.rect = self.image.get_rect()
        self.rect.width = 10

        self.posX = posx
        self.posY = posy
        self.velocity = [0,0]
        self.SPEED = 0.3
        self.health = 1.75 if self.isStrong else 1.00
        self.playerGaveDmg = False
        self.tick = 0
        self.r = 255

        self.states = Enum('state', [('FOLLOW', 0), ('DEAD', 1), ('ATTACK', 2), ('HURT', 3)])
        self.state = self.states['FOLLOW']
        self.animspd = 6

    def update(self, delta, tileGroup, scroll, player):
        
        match self.state:
            case self.states.FOLLOW:
                self.clr = (255,255,255)
                plDist = self.rect.centerx - player.rect.centerx
                
                if self.rect.colliderect(player.rect):#abs(plDist) < 10:
                    self.state = self.states['ATTACK']
                    self.curranim = "hit"
                    self.animspd = 10
                    self.tick = 0
                    self.playerGaveDmg = False

                if abs(plDist) < 10:
                    self.velocity[0] = 0
                elif plDist < 0:
                    self.velocity[0] = self.SPEED
                else:
                    self.velocity[0] = -self.SPEED 
                
                self.r += delta
                if self.r > 255:
                    self.r = 255
                
            case self.states.ATTACK:
                self.clr = (255,255,0)
                if not self.playerGaveDmg and not player.isDead:
                    player.takedmg(0.1 if self.isStrong else 0.06)
                    self.playerGaveDmg = True

                if self.tick > 25:
                    self.state = self.states['FOLLOW']
                    self.curranim = "walk"
                    self.tick = 0
                    self.animspd = 6
                
            case self.states.DEAD:
                self.clr = (0,0,0)
                self.velocity[0] = 0
                self.velocity[1] = 0
                
        
            case self.states.HURT:
                self.clr = (255,50,50)
                if self.tick > 20:
                    self.state = self.states['FOLLOW']
                    self.tick = 0
                    self.curranim = "walk"     
                    self.animspd = 6   

        self.tick += 1
        self.animations()
        self.movewCollision(tileGroup, scroll, delta)
    
    def movewCollision(self, tileGroup, scroll, delta):
        if self.posY > 1000:
            self.posY = 200

        self.rect.x = self.posX - scroll.x
        self.rect.y = self.posY - scroll.y

        self.velocity[0] *= 0.7 
        self.velocity[1] -= 0.05  
        
        self.rect.x += self.velocity[0] * delta
        self.moveX(tileGroup)

        self.rect.y -= self.velocity[1] * delta
        self.moveY(tileGroup)

        self.posX = self.rect.x + scroll.x
        self.posY = self.rect.y + scroll.y

    def moveX(self, tileGroup):
        hit_list = pygame.sprite.spritecollide(self, tileGroup, False)
        for hit_tile in hit_list:
            if hit_tile.tileID > 0: 
                
                if self.velocity[0] > 0: #droite
                    self.rect.right = hit_tile.rect.left #- self.rect.width*5
                elif self.velocity[0] < 0: #gauche
                    self.rect.left = hit_tile.rect.right #- self.rect.width
                self.velocity[0] = 0

    def moveY(self, tileGroup):
        hit_list = pygame.sprite.spritecollide(self, tileGroup, False)
        for hit_tile in hit_list:
            if hit_tile.tileID > 0: 
                
                if self.velocity[1] > 0: #haut
                    self.rect.top = hit_tile.rect.bottom 
                elif self.velocity[1] < 0: #bas
                    self.jumping = False
                    self.rect.bottom = hit_tile.rect.top #+ self.rect.height

                self.velocity[1] = 0

    def takedmg(self, damageNum):
        self.eventMan.broadcast(self.eventMan.evts['ENNEMY_TAKE_DAMAGE'])
        self.health -= damageNum

        self.r = 0
        if self.health < 0:
            self.state = self.states['DEAD']
        else:
            self.state = self.states['HURT']
            self.tick = 0
            self.curranim = "hurt"     
            self.animspd = 6   

    def animations(self):
        
        animIdx = int(self.tick / 60 * self.animspd) % len(self.images[self.curranim])

        if self.velocity[0] < 0:
            self.image = pygame.transform.flip(self.images[self.curranim][animIdx], True, False)
        else:
            self.image = self.images_orig[self.curranim][animIdx]