#Projet : Card Opening Simulator
#Auteurs : Fahreddin, Thyraël, Tristan, Augustin

"""
generator.py
Génération des coffres et tirage des cartes.
"""

import random as rd

from chest import Chest, ChestType
from card import Rarity
from card_repository import CardRepository

REPOSITORY = CardRepository()

# Coûts des coffres (en pièces)
CHEST_COST = {
    'normal' : 250,
    'omni' : 1000
}


# Utilitaires

def draw_card(rarity: Rarity, category=None):
    return REPOSITORY.get_random_card(rarity, category)


def sort_cards(cards: list) -> list:
    return sorted(cards, key=lambda c: c.rarity.value)


# Type de coffre aléatoire

def generate_chest_type() -> ChestType:
    roll = rd.random()
    if roll <= 1 / 67_067:
        return ChestType.DIVINE
    elif roll <= (1 / 67_067 + 1 / 200):
        return ChestType.GOD
    return ChestType.NORMAL


# Génération des cartes selon le type de coffre

def generate_divine_chest_cards() -> list:
    return [draw_card(Rarity.DIVINE) for _ in range(10)]


def generate_god_chest_cards(category=None) -> list:
    cards = []
    for _ in range(10):
        roll = rd.random()
        if roll < 0.01:
            cards.append(draw_card(Rarity.UNIQUE, category))
        elif roll < 0.31:
            cards.append(draw_card(Rarity.MYTHIQUE, category))
        else:
            cards.append(draw_card(Rarity.LÉGENDAIRE, category))
    return sort_cards(cards)


def generate_normal_chest_cards(category=None) -> list:
    cards = []

    # 6 slots → 100 % Communes
    for _ in range(6):
        cards.append(draw_card(Rarity.COMMUNE, category))

    # 3 slots → 75 % Rares / 25 % Épiques
    for _ in range(3):
        if rd.random() < 0.25:
            cards.append(draw_card(Rarity.ÉPIQUE, category))
        else:
            cards.append(draw_card(Rarity.RARE, category))

    # Dernier slot - table spéciale
    roll = rd.random()
    if roll < 0.001:
        cards.append(draw_card(Rarity.UNIQUE, category))
    elif roll < 0.05:
        cards.append(draw_card(Rarity.MYTHIQUE, category))
    elif roll < 0.15:
        cards.append(draw_card(Rarity.LÉGENDAIRE, category))
    elif roll < 0.45:
        cards.append(draw_card(Rarity.ÉPIQUE, category))
    else:
        cards.append(draw_card(Rarity.RARE, category))

    return sort_cards(cards)


def generate_omni_chest_cards() -> list:
    """Coffre OMNI : sans filtre de catégorie, légèrement meilleures chances."""
    cards = []

    # 5 slots → Communes
    for _ in range(5):
        cards.append(draw_card(Rarity.COMMUNE))

    # 3 slots → 60 % Rares / 40 % Épiques
    for _ in range(3):
        if rd.random() < 0.40:
            cards.append(draw_card(Rarity.ÉPIQUE))
        else:
            cards.append(draw_card(Rarity.RARE))

    # 2 derniers slots - table améliorée
    for _ in range(2):
        roll = rd.random()
        if roll < 0.005:
            cards.append(draw_card(Rarity.UNIQUE))
        elif roll < 0.25:
            cards.append(draw_card(Rarity.MYTHIQUE))
        elif roll < 0.60:
            cards.append(draw_card(Rarity.LÉGENDAIRE))
        else:
            cards.append(draw_card(Rarity.ÉPIQUE))

    return sort_cards(cards)


# Bonus Divine

def maybe_add_divine(cards: list) -> list:
    """1 chance sur 30 000 d'ajouter une carte Divine en bonus."""
    if rd.randint(1, 30_000) == 67:
        cards.append(draw_card(Rarity.DIVINE))
    return cards


# Points d'entrée publics

def generate_normal_chest(category=None) -> Chest:
    chest_type = generate_chest_type()

    if chest_type == ChestType.DIVINE:
        cards = generate_divine_chest_cards()
    elif chest_type == ChestType.GOD:
        cards = generate_god_chest_cards(category)
    else:
        cards = generate_normal_chest_cards(category)

    cards = maybe_add_divine(cards)
    cost  = CHEST_COST['normal']
    return Chest(type=chest_type, category=category, cards=cards, cost=cost)


def generate_omni_chest() -> Chest:
    chest_type = generate_chest_type()

    if chest_type == ChestType.DIVINE:
        cards = generate_divine_chest_cards()
    elif chest_type == ChestType.GOD:
        cards = generate_god_chest_cards(category=None)
    else:
        cards = generate_omni_chest_cards()

    cards = maybe_add_divine(cards)
    cost  = CHEST_COST['omni']
    return Chest(type=chest_type, category=None, cards=cards, cost=cost)