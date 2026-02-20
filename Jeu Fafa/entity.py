import pygame
from math import ceil
class Entity(pygame.sprite.Sprite):
    def __init__(self, clr, size, posx, posy, speed):
        pygame.sprite.Sprite.__init__(self)
        self.type = 0 #0 == FOLLOW
        self.clr = clr
        self.image = pygame.Surface([size, size*1.5])
        self.image.fill(self.clr)
        
        self.rect = self.image.get_rect()
        self.posX = posx
        self.posY = posy
        self.velocity = [0,0]
        self.SPEED = speed

        self.health = 1.00

        self.tick = 0
        self.r = 255

    def update(self, delta, tileGroup, scroll):
        self.tick += 1
        self.r += delta
        if self.r > 255:
            self.r = 255

        self.image.fill((self.r, 255, 255, 255))
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
        self.health -= damageNum

        self.r = 0

        
