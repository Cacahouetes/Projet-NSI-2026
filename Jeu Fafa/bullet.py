import pygame 
from math import cos, sin
class Bullet(pygame.sprite.Sprite):
    def __init__(self, posx, posy, bDir):
        pygame.sprite.Sprite.__init__(self)
        self.type = 2 #bullet
        self.image = pygame.Surface([15, 5])
        self.image.fill((255,255,0))

        self.dir = bDir
        self.rect = self.image.get_rect()
        self.vPos = [int(posx), int(posy)]
        self.velocity = [0,0]

    def update(self, delta, tile_sprites, scroll):
    
        self.velocity[0] = 3 * delta * cos(self.dir)
        self.velocity[1] = 3 * delta * sin(self.dir)

        self.movewCollision(tile_sprites, scroll, delta)

        for hit_tile in pygame.sprite.spritecollide(self, tile_sprites, False):
            if hit_tile.tileID > 0: 
                self.kill()
                return
    
    def movewCollision(self, tileGroup, scroll, delta):
        
        self.rect.x = self.posX - scroll.x
        self.rect.y = self.posY - scroll.y

        self.rect.x += self.velocity[0] * delta
        self.rect.y -= self.velocity[1] * delta

        self.posX = self.rect.x + scroll.x
        self.posY = self.rect.y + scroll.y
            
