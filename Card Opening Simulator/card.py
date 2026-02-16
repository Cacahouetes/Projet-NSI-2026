from enum import Enum


class Rarity(Enum):
    COMMON = 1
    RARE = 2
    EPIC = 3
    LEGENDARY = 4
    MYTHIC = 5
    UNIQUE = 6
    DIVINE = 7


class Category(Enum):
    MEME = 1
    MOTS = 2
    OBJETS = 3
    PERSONNAGES = 4
    CONCEPTS = 5


RARITY_SELL_VALUE = {
    Rarity.COMMON: 5,
    Rarity.RARE: 50,
    Rarity.EPIC: 80,
    Rarity.LEGENDARY: 300,
    Rarity.MYTHIC: 1200,
    Rarity.UNIQUE: 5000,
    Rarity.DIVINE: None,  # Invendable
}


class Card:
    def __init__(
        self,
        rarity,
        category=None,
        card_id=None,
        name=None,
        stat1=None,
        stat2=None,
        stat3=None,
        description=None,
        author=None,
        image_path=None,
    ):
        self.rarity = rarity
        self.category = category
        self.id = card_id
        self.name = name
        self.stat1 = stat1
        self.stat2 = stat2
        self.stat3 = stat3
        self.description = description
        self.author = author
        self.image_path = image_path

    def __repr__(self):
        display_name = f" - {self.name}" if self.name else ""
        return f"[{self.id}]: {self.rarity.name} ({self.category}){display_name}"
