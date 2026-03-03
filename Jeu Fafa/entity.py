import pygame
from math import ceil
from enum import Enum


class Entity(pygame.sprite.Sprite):
    def __init__(self, clr, size, posx, posy, events):
        pygame.sprite.Sprite.__init__(self)
        
        self.eventman = events
        self.type = 0 #0 == FOLLOW
        self.clr = clr
        self.image = pygame.Surface([size, size*1.5])
        self.image.fill(self.clr)
        
        self.rect = self.image.get_rect()
        self.rect.width = 10

        self.posX = posx
        self.posY = posy
        self.velocity = [0,0]
        self.SPEED = 0.3
        self.health = 1.00

        self.tick = 0
        self.r = 255

        self.states = Enum('state', [('FOLLOW', 0), ('DEAD', 1), ('ATTACK', 1)])
        self.state = self.states['FOLLOW']

    def update(self, delta, tileGroup, scroll, player):
        
        match self.state:
            case self.states.FOLLOW:
                self.tick += 1
                plDist = self.rect.centerx - player.rect.centerx
                
                if self.rect.colliderect(player.rect):#abs(plDist) < 10:
                    self.state = self.states['ATTACK']
                    self.tick = 0

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
                
                if self.tick == 0:
                    player.takedmg(0.02)
                elif self.tick > 80:
                    self.state = self.states['FOLLOW']
                self.tick += 1
            case self.states.DEAD:

                self.velocity[0] = 0
                self.velocity[1] = 0
                self.tick += 1
        
        
        self.image.fill(self.clr)
        self.movewCollision(tileGroup, scroll, delta)
    
    def movewCollision(self, tileGroup, scroll, delta):
        if self.posY > 1000:
            self.posY = -200
        
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
        self.eventman.broadcast(self.eventman.evts['ENNEMY_TAKE_DAMAGE'])
        self.health -= damageNum

        self.r = 0
        if self.health < 0:
            self.state = self.states['DEAD']

    