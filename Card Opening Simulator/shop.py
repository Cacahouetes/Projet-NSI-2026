import random as rd
import time
from cards import Rarity, Card, RARITY_SELL_VALUE

# Constante du shop
SHOP_PRICE_MULTIPLIER = 2  # Prix augmenté de 100% par rapport au prix de base

class Shop:
    def __init__(self):
        self.last_restock = time.time()
        self.shop_cards = self.generate_shop_cards()
    
    def restock(self):
        self.cards = self.generate_shop_cards()
        self.last_restock = time.time()
    
    def generate_shop_cards(self):
        shop_cards = []
        
        available_rarities = [
            Rarity.COMMON,
            Rarity.RARE,
            Rarity.EPIC,
            Rarity.LEGENDARY,
            Rarity.MYTHIC,
            Rarity.UNIQUE
        ]
        
        for _ in range(3):
            roll = rd.random()
            if roll < 0.02:
                rarity = Rarity.UNIQUE
            elif roll < 0.06:
                rarity = Rarity.MYTHIC
            elif roll < 0.12:
                rarity = Rarity.LEGENDARY
            elif roll < 0.20:
                rarity = Rarity.EPIC
            elif roll < 0.30:
                rarity = Rarity.RARE
            else:
                rarity = Rarity.COMMON
            
            shop_cards.append(Card(rarity))
        
        return shop_cards
    
    def get_card_price(self, card):
        value = RARITY_SELL_VALUE.get(card.rarity)
        return int(value * SHOP_PRICE_MULTIPLIER)
    
    def buy_card(self, player, index):
        if index < 0 or index >= len(self.shop_cards):
            raise IndexError("Index de carte invalide")
        
        card = self.shop_cards[index]
        price = self.get_card_price(card)
        
        if not player.can_buy(price):
            raise ValueError("Pas assez de pièces pour acheter cette carte")
        
        player.coins -= price
        player.inventory.add_card(card)
        self.shop_cards.pop(index)