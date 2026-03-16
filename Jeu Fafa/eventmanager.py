from soundmanager import SoundManager
from enum import Enum

class EventManager:
    def __init__(self):
        self.evts = Enum('evts', [('ENNEMY_TAKE_DAMAGE', 0), ('PLAYER_TAKE_DAMAGE', 1), ('PLAYER_FIRE', 2), ('NEW_WAVE', 4), ('PLAYER_WALK_START', 5), ('PLAYER_WALK_STOP', 6), ('PLAYER_JUMP', 7), ('PLAYER_LAND', 7), ('PLAYER_DEAD', 8), ('PLAYER_GET_PT', 9), ('PLAYER_GET_HEALTH', 10), ('PLAYER_GET_NEW_FLY', 11), ('PLAYER_GET_NEW_AK', 12), ('WAVE_END', 13), ('CHANGE_GUN', 14)])
        self.eventObjects = []

    
    def broadcast(self, event):
        for obj in self.eventObjects:
            obj.eventGet(event)

