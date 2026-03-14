import time

from card import Rarity, Card

# Durée d'un jour en secondes
DAY_DURATION = 86_400


class DailyReward:
    def __init__(self, coins: int = 0, card: Card | None = None, description: str = ""):
        self.coins       = coins
        self.card        = card
        self.description = description

    def __repr__(self):
        extra = f" + {self.card.rarity.name}" if self.card else ""
        return f"DailyReward({self.coins} pièces{extra})"


# Cartes de récompense daily (card_id=None → sera résolu par la DB)
def _reward_card(rarity: Rarity) -> Card:
    return Card(card_id=None, name="???", rarity=rarity,
                category=None, stat1=0, stat2=0, stat3=0,
                description="", author="", image_path="")


DAILY_REWARDS: list[DailyReward] = [
    DailyReward(coins=100,  description="Jour 1 : 100 pièces"),
    DailyReward(coins=150,  description="Jour 2 : 150 pièces"),
    DailyReward(coins=200,  card=_reward_card(Rarity.COMMUNE),    description="Jour 3 : 200 pièces + 1 carte Commune"),
    DailyReward(coins=250,  card=_reward_card(Rarity.RARE),       description="Jour 4 : 250 pièces + 1 carte Rare"),
    DailyReward(coins=300,  card=_reward_card(Rarity.ÉPIQUE),     description="Jour 5 : 300 pièces + 1 carte Épique"),
    DailyReward(coins=350,  card=_reward_card(Rarity.LÉGENDAIRE), description="Jour 6 : 350 pièces + 1 carte Légendaire"),
    DailyReward(coins=500,  card=_reward_card(Rarity.MYTHIQUE),   description="Jour 7 : 500 pièces + 1 carte Mythique"),
]


class DailyRewardManager:

    def can_claim(self, player) -> bool:
        return time.time() - player.stats.last_daily_timestamp >= DAY_DURATION

    def time_until_next(self, player) -> int:
        """Secondes restantes avant la prochaine revendication (0 si dispo)."""
        remaining = DAY_DURATION - (time.time() - player.stats.last_daily_timestamp)
        return max(0, int(remaining))

    def claim_reward(self, player) -> DailyReward:
        now = time.time()

        if not self.can_claim(player):
            remaining = self.time_until_next(player)
            raise ValueError(f"Récompense déjà réclamée. Reviens dans {remaining} secondes.")

        # ── Gestion du streak ──────────────────────────────────────────────
        # Si plus de 2 jours sans connexion → streak reset
        if player.stats.last_daily_timestamp > 0 and \
                now - player.stats.last_daily_timestamp >= DAY_DURATION * 2:
            if player.stats.daily_current_streak > 0:
                player.stats.daily_streak_breaks += 1
            player.stats.daily_current_streak = 1
        else:
            player.stats.daily_current_streak += 1

        player.stats.daily_best_streak = max(
            player.stats.daily_best_streak,
            player.stats.daily_current_streak
        )
        player.stats.last_daily_timestamp = now
        player.stats.daily_claims_total  += 1

        # ── Sélection de la récompense (cycle de 7 jours) ──────────────────
        reward_index = (player.stats.daily_current_streak - 1) % len(DAILY_REWARDS)
        reward       = DAILY_REWARDS[reward_index]

        # ── Application des pièces ─────────────────────────────────────────
        player.coins               += reward.coins
        player.stats.coins_earned  += reward.coins   # ← correction de la faute "coin_earned"
        player._update_max_coins()   # snapshot après réception des pièces

        # ── Sauvegarde en base ─────────────────────────────────────────────
        stats_to_save = {
            'coins':          player.coins,
            'coins_earned':   player.stats.coins_earned,
            'last_ts':        player.stats.last_daily_timestamp,
            'current_streak': player.stats.daily_current_streak,
            'best_streak':    player.stats.daily_best_streak,
            'streak_breaks':  player.stats.daily_streak_breaks,
            'total_claims':   player.stats.daily_claims_total,
        }

        import database_manager
        database_manager.db_update_daily(player.id, stats_to_save, reward.coins, reward.card)

        # ── Application de la carte ────────────────────────────────────────
        if reward.card:
            player.inventory.add_card(reward.card)
            player.carddex.add_card(reward.card)
            player.stats.cards_obtained += 1
            player.stats.cards_by_rarity[reward.card.rarity]     += 1
            if reward.card.category:
                player.stats.cards_by_category[reward.card.category] += 1

        # ── Vérification des succès ────────────────────────────────────────
        player.check_achievements()

        return reward