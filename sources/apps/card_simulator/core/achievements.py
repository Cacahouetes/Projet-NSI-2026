#Projet : Card Opening Simulator
#Auteurs : Fahreddin, Thyraël, Tristan, Augustin

from card import Rarity, Category


class Achievement:
    def __init__(self, id: str, name: str, description: str, condition):
        self.id          = id
        self.name        = name
        self.description = description
        self.condition   = condition   # callable(stats) -> bool


# Définition de tous les succès du jeu

ACHIEVEMENTS: list[Achievement] = [

    # Coffres
    Achievement("first_chest",   "Premier coffre !",     "Ouvrir son premier coffre",
                lambda s: s.chests_opened >= 1),
    Achievement("chest_10",      "Collectionneur débutant", "Ouvrir 10 coffres",
                lambda s: s.chests_opened >= 10),
    Achievement("chest_50",      "Ouvre-boîte",          "Ouvrir 50 coffres",
                lambda s: s.chests_opened >= 50),
    Achievement("chest_100",     "Centenaire",           "Ouvrir 100 coffres",
                lambda s: s.chests_opened >= 100),
    Achievement("chest_500",     "Addict aux coffres",   "Ouvrir 500 coffres",
                lambda s: s.chests_opened >= 500),

    # Raretés obtenues
    Achievement("first_rare",    "Première Rare",        "Obtenir une carte Rare",
                lambda s: s.cards_by_rarity.get(Rarity.RARE, 0) >= 1),
    Achievement("first_epic",    "Première Épique",      "Obtenir une carte Épique",
                lambda s: s.cards_by_rarity.get(Rarity.ÉPIQUE, 0) >= 1),
    Achievement("first_legend",  "Première Légendaire",  "Obtenir une carte Légendaire",
                lambda s: s.cards_by_rarity.get(Rarity.LÉGENDAIRE, 0) >= 1),
    Achievement("first_mythic",  "Première Mythique",    "Obtenir une carte Mythique",
                lambda s: s.cards_by_rarity.get(Rarity.MYTHIQUE, 0) >= 1),
    Achievement("first_unique",  "Première Unique",      "Obtenir une carte Unique",
                lambda s: s.cards_by_rarity.get(Rarity.UNIQUE, 0) >= 1),
    Achievement("first_divine",  "Élue des Dieux",       "Obtenir une carte Divine",
                lambda s: s.divine_obtained >= 1),

    # Fusions
    Achievement("first_fusion",  "Alchimiste",           "Réussir sa première fusion",
                lambda s: s.fusions_success >= 1),
    Achievement("fusion_10",     "Maître du creuset",    "Réussir 10 fusions",
                lambda s: s.fusions_success >= 10),
    Achievement("fusion_fail",   "Ça arrive…",           "Rater une fusion",
                lambda s: s.fusions_failed >= 1),
    Achievement("fusion_50",     "Forges ardentes",      "Tenter 50 fusions",
                lambda s: s.fusions_attempted >= 50),

    # Économie
    Achievement("earn_1000",     "Premier millier",      "Gagner 1 000 pièces au total",
                lambda s: s.coins_earned >= 1_000),
    Achievement("earn_10000",    "Petit capitaliste",    "Gagner 10 000 pièces au total",
                lambda s: s.coins_earned >= 10_000),
    Achievement("earn_100000",   "Grand Trésorier",      "Gagner 100 000 pièces au total",
                lambda s: s.coins_earned >= 100_000),
    Achievement("sell_10",       "Bradeur",              "Vendre 10 cartes",
                lambda s: s.cards_sold >= 10),
    Achievement("sell_100",      "Liquidateur",          "Vendre 100 cartes",
                lambda s: s.cards_sold >= 100),

    # Daily streak
    Achievement("daily_7",       "Semaine complète",     "Atteindre un streak de 7 jours",
                lambda s: s.daily_best_streak >= 7),
    Achievement("daily_30",      "Mois de discipline",   "Atteindre un streak de 30 jours",
                lambda s: s.daily_best_streak >= 30),

    # Shop
    Achievement("shop_first",    "Premier achat",        "Acheter une carte dans le shop",
                lambda s: s.shop_cards_bought >= 1),
    Achievement("shop_10",       "Client fidèle",        "Acheter 10 cartes dans le shop",
                lambda s: s.shop_cards_bought >= 10),

    # CardDex
    Achievement("carddex_25",    "Curieux",              "Découvrir 25 % du CardDex",
                lambda s: getattr(s, '_carddex_pct', 0) >= 25),
    Achievement("carddex_50",    "Explorateur",          "Découvrir 50 % du CardDex",
                lambda s: getattr(s, '_carddex_pct', 0) >= 50),
    Achievement("carddex_100",   "Dieu du CardDex",      "Compléter le CardDex à 100 %",
                lambda s: getattr(s, '_carddex_pct', 0) >= 100),
]


class AchievementManager:
    """Vérifie et débloque les succès d'un joueur."""

    def check_all(self, player) -> list[Achievement]:
        """
        Parcourt tous les succès non encore débloqués.
        Injecte le % du CardDex dans les stats avant les vérifications.
        Retourne la liste des succès nouvellement débloqués.
        """
        # Injection du % CardDex pour les lambdas qui en ont besoin
        player.stats._carddex_pct = player.carddex.completion_percentage()

        unlocked = []
        for ach in ACHIEVEMENTS:
            if ach.id in player.stats.achievements:
                continue
            try:
                if ach.condition(player.stats):
                    player.stats.achievements.add(ach.id)
                    player.stats.achievements_unlocked += 1
                    unlocked.append(ach)
            except Exception:
                pass   # Ne jamais crasher à cause d'un succès

        return unlocked