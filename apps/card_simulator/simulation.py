"""
simulation.py
=============
Simulateur de jeu complet.
Lance ce fichier directement pour tester l'équilibrage.

Usage :
    python simulation.py               # simulation standard (1 000 coffres)
    python simulation.py --n 10000     # simulation intensive
    python simulation.py --fusion      # test des fusions
    python simulation.py --economy     # test de l'économie
"""

import sys
import argparse
from collections import defaultdict

# Ajout du chemin des modules core + logic
sys.path.insert(0, "./core")
sys.path.insert(0, "./logic")

from generator import generate_normal_chest, generate_omni_chest
from card import Rarity, Category, RARITY_SELL_VALUE
from inventory import FUSION_RULES


# ═══════════════════════════════════════════════════════════════════════════════
# Statistiques de simulation
# ═══════════════════════════════════════════════════════════════════════════════

class SimStats:
    def __init__(self):
        self.total_chests      = 0
        self.total_cards       = 0
        self.rarity_count      = defaultdict(int)
        self.chest_type_count  = defaultdict(int)
        self.chest_size_count  = defaultdict(int)
        self.divine_bonus_count = 0   # bonus divine indépendant du type de coffre

    # ── Comptage rapide ──────────────────────────────────────────────────
    def count_card(self, rarity: Rarity):
        self.rarity_count[rarity] += 1

    # ── Métrique : fréquence d'apparition d'une rareté ───────────────────
    def freq(self, rarity: Rarity) -> float:
        """Pourcentage de cartes de cette rareté."""
        if self.total_cards == 0:
            return 0.0
        return self.rarity_count[rarity] / self.total_cards * 100

    def chests_per_rarity(self, rarity: Rarity) -> float:
        count = self.rarity_count[rarity]
        return self.total_chests / count if count else float("inf")


# ═══════════════════════════════════════════════════════════════════════════════
# Simulations
# ═══════════════════════════════════════════════════════════════════════════════

def simulate_category(category: Category, n: int) -> SimStats:
    stats = SimStats()
    for _ in range(n):
        chest = generate_normal_chest(category)
        stats.total_chests += 1
        stats.total_cards  += len(chest.cards)
        stats.chest_size_count[len(chest.cards)] += 1
        stats.chest_type_count[chest.type]        += 1
        for card in chest.cards:
            stats.count_card(card.rarity)
    return stats


def simulate_omni(n: int) -> SimStats:
    stats = SimStats()
    for _ in range(n):
        chest = generate_omni_chest()
        stats.total_chests += 1
        stats.total_cards  += len(chest.cards)
        stats.chest_size_count[len(chest.cards)] += 1
        stats.chest_type_count[chest.type]        += 1
        for card in chest.cards:
            stats.count_card(card.rarity)
    return stats


# ═══════════════════════════════════════════════════════════════════════════════
# Simulation d'économie
# ═══════════════════════════════════════════════════════════════════════════════

def simulate_economy(n_chests: int = 1_000) -> dict:
    """
    Simule n_chests coffres normaux (OMNI) et calcule :
    - Coût total dépensé
    - Valeur totale des cartes obtenues (si toutes vendues)
    - ROI (return on investment)
    - Nombre de coffres pour rentabiliser via la vente
    """
    from generator import generate_omni_chest, CHEST_COST
    from chest import ChestType

    cost_per_chest = CHEST_COST[ChestType.NORMAL]
    total_spent    = 0
    total_value    = 0
    rarity_value   = defaultdict(int)

    for _ in range(n_chests):
        chest        = generate_omni_chest()
        total_spent += cost_per_chest
        for card in chest.cards:
            v = RARITY_SELL_VALUE.get(card.rarity)
            if v:
                total_value             += v
                rarity_value[card.rarity] += v

    roi = (total_value / total_spent) * 100 if total_spent else 0

    return {
        "n_chests":    n_chests,
        "total_spent": total_spent,
        "total_value": total_value,
        "roi_pct":     roi,
        "rarity_value": rarity_value,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Simulation des fusions
# ═══════════════════════════════════════════════════════════════════════════════

def simulate_fusions(n: int = 10_000) -> dict:
    """
    Pour chaque rareté fusionnable, simule n tentatives et mesure
    le taux de succès réel vs. théorique et le coût moyen par réussite.
    """
    import random as rd
    results = {}

    for rarity, rule in FUSION_RULES.items():
        success_count = sum(1 for _ in range(n) if rd.random() < rule["success"])
        cost_per_win  = (rule["cost"] * n / success_count) if success_count else float("inf")

        results[rarity] = {
            "theoretical_rate": rule["success"] * 100,
            "actual_rate":      success_count / n * 100,
            "cost_per_attempt": rule["cost"],
            "cost_per_success": round(cost_per_win),
            "successes":        success_count,
        }

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Affichage
# ═══════════════════════════════════════════════════════════════════════════════

SEP  = "═" * 60
SEP2 = "─" * 60

def display_stats(stats: SimStats, title: str):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)
    print(f"  Coffres ouverts : {stats.total_chests:>10,}")
    print(f"  Cartes obtenues : {stats.total_cards:>10,}")
    print(f"  Cartes / coffre : {stats.total_cards / stats.total_chests:>10.2f}")
    print()

    # Répartition par rareté
    print(f"  {'Rareté':<14} {'Nb':>9}  {'%':>9}  {'1 / X coffres':>14}")
    print(f"  {SEP2}")
    for rarity in Rarity:
        count  = stats.rarity_count[rarity]
        pct    = stats.freq(rarity)
        freq   = stats.chests_per_rarity(rarity)
        freq_s = f"{freq:,.1f}" if freq != float("inf") else "—"
        print(f"  {rarity.name:<14} {count:>9,}  {pct:>8.4f}%  {freq_s:>14}")

    # Types de coffres déclenchés
    print(f"\n  {'Type de coffre':<20} {'Nb':>9}")
    print(f"  {SEP2}")
    from chest import ChestType
    for ct in ChestType:
        count = stats.chest_type_count[ct]
        print(f"  {ct.name:<20} {count:>9,}")

    # Taille des coffres
    print(f"\n  {'Taille':<10} {'Nb':>9}")
    print(f"  {SEP2}")
    for size, count in sorted(stats.chest_size_count.items()):
        print(f"  {size} cartes   {count:>9,}")


def display_economy(eco: dict):
    print(f"\n{SEP}")
    print(f"  SIMULATION ÉCONOMIQUE ({eco['n_chests']:,} coffres OMNI)")
    print(SEP)
    print(f"  Dépenses totales  : {eco['total_spent']:>12,} 🪙")
    print(f"  Valeur des cartes : {eco['total_value']:>12,} 🪙")
    print(f"  ROI               : {eco['roi_pct']:>11.1f} %")
    print()
    print(f"  {'Rareté':<14} {'Valeur totale':>14}")
    print(f"  {SEP2}")
    for rarity in Rarity:
        v = eco['rarity_value'].get(rarity, 0)
        if v:
            print(f"  {rarity.name:<14} {v:>14,} 🪙")

    if eco['roi_pct'] < 30:
        print("\n  ⚠️  ROI faible : les joueurs perdent beaucoup de valeur en ouvrant des coffres.")
    elif eco['roi_pct'] > 80:
        print("\n  ⚠️  ROI élevé : le jeu est trop généreux, l'économie risque l'inflation.")
    else:
        print(f"\n  ✅  ROI équilibré ({eco['roi_pct']:.1f} %).")


def display_fusions(results: dict):
    print(f"\n{SEP}")
    print(f"  SIMULATION DES FUSIONS")
    print(SEP)
    print(f"  {'Rareté':<14} {'Théo%':>7} {'Réel%':>7} {'Coût/essai':>11} {'Coût/succès':>12}")
    print(f"  {SEP2}")
    for rarity, data in results.items():
        print(
            f"  {rarity.name:<14}"
            f" {data['theoretical_rate']:>6.1f}%"
            f" {data['actual_rate']:>6.1f}%"
            f" {data['cost_per_attempt']:>11,}"
            f" {data['cost_per_success']:>12,}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Point d'entrée
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Simulateur de coffres NSI")
    parser.add_argument("--n",       type=int, default=1_000,
                        help="Nombre de coffres à simuler (défaut : 1 000)")
    parser.add_argument("--fusion",  action="store_true",
                        help="Simuler les fusions")
    parser.add_argument("--economy", action="store_true",
                        help="Simuler l'économie")
    parser.add_argument("--all",     action="store_true",
                        help="Lancer toutes les simulations")
    args = parser.parse_args()

    N = args.n

    if args.all or (not args.fusion and not args.economy):
        # Simulation par catégorie
        for cat in Category:
            stats = simulate_category(cat, N)
            display_stats(stats, f"CATÉGORIE {cat.name} – {N:,} coffres")

        # Simulation OMNI
        omni = simulate_omni(N)
        display_stats(omni, f"OMNI – {N:,} coffres")

    if args.all or args.fusion:
        fusion_results = simulate_fusions(10_000)
        display_fusions(fusion_results)

    if args.all or args.economy:
        eco = simulate_economy(N)
        display_economy(eco)


if __name__ == "__main__":
    main()