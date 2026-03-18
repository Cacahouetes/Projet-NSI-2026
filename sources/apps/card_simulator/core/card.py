#Projet : Card Opening Simulator
#Auteurs : Fahreddin, Thyraël, Tristan, Augustin

from enum import Enum

class Rarity(Enum):
    COMMUNE    = 1
    RARE       = 2
    ÉPIQUE     = 3
    LÉGENDAIRE = 4
    MYTHIQUE   = 5
    UNIQUE     = 6
    DIVINE     = 7

class Category(Enum):
    MEME        = 1
    MOTS        = 2
    OBJETS      = 3
    PERSONNAGES = 4
    CONCEPTS    = 5

RARITY_SELL_VALUE = {
    Rarity.COMMUNE:    5,
    Rarity.RARE:       50,
    Rarity.ÉPIQUE:     80,
    Rarity.LÉGENDAIRE: 300,
    Rarity.MYTHIQUE:   1200,
    Rarity.UNIQUE:     5000,
    Rarity.DIVINE:     None,  # Invendable
}

class Card:
    def __init__(self, card_id, name, rarity, category, stat1, stat2, stat3,
                 description, author, image_path):
        self.card_id    = card_id
        self.name       = name
        self.rarity     = rarity
        self.category   = category
        self.stat1      = stat1
        self.stat2      = stat2
        self.stat3      = stat3
        self.description = description
        self.author     = author
        self.image_path = image_path

    def __repr__(self):
        return f"[{self.card_id}] {self.name} – {self.category} ({self.rarity.name})"