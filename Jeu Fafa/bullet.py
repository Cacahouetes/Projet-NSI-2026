import pygame 

class Bullet(pygame.sprite.Sprite):
    def __init__(self, posx, posy, bDir):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface([15, 5])
        self.image.fill((255,255,0))

        self.dir = bDir
        self.rect = self.image.get_rect()
        self.vPos = [int(posx), int(posy)]

    def update(self, delta, tile_sprites):
    
        self.vPos[0] += 3 * delta * self.dir
        self.rect.centerx = self.vPos[0]
        self.rect.centery = self.vPos[1]

        for hit_tile in pygame.sprite.spritecollide(self, tile_sprites, False):
            if hit_tile.tileID > 0: 
                self.kill()
                return
        #if abs(self.vPos[0]) > 10000:
            
