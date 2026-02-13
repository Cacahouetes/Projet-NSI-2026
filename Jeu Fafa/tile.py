import pygame 

class Tile(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([32, 32])
        #self.image.fill((243,234,233))

        self.rect = self.image.get_rect()
        self.x = 0
        self.y = 0
        self.tileID = 0
        #self.rect.x = self.tX
        #self.tX = 0
        #self.tY = 0

    def update(self, scroll):
        self.rect.x = self.x - scroll.x
        self.rect.y = self.y - scroll.y #% 32
        