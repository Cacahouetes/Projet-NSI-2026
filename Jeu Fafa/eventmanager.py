from soundmanager import SoundManager
from enum import Enum

class EventManager:
    def __init__(self):
        self.evts = Enum('evts', [('ENNEMY_TAKE_DAMAGE', 0), ('PLAYER_TAKE_DAMAGE', 1), ('PLAYER_FIRE', 2), ('PLAYER_GET_THING', 3), ('NEW_WAVE', 4), ('PLAYER_WALK_START', 5), ('PLAYER_WALK_STOP', 6)])
        self.eventObjects = []

    
    def broadcast(self, event):
        for obj in self.eventObjects:
            obj.eventGet(event)

