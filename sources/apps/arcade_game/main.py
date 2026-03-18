#Projet : Card Opening Simulator
#Auteurs : Fahreddin, Thyraël, Tristan, Augustin

import pygame
import sqlite3
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "data", "game.db"))
sys.path.insert(0, os.path.join(HERE, 'engine'))
sys.path.insert(0, os.path.join(HERE, 'entities'))

from level import Level

running = True 
dt = 0.1

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Arial', 40)

win = pygame.display.set_mode((1280, 736), vsync=1)
pygame.display.set_caption("Arcade Game")
clock = pygame.time.Clock()

level = Level()
session_ms = 0

#boucle principale du jeu
while running:
    keys = pygame.key.get_pressed()
    dt = clock.tick(60)
    session_ms += dt
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False


        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    win.fill((60,48,39))
    level.update(dt, events)
    level.draw(win)

    pygame.display.flip()


# Sauvegarde du playtime
try:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT player_id FROM PLAYERS ORDER BY player_id LIMIT 1")
        row = cur.fetchone()
        if row:
            cur.execute("""
                UPDATE PLAYER_STATS
                SET play_time_seconds = play_time_seconds + ?
                WHERE player_id = ?
            """, (session_ms // 1000, row[0]))
            conn.commit()
except Exception:
    pass

pygame.quit()
sys.exit(0)

"""
change_gun.wav
jump.wav
get_point.wav
get_health.wav
get_new_gun.wav
new_wave.wav
"""
