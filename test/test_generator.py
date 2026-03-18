#Projet : Card Opening Simulator
#Auteurs : Fahreddin, Thyraël, Tristan, Augustin

"""
test_generator.py
Tests unitaires du générateur de coffres (generator.py).
"""

import sys
import os

# Ajouter les chemins nécessaires
HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES = os.sep.join([os.path.dirname(HERE), "sources"])
sys.path.insert(0, os.sep.join([SOURCES, "apps", "card_simulator", "core"]))
sys.path.insert(0, os.sep.join([SOURCES, "apps", "card_simulator", "logic"]))

from card import Rarity, Category


# Tests du générateur de type de coffre

def test_chest_type_distribution():
    """
    Vérifie que la distribution des types de coffres sur 10 000 tirages
    est cohérente avec les probabilités définies.
    Taux attendu GODPACK : ~0,5% (1/200)
    Taux attendu DIVINE  : ~0,00149% (1/67 067)
    """
    from generator import generate_chest_type
    from chest import ChestType

    N = 10_000
    counts = {ChestType.NORMAL: 0, ChestType.GOD: 0, ChestType.DIVINE: 0}

    for _ in range(N):
        t = generate_chest_type()
        counts[t] += 1

    normal_pct = counts[ChestType.NORMAL] / N * 100
    god_pct = counts[ChestType.GOD]    / N * 100

    print(f"Normal : {normal_pct:.2f}% (attendu ~99.5%)")
    print(f"GODPACK: {god_pct:.2f}% (attendu ~0.5%)")
    print(f"DIVINE : {counts[ChestType.DIVINE]} occurrences sur {N} (attendu ~0)")

    # Tolérance large car aléatoire
    assert 98.5 < normal_pct < 100, f"Normal hors plage : {normal_pct:.2f}%"
    assert god_pct < 2.0, f"GODPACK trop fréquent : {god_pct:.2f}%"

    print("✓ test_chest_type_distribution OK")


def test_normal_chest_has_10_cards():
    """Un coffre normal doit contenir exactement 10 cartes (sans bonus Divine)."""
    from generator import generate_normal_chest_cards

    cards = generate_normal_chest_cards(category=None)
    assert len(cards) == 10, f"Attendu 10 cartes, obtenu {len(cards)}"
    print("✓ test_normal_chest_has_10_cards OK")


def test_normal_chest_slots_1_to_6_are_communes():
    """Les 6 premières cartes (après tri) doivent inclure au moins des Communes."""
    from generator import generate_normal_chest_cards

    # Tirer 100 coffres et vérifier qu'on a toujours au moins 6 Communes
    for _ in range(100):
        cards = generate_normal_chest_cards()
        communes = [c for c in cards if c.rarity == Rarity.COMMUNE]
        assert len(communes) >= 6, f"Moins de 6 Communes : {len(communes)}"

    print("✓ test_normal_chest_slots_1_to_6_are_communes OK")


def test_god_chest_only_high_rarity():
    """Un GODPACK ne doit contenir que Légendaire, Mythique ou Unique."""
    from generator import generate_god_chest_cards

    allowed = {Rarity.LÉGENDAIRE, Rarity.MYTHIQUE, Rarity.UNIQUE}
    for _ in range(50):
        cards = generate_god_chest_cards()
        for card in cards:
            assert card.rarity in allowed, \
                f"Rareté inattendue dans GODPACK : {card.rarity}"

    print("✓ test_god_chest_only_high_rarity OK")


def test_divine_chest_only_divine():
    """Un DIVINE PACK ne doit contenir que des cartes Divines."""
    from generator import generate_divine_chest_cards

    cards = generate_divine_chest_cards()
    assert len(cards) == 10
    for card in cards:
        assert card.rarity == Rarity.DIVINE, \
            f"Carte non-Divine dans DIVINE PACK : {card.rarity}"

    print("✓ test_divine_chest_only_divine OK")


def test_maybe_add_divine_rare():
    """
    maybe_add_divine() ne doit ajouter une carte que très rarement.
    Sur 1000 tirages, on s'attend à 0 ou très peu d'ajouts.
    """
    from generator import maybe_add_divine

    added = 0
    for _ in range(1000):
        cards_before = [None] * 10  # liste factice
        result = maybe_add_divine(list(cards_before))
        if len(result) == 11:
            added += 1

    print(f"  Divines ajoutées sur 1000 : {added} (attendu : 0 ou 1)")
    assert added < 5, f"Trop de cartes Divines ajoutées : {added}"
    print("✓ test_maybe_add_divine_rare OK")


if __name__ == "__main__":
    print("Tests du générateur de coffres\n")
    try:
        test_chest_type_distribution()
        test_normal_chest_has_10_cards()
        test_normal_chest_slots_1_to_6_are_communes()
        test_god_chest_only_high_rarity()
        test_divine_chest_only_divine()
        test_maybe_add_divine_rare()
        print("\n✓ Tous les tests sont passés.")
    except AssertionError as e:
        print(f"\n✗ ÉCHEC : {e}")
        sys.exit(1)
    except ImportError as e:
        print(f"\n⚠ Import manquant (lancer depuis la racine du projet) : {e}")
        sys.exit(1)