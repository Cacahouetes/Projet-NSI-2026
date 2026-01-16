class Chest:
    def __init__(self, type, category, cards, cost):
        self.type = type
        self.category = category
        self.cards = cards
        self.cost = cost

    def __len__(self):
        return len(self.cards)
    
    def __str__(self):
        return f"Chest Type: {self.type}, Cost: {self.cost}, Cards: {len(self.cards)}"