import random as rd
from chest_type import ChestType
from rarity import Rarity

def generate_chest_type():
    roll = rd.random()
    if roll <= 1/67067:
        return ChestType.DIVINE
    elif roll <= 1/200:
        return ChestType.GOD
    else:
        return ChestType.NORMAL
    
def generate_divine_chest():
    return [Rarity.DIVINE for _ in range(10)]

def sort_cards(cards):
    return sorted(cards, key=lambda card: card.value)

def generate_god_chest():
    # Génère 10 cartes selon les probabilités spécifiées
    cards = []
    for _ in range(10):
        roll = rd.random()
        if roll <= 0.01:
            cards.append(Rarity.UNIQUE)
        elif roll <= 0.29:
            cards.append(Rarity.MYTHIC)
        else:
            cards.append(Rarity.LEGENDARY)
    return sort_cards(cards)

def generate_normal_chest():
    # Génère 10 cartes selon les probabilités spécifiées
    cards = []
    # 6 premiers slots: 100% Communes
    for _ in range(6):
        cards.append(Rarity.COMMON)

    # 3 slots suivants: 75% Rares, 25% Épiques
    for _ in range(3):
        roll = rd.random()
        if roll <= 0.25:
            cards.append(Rarity.EPIC)
        else:
            cards.append(Rarity.RARE)

    # Dernier slot: 55% Rare, 30% Épique, 10% Légendaire, 4,9% Mythique, 0,1% Unique
    roll = rd.random()
    if roll <= 0.001:
        cards.append(Rarity.UNIQUE)
    elif roll <= 0.049:
        cards.append(Rarity.MYTHIC)
    elif roll <= 0.10:
        cards.append(Rarity.LEGENDARY)
    elif roll <= 0.30:
        cards.append(Rarity.EPIC)
    else:
        cards.append(Rarity.RARE)

    return sort_cards(cards)

def bonus_divine_card(cards):
    roll = rd.randint(1, 30000)
    if roll == 67:
        cards.append(Rarity.DIVINE)
    return cards

def generate_chest():
    chest_type = generate_chest_type()
    if chest_type == ChestType.DIVINE:
        return bonus_divine_card(generate_divine_chest())
    elif chest_type == ChestType.GOD:
        return bonus_divine_card(generate_god_chest())
    else:
        return bonus_divine_card(generate_normal_chest())
    

print(generate_chest())