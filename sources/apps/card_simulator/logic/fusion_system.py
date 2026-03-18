#Projet : Card Opening Simulator
#Auteurs : Fahreddin, Thyraël, Tristan, Augustin

"""
fusion_system.py
Orchestre une fusion côté métier + persistance DB.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data"))

from card import Rarity
from inventory import FUSION_RULES
import database_manager as db


class FusionSystem:

    def fuse(self, player, rarity: Rarity) -> dict:
        """
        Lance une tentative de fusion pour le joueur.

        Retourne un dict :
            success     : bool
            cost        : int  (0 si fusion impossible)
            result_card : Card | None
            message     : str
        """
        # Validation
        if rarity not in FUSION_RULES:
            return {"success": False, "cost": 0,
                    "result_card": None,
                    "message": f"La rareté {rarity.name} ne peut pas être fusionnée."}

        rule      = FUSION_RULES[rarity]
        available = [c for c in player.inventory.cards if c.rarity == rarity]

        if len(available) < rule["needed"]:
            return {"success": False, "cost": 0,
                    "result_card": None,
                    "message": (f"Pas assez de cartes {rarity.name} "
                                f"(besoin : {rule['needed']}, disponible : {len(available)}).")}

        if player.coins < rule["cost"]:
            return {"success": False, "cost": 0,
                    "result_card": None,
                    "message": (f"Pas assez de pièces "
                                f"(besoin : {rule['cost']}, disponible : {player.coins}).")}

        # Exécution côté inventaire
        cards_used = available[:rule["needed"]]
        success, cost = player.player_fuse_card(rarity)

        # Récupère la carte résultat (si succès, dernière carte ajoutée)
        result_card = None
        if success:
            result_card = player.inventory.cards[-1]

        # Persistance DB
        new_achievements = []
        if player.id is not None:
            fusion_data = {
                "cards_used":  cards_used,
                "result_card": result_card,
                "is_success":  success,
                "cost":        cost,
            }
            db.db_register_fusion(player.id, fusion_data)
            # db_register_fusion gère déjà le débit coins en DB,
            # pas besoin de db_update_coins ici (évite double débit)
            new_achievements = player.check_achievements()
            db.db_sync_achievements(player.id, new_achievements)

        # Message
        if success:
            msg = (f"Fusion réussie ! "
                   f"Tu obtiens une carte {result_card.name} ({result_card.rarity.name}).")
        else:
            msg = (f"Fusion échouée. "
                   f"Tes {rule['needed']} cartes {rarity.name} ont été consommées.")

        return {
            "success":          success,
            "cost":             cost,
            "result_card":      result_card,
            "message":          msg,
            "new_achievements": new_achievements,
        }