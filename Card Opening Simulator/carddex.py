class CardDex:
    def __init__(self, total_cards):
        self.total_cards = total_cards
        self.collected_cards = set()
        self.diploma_unlocked = False
        
    def add_card(self, card):
        if card.id is not None:
            self.collected_cards.add(card.id)
        
    def completion_percentage(self):
        return (len(self.collected_cards) / self.total_cards)*100
    
    def is_complete(self):
        return len(self.collected_cards) == self.total_cards