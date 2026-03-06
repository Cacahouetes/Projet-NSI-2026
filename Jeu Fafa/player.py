import pygame
from math import ceil, atan2, cos, sin
class Player(pygame.sprite.Sprite):
    def loadimg(self, path):
        return pygame.image.load(path).convert_alpha()
    
    
    def __init__(self, posx, posy, evts):
        pygame.sprite.Sprite.__init__(self)

        self.eventman = evts
        self.type = 1 #PLAYER
        self.health = 1.00
        self.isDead = False        
        self.animdict = {
            "idle" : ["idle/playerIdle1.png", "idle/playerIdle2.png"],
            "walk" : ["walk/playerWalk2.png", "walk/playerWalk1.png"],
            "jump" : ["jump/playerJump1.png", "jump/playerJump2.png", "jump/playerJump3.png"],
            "damage": ["damage/playerDamage1.png"]
        }
        #charger les animations
        self.images = {}
        self.images_orig = {}
        for anim in self.animdict:
            self.images[anim] = []
            self.images_orig[anim] = []
            for i in range(len(self.animdict[anim])):
                self.images[anim].append(self.loadimg("Assets/jeu arcade/playerspr/" + self.animdict[anim][i]))
                self.images[anim][i] = pygame.transform.scale2x(self.images[anim][i])
                self.images_orig[anim].append(self.images[anim][i])
        
        self.curranim = "idle" #remplacer ça par un enum?
        self.animspd = 10
        self.image = self.images["idle"][0]
        self.rect = self.image.get_rect()
        self.posX = posx
        self.posY = posy
        self.velocity = [0,0]
        self.jumping = False
        self.SPEED = 0.6
        self.tick = 0

        self.score = 0

        self.msPlDir = 0

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
        self.updMousePos()
        self.animations()

    def animations(self):
        
        #if self.curranim == "damage":
        #    self.curranim = "idle"

        if self.jumping:
            if self.curranim != "jump":
                self.curranim = "jump"
                self.tick = 0
                self.animspd = 6
        else:   
            if abs(self.velocity[0]) > 0.1 and self.curranim != "walk":
                self.curranim = "walk"
                self.tick = 0
                self.animspd = 10
            elif abs(self.velocity[0]) < 0.1 and self.curranim != "idle":
                self.curranim = "idle"
                self.tick = 0
                self.animspd = 5


        if self.curranim == "jump" and int(self.tick / 60 * self.animspd) >= len(self.images[self.curranim]): #eviter l'animation en boucle pour le saut
            animIdx = len(self.images[self.curranim]) -1
        else:
            animIdx = int(self.tick / 60 * self.animspd) % len(self.images[self.curranim])
        if cos(self.msPlDir) < 0:
            self.image = pygame.transform.flip(self.images[self.curranim][animIdx], True, False)
        else:
            self.image = self.images_orig[self.curranim][animIdx]

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

        #self.rect.x = self.x
        #self.rect.y = self.y 

    def updMousePos(self):
        #get angle of player mouse line
        lx = pygame.mouse.get_pos()[0] - self.rect.centerx 
        ly = self.rect.centery -  pygame.mouse.get_pos()[1]
        self.msPlDir = atan2(ly, lx)

    def takedmg(self, damageNum):
        self.eventman.broadcast(self.eventman.evts['PLAYER_TAKE_DAMAGE'])
        self.health -= damageNum

        self.r = 0
        if self.health < 0:
            self.isDead = True

    def eventGet(self, event):
        if event.value == self.eventman.evts['PLAYER_TAKE_DAMAGE'].value:
            self.curranim = "damage"
        
        if event.value == self.eventman.evts['PLAYER_FIRE'].value:
            pass
            #self.velocity[0] = -cos(self.msPlDir)/2
            #self.velocity[1] -= sin(self.msPlDir)/2
        
        if event.value == self.eventman.evts['PLAYER_GET_THING'].value:
            self.score += 10