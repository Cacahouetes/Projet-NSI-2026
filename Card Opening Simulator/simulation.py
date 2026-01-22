from generation import generate_normal_chest, generate_omni_chest
from card import Rarity, Category
from collections import defaultdict

class Stats:
    def __init__(self):
        self.total_chests = 0
        self.total_cards = 0

        self.rarity_count = defaultdict(int)
        self.category_count = defaultdict(int)
        self.chest_size_count = defaultdict(int)

        self.divine_count = 0
        self.unique_count = 0
        self.mythic_count = 0
        self.legendary_count = 0
        self.epic_count = 0
        self.rare_count = 0
        self.common_count = 0
    
        
def count_card(stats, rarity):
    stats.rarity_count[rarity] += 1
    
    if rarity == Rarity.DIVINE:
        stats.divine_count += 1
    elif rarity == Rarity.UNIQUE:
        stats.unique_count += 1
    elif rarity == Rarity.MYTHIC:
        stats.mythic_count += 1
    elif rarity == Rarity.LEGENDARY:
        stats.legendary_count += 1
    elif rarity == Rarity.EPIC:
        stats.epic_count += 1
    elif rarity == Rarity.RARE:
        stats.rare_count += 1
    elif rarity == Rarity.COMMON:
        stats.common_count += 1
 
        
def simulate_category(category, n):
    stats = Stats()

    for _ in range(n):
        cards = generate_normal_chest(category)
        
        stats.total_chests += 1
        stats.total_cards += len(cards)
        stats.chest_size_count[len(cards)] += 1

        for card in cards:
            count_card(stats, card.rarity)

    return stats

def simulate_omni(n):
    stats = Stats()

    for _ in range(n):
        cards = generate_omni_chest()
        stats.total_chests += 1
        stats.total_cards += len(cards)
        stats.chest_size_count[len(cards)] += 1

        for card in cards:
            count_card(stats, card.rarity)
            
    return stats
        


def display_stats(stats, title):
    print(f"\n=== {title} ===")
    print(f"Coffres ouverts : {stats.total_chests}")
    print(f"Cartes obtenues : {stats.total_cards}\n")

    for rarity in Rarity:
        count = stats.rarity_count[rarity]
        percent = (count / stats.total_cards) * 100 if stats.total_cards else 0
        print(f"{rarity.name:<10} : {count:<10} ({percent:.6f}%)")

    print("\n--- Metrics game design ---")
    if stats.common_count:
        print(f"1 COMMON tous les ~{stats.total_chests / stats.common_count:.1f} coffres")
    if stats.rare_count:
        print(f"1 RARE tous les ~{stats.total_chests / stats.rare_count:.1f} coffres")
    if stats.epic_count:
        print(f"1 EPIC tous les ~{stats.total_chests / stats.epic_count:.1f} coffres")
    if stats.legendary_count:
        print(f"1 LEGENDARY tous les ~{stats.total_chests / stats.legendary_count:.1f} coffres")
    if stats.mythic_count:
        print(f"1 MYTHIC tous les ~{stats.total_chests / stats.mythic_count:.1f} coffres")
    if stats.unique_count:
        print(f"1 UNIQUE tous les ~{stats.total_chests / stats.unique_count:.1f} coffres")
    if stats.divine_count:
        print(f"1 DIVINE tous les ~{stats.total_chests / stats.divine_count:.1f} coffres")

    print("\n--- Taille des coffres ---")
    for size, count in sorted(stats.chest_size_count.items()):
        print(f"{size} cartes : {count}")
        
if __name__ == "__main__":
    N = 1_000_000

    meme_stats = simulate_category(Category.MEME, N)
    omni_stats = simulate_omni(N)
    display_stats(meme_stats, "CATÉGORIE MEME")
    display_stats(omni_stats, "OMNI")