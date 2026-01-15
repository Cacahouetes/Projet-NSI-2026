import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, clr, size):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([size, size*1.5])
        self.image.fill(clr)

        self.rect = self.image.get_rect()
        self.x = 0
        self.y = 0
        self.velocity = [0,0]
        self.jumping = False
        self.SPEED = 0.6

    def update(self, delta):

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.velocity[0] = -self.SPEED
        elif keys[pygame.K_RIGHT]:
            self.velocity[0] = self.SPEED
        
        if keys[pygame.K_UP] and not self.jumping:
            self.velocity[1] = 1
            self.jumping = True
        #elif keys[pygame.K_DOWN]:
        #    self.y += 5
        
        self.velocity[0] *= 0.7 
        self.velocity[1] -= 0.05  
        
        self.x += self.velocity[0] * delta
        self.y -= self.velocity[1] * delta
        
        if self.y >= 500:
            self.y = 500
            self.velocity[1] = 0
            self.jumping = False
        
        self.rect.centerx = self.x
        self.rect.centery = self.y 

