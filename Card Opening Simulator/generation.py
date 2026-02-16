import random as rd
from chest import ChestType
from card import Rarity
from database import CardRepository

REPOSITORY = CardRepository()


def draw_card(rarity, category=None):
    return REPOSITORY.get_random_card(rarity, category)

# Tirage du type de coffre
def generate_chest_type():
    roll = rd.random()
    if roll <= 1/67067:
        return ChestType.DIVINE
    elif roll <= (1/67067+1/200):
        return ChestType.GOD
    else:
        return ChestType.NORMAL

# Utilitaire pour trier les cartes par rareté
def sort_cards(cards):
    return sorted(cards, key=lambda card: card.rarity.value)

# Coffre Divin
def generate_divine_chest():
    return [draw_card(Rarity.DIVINE) for _ in range(10)]

# Coffre de Dieu
def generate_god_chest(category):
    # Génère 10 cartes selon les probabilités spécifiées
    cards = []
    for _ in range(10):
        roll = rd.random()
        if roll < 0.01:
            cards.append(draw_card(Rarity.UNIQUE, category))
        elif roll < 0.31:
            cards.append(draw_card(Rarity.MYTHIC, category))
        else:
            cards.append(draw_card(Rarity.LEGENDARY, category))
    return sort_cards(cards)

# Coffre Omni dieu 
def generate_god_omni_chest():
    # Génère 10 cartes selon les probabilités spécifiées
    cards = []
    for _ in range(10):
        roll = rd.random()
        if roll < 0.05:
            cards.append(draw_card(Rarity.UNIQUE))
        elif roll < 0.5:
            cards.append(draw_card(Rarity.MYTHIC))
        else:
            cards.append(draw_card(Rarity.LEGENDARY))
    return sort_cards(cards)

# Coffre Normal
def generate_cards_normal_chest(category):
    # Génère 10 cartes selon les probabilités spécifiées
    cards = []
    # 6 premiers slots: 100% Communes
    for _ in range(6):
        cards.append(draw_card(Rarity.COMMON, category))

    # 3 slots suivants: 75% Rares, 25% Épiques
    for _ in range(3):
        roll = rd.random()
        if roll < 0.25:
            cards.append(draw_card(Rarity.EPIC, category))
        else:
            cards.append(draw_card(Rarity.RARE, category))

    # Dernier slot: 55% Rare, 30% Épique, 10% Légendaire, 4,9% Mythique, 0,1% Unique
    roll = rd.random()
    if roll < 0.001:
        cards.append(draw_card(Rarity.UNIQUE, category))
    elif roll < 0.05:
        cards.append(draw_card(Rarity.MYTHIC, category))
    elif roll < 0.15:
        cards.append(draw_card(Rarity.LEGENDARY, category))
    elif roll < 0.45:
        cards.append(draw_card(Rarity.EPIC, category))
    else:
        cards.append(draw_card(Rarity.RARE, category))

    return sort_cards(cards)

def generate_cards_omni_chest():
    # Génère 10 cartes selon les probabilités spécifiées
    cards = []
    # 6 premiers slots: 100% Communes
    for _ in range(5):
        cards.append(draw_card(Rarity.COMMON))

    # 3 slots suivants: 60% Rares, 40% Épiques
    for _ in range(3):
        roll = rd.random()
        if roll < 0.40:
            cards.append(draw_card(Rarity.EPIC))
        else:
            cards.append(draw_card(Rarity.RARE))

    # 2 dernier slots: 40% Épique, 35% Légendaire, 24.5% Mythique, 0,5% Unique
    for _ in range(2):
        roll = rd.random()
        if roll < 0.005:
            cards.append(draw_card(Rarity.UNIQUE))
        elif roll < 0.25:
            cards.append(draw_card(Rarity.MYTHIC))
        elif roll < 0.60:
            cards.append(draw_card(Rarity.LEGENDARY))
        else:
            cards.append(draw_card(Rarity.EPIC))
    return sort_cards(cards)

def bonus_divine_card(cards):
    roll = rd.randint(1, 30000)
    if roll == 67:
        cards.append(draw_card(Rarity.DIVINE))
    return cards

def generate_normal_chest(category):
    chest_type = generate_chest_type()
    
    if chest_type == ChestType.DIVINE:
        cards = generate_divine_chest()
    elif chest_type == ChestType.GOD:
        cards = generate_god_chest(category)
    else:
        cards = generate_cards_normal_chest(category)
    
    return bonus_divine_card(cards)
    
def generate_omni_chest():
    chest_type = generate_chest_type()
    
    if chest_type == ChestType.DIVINE:
        cards = generate_divine_chest()
    elif chest_type == ChestType.GOD:
        cards = generate_god_omni_chest()
    else:
        cards = generate_cards_omni_chest()
        
    return bonus_divine_card(cards)