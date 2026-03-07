from card import Card, Rarity

class CardDex:
    def __init__(self, total_cards):
        self.total_cards = total_cards
        self.collected_cards = set()
        self.diploma_unlocked = False
    
    def add_card(self, card):
        self.collected_cards.add(card.card_id)
        
    def completion_percentage(self):
        return (len(self.collected_cards) / self.total_cards)*100
    
    def is_complete(self):
        return len(self.collected_cards) == self.total_cards


CardDex = CardDex(756)
CardDex.add_card(Card(1, 'r', Rarity.COMMUNE, 'e', 1,2,2,'rere', 'rerer','zzgreg'))
print(CardDex.collected_cards)
CardDex.add_card(Card(2, 'r', Rarity.COMMUNE, 'e', 1,2,2,'rere', 'rerer','zzgreg'))
print(CardDex.collected_cards)