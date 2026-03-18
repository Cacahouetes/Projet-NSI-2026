import pygame
import sqlite3
import os
from math import atan2, cos

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "..", "assets", "arcade_game"))

DB_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "..", "data", "game.db"))
PLAYER_ID = 1
RARITIES = ["Commune", "Rare", "Épique", "Légendaire", "Mythique", "Unique", "Divine"]


class Player(pygame.sprite.Sprite):
    def loadimg(self, path):
        return pygame.image.load(path).convert_alpha()
    
    def __init__(self, posx, posy, evts):
        pygame.sprite.Sprite.__init__(self)

        self.eventMan = evts
        self.eventMan.eventObjects.append(self)

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
                self.images[anim].append(self.loadimg(os.path.join(ASSETS_DIR, "playerspr", self.animdict[anim][i])))
                self.images[anim][i] = pygame.transform.scale2x(self.images[anim][i])
                self.images_orig[anim].append(self.images[anim][i])
        
        self.currAnim = "idle" #J'aurais pu remplacer cette variable par un enum
        self.animSpd = 10 #vitesse des animations 
        self.image = self.images["idle"][0]
        self.rect = self.image.get_rect()
        self.posX = posx
        self.posY = posy
        self.velocity = [0,0]
        self.isJumping = False
        self.moveSpd = 0.6
        self.tick = 0
        
        self.score = 0
        self.msPlDir = 0

        self.GetScore()
    
    def GetScore(self):
        """
        Lit les pièces depuis la DB.
        Si aucun joueur n'existe, en crée un automatiquement.
        """
        import time as _time
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
 
                cur.execute("SELECT player_id FROM PLAYERS ORDER BY player_id LIMIT 1")
                row = cur.fetchone()
 
                if row is None:
                    # Aucun joueur, création automatique
                    cur.execute(
                        "INSERT INTO PLAYERS (username, created_at) VALUES (?, ?)",
                        ("Joueur", int(_time.time()))
                    )
                    new_id = cur.lastrowid
                    cur.execute("INSERT INTO PLAYER_STATS (player_id) VALUES (?)", (new_id,))
                    for rarity in RARITIES:
                        cur.execute("""
                            INSERT INTO PLAYER_RARITY_STATS (player_id, rarity, obtained, sold, fused)
                            VALUES (?, ?, 0, 0, 0)
                        """, (new_id, rarity))
                    conn.commit()
                    self.score = 0
                else:
                    cur.execute("SELECT coins FROM PLAYER_STATS WHERE player_id=?",
                                (row["player_id"],))
                    stat = cur.fetchone()
                    self.score = stat["coins"] if stat else 0
 
        except Exception:
            self.score = 0
    
    def PutScore(self):
        """Ajoute 1 pièce dans la base de données (1 point = 1 pièce)."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE PLAYER_STATS
                    SET coins        = coins + 10,
                        coins_earned = coins_earned + 10,
                        max_coins_held = MAX(max_coins_held, coins + 10)
                    WHERE player_id = ?
                """, (PLAYER_ID,))
                conn.commit()
        except Exception:
            pass

    def update(self, delta, tileGroup, scroll):
        self.velXBefore = abs(self.velocity[0])
        self.tick += 1
        keys = pygame.key.get_pressed()

        if not self.isDead:
            if keys[pygame.K_LEFT]:
                self.velocity[0] = -self.moveSpd
                
            elif keys[pygame.K_RIGHT]:
                self.velocity[0] = self.moveSpd
            
            if keys[pygame.K_UP] and not self.isJumping:
                self.velocity[1] = 1
                self.eventMan.broadcast(self.eventMan.evts.PLAYER_JUMP)
                self.isJumping = True
        else:
            self.tick = 0
    
        self.movewCollision(tileGroup, scroll, delta)
        self.updMousePos()
        self.animations()
        if self.velXBefore < 0.1 and abs(self.velocity[0]) >= 0.1:
            self.eventMan.broadcast(self.eventMan.evts['PLAYER_WALK_START'])
        elif self.velXBefore > 0.1 and abs(self.velocity[0]) <= 0.1 :
            self.eventMan.broadcast(self.eventMan.evts['PLAYER_WALK_STOP'])

    def animations(self):
        """Gestion des animations du joueur en fonction de son état."""

        if self.isJumping:
            if self.currAnim != "jump":
                self.currAnim = "jump"
                self.tick = 0
                self.animSpd = 6
        else:   
            if abs(self.velocity[0]) > 0.1 and self.currAnim != "walk":
                self.currAnim = "walk"
                self.tick = 0
                self.animSpd = 10
            elif abs(self.velocity[0]) < 0.1 and self.currAnim != "idle":
                self.currAnim = "idle"
                self.tick = 0
                self.animSpd = 5

        if self.currAnim == "jump" and int(self.tick / 60 * self.animSpd) >= len(self.images[self.currAnim]): #Eviter l'animation en boucle pour le saut
            animIdx = len(self.images[self.currAnim]) -1
        else:
            #Répéter l'animation en boucle
            animIdx = int(self.tick / 60 * self.animSpd) % len(self.images[self.currAnim])
        
        #Pivot horizontal de l'image du joueur en fonction de l'angle entre le joueur et la souris
        if cos(self.msPlDir) < 0:
            self.image = pygame.transform.flip(self.images[self.currAnim][animIdx], True, False)
        else:
            self.image = self.images_orig[self.currAnim][animIdx]

    def movewCollision(self, tileGroup, scroll, delta):
        """Change les coordonnées du joueur et gère les collisions entre ceci et le niveau."""
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
        """Change les coordonnées X du joueur et vérifie les collisions."""
        hit_list = pygame.sprite.spritecollide(self, tileGroup, False)
        for hit_tile in hit_list:
            if hit_tile.tileID > 0: 
                
                if self.velocity[0] > 0: #droite
                    self.rect.right = hit_tile.rect.left 
                elif self.velocity[0] < 0: #gauche
                    self.rect.left = hit_tile.rect.right 
                self.velocity[0] = 0
  
    def moveY(self, tileGroup):
        """Change les coordonnées Y du joueur et vérifie les collisions."""
        hit_list = pygame.sprite.spritecollide(self, tileGroup, False)
        for hit_tile in hit_list:
            if hit_tile.tileID > 0: 
                
                if self.velocity[1] > 0: #haut
                    self.rect.top = hit_tile.rect.bottom 
                elif self.velocity[1] < 0: #bas
                    if self.isJumping:
                        self.eventMan.broadcast(self.eventMan.evts['PLAYER_LAND'])
                    self.isJumping = False
                    
                    self.rect.bottom = hit_tile.rect.top 

                self.velocity[1] = 0

    def updMousePos(self):
        """Obtient l'angle entre le joueur et la souris en utilisant la fonction tangente inverse."""
        lx = pygame.mouse.get_pos()[0] - self.rect.centerx 
        ly = self.rect.centery -  pygame.mouse.get_pos()[1]
        self.msPlDir = atan2(ly, lx)

    def takedmg(self, damageNum):
        """Performe les actions à faire quand le joueur perd des points de PV."""
        self.health -= damageNum
        
        if self.health < 0:
            self.isDead = True
            self.eventMan.broadcast(self.eventMan.evts['PLAYER_DEAD'])
        else:
            self.eventMan.broadcast(self.eventMan.evts['PLAYER_TAKE_DAMAGE'])

    def eventGet(self, event):
        if event == self.eventMan.evts['PLAYER_TAKE_DAMAGE']:
            self.currAnim = "damage"
        
        if not self.isDead:
            if event == self.eventMan.evts['PLAYER_GET_PT']:
                self.score += 10
                self.PutScore()
            
            if event == self.eventMan.evts['PLAYER_GET_HEALTH']:
                self.health = min(1.0,self.health+0.2) 
            
            
            
            