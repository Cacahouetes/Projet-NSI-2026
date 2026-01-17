from inventory import Inventory
from cards import Card, Rarity

class Player:
    def __init__(self, coins=0):
        self.coins = coins
        self.inventory = Inventory()

    def can_buy(self, cost):
        return self.coins >= cost

    def buy_chest(self, chest):
        if not self.can_buy(chest.cost):
            raise ValueError("Pas assez de pièces pour acheter ce coffre")

        self.coins -= chest.cost
        self.inventory.add_cards(chest.cards)