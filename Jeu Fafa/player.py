import pygame
from math import ceil
class Player(pygame.sprite.Sprite):
    def __init__(self, clr, size):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([size, size*1.5])
        self.image.fill(clr)
        
        self.rect = self.image.get_rect()
        self.posX = 100
        self.posY = 0
        self.velocity = [0,0]
        self.jumping = False
        self.SPEED = 0.6
        self.tick = 0


    def update(self, delta, tileGroup, scroll):
        self.tick += 1
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.velocity[0] = -self.SPEED
        elif keys[pygame.K_RIGHT]:
            self.velocity[0] = self.SPEED
        
        if keys[pygame.K_UP] and not self.jumping:
            self.velocity[1] = 1
            self.jumping = True
        
        self.movewCollision(tileGroup, scroll, delta)
        

    def movewCollision(self, tileGroup, scroll, delta):
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

        #self.rect.x = self.x
        #self.rect.y = self.y 

