import random as rd
from collections import defaultdict
from card import Card, Rarity, RARITY_SELL_VALUE

# Constante des fusions de cartes
# Table de fusion
FUSION_RULES = {
    Rarity.COMMON: {"needed": 3, "success": 1, "cost": 4*RARITY_SELL_VALUE[Rarity.COMMON], "result": Rarity.RARE},
    Rarity.RARE: {"needed": 3, "success": 0.9, "cost": 4*RARITY_SELL_VALUE[Rarity.RARE], "result": Rarity.EPIC},
    Rarity.EPIC: {"needed": 3, "success": 0.25, "cost": 4*RARITY_SELL_VALUE[Rarity.EPIC], "result": Rarity.LEGENDARY},
    Rarity.LEGENDARY: {"needed": 3, "success": 0.9, "cost": 4*RARITY_SELL_VALUE[Rarity.LEGENDARY], "result": Rarity.MYTHIC},
    Rarity.MYTHIC: {"needed": 3, "success": 0.05, "cost": 4*RARITY_SELL_VALUE[Rarity.MYTHIC], "result": Rarity.UNIQUE},
}

class Inventory:
    def __init__(self):
        self.cards = []

    def add_cards(self, cards):
        self.cards.extend(cards)

    def add_card(self, card):
        self.cards.append(card)

    def sell_card(self, card):
        if card not in self.cards:
            return False

        value = RARITY_SELL_VALUE.get(card.rarity)
        if value is None:
            return False

        self.cards.remove(card)
        return value

    def sell_all_by_rarity(self, rarity):
        value = RARITY_SELL_VALUE.get(rarity)
        if value is None:
            return False

        to_sell = [card for card in self.cards if card.rarity == rarity]
        gained = len(to_sell) * value

        self.cards = [card for card in self.cards if card.rarity != rarity]
        return gained

    def count_by_rarity(self):
        counts = defaultdict(int)
        for card in self.cards:
            counts[card.rarity] += 1
        return counts

    def total_value(self):
        total = 0
        for card in self.cards:
            value = RARITY_SELL_VALUE.get(card.rarity)
            if value:
                total += value
        return total
    
    def fuse_cards(self, coins_available, rarity):
        if rarity not in FUSION_RULES:
            raise ValueError("Impossible de fusionner cette rareté")
        
        rule = FUSION_RULES[rarity]
        needed = rule["needed"]
        cost = rule["cost"]
        success_rate = rule["success"]
        result_rarity = rule["result"]
        
        # Vérifier si le joueur a assez de cartes
        available_cards = [card for card in self.cards if card.rarity == rarity]
        if len(available_cards) < needed:
            return False, 0
        
        # Vérifier si le joueur a assez de pièces
        if coins_available < cost:
            return False, 0
        
        # Retirer les cartes utilisées pour la fusion
        for _ in range(needed):
            self.cards.remove(available_cards.pop())
            
        # Déterminer le succès de la fusion
        if rd.random() <= success_rate:
            new_card = Card(result_rarity)
            self.cards.append(new_card)
            return True, cost
        else:
            return False, cost
        
    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return f"Inventory({len(self.cards)} cards)"