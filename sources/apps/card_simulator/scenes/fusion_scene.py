#Projet : Card Opening Simulator
#Auteurs : Fahreddin, Thyraël, Tristan, Augustin

"""
fusion_scene.py
Ecran de fusion
"""

import pygame
import random
import math
from collections import defaultdict
from engine.scene_manager import BaseScene, TransitionType
from engine.ui_components  import (
    Colors, Button, CoinDisplay, ProgressBar, draw_rounded_rect
)
from card import Rarity, RARITY_SELL_VALUE
from inventory import FUSION_RULES


# Constantes

SLOT_W, SLOT_H = 110, 154      # slots de depot
SLOT_GAP       = 18
SLOTS_Y        = 90            # y des slots de depot
GRID_TOP       = 60            # y de la grille
CARD_W, CARD_H = 82, 115       # cartes dans la grille
CARD_GAP       = 8
BOTTOM_H       = 55

RARITY_LABELS = {
    Rarity.COMMUNE:    "Commune",
    Rarity.RARE:       "Rare",
    Rarity.ÉPIQUE:     "Epique",
    Rarity.LÉGENDAIRE: "Legendaire",
    Rarity.MYTHIQUE:   "Mythique",
}

RESULT_LABELS = {
    Rarity.COMMUNE:    "Rare",
    Rarity.RARE:       "Epique",
    Rarity.ÉPIQUE:     "Legendaire",
    Rarity.LÉGENDAIRE: "Mythique",
    Rarity.MYTHIQUE:   "Unique",
}


def _rarity_name(card) -> str:
    return card.rarity.name if hasattr(card.rarity, "name") else str(card.rarity)

def _rarity_color(card) -> tuple:
    return Colors.RARITY.get(_rarity_name(card), Colors.BORDER)

def _rarity_color_r(rarity) -> tuple:
    name = rarity.name if hasattr(rarity, "name") else str(rarity)
    return Colors.RARITY.get(name, Colors.BORDER)


# Particule de feu (animation fusion)

class Particle:
    def __init__(self, x, y):
        self.x    = x + random.uniform(-20, 20)
        self.y    = y + random.uniform(-10, 10)
        self.vx   = random.uniform(-1.5, 1.5)
        self.vy   = random.uniform(-3.0, -0.5)
        self.life = random.uniform(400, 900)   # ms
        self.max_life = self.life
        r = random.randint(200, 255)
        g = random.randint(60, 160)
        self.color = (r, g, 20)
        self.size  = random.uniform(3, 8)
        self.done  = False

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.done = True
            return
        self.x  += self.vx * dt * 0.06
        self.y  += self.vy * dt * 0.06
        self.vy += 0.002 * dt   # gravité légère vers le haut inversée

    def draw(self, surface):
        if self.done:
            return
        alpha = int(255 * (self.life / self.max_life))
        size  = max(1, int(self.size * (self.life / self.max_life)))
        r, g, b = self.color
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (r, g, b, alpha), (size, size), size)
        surface.blit(s, (int(self.x) - size, int(self.y) - size))


# FusionScene

class FusionScene(BaseScene):

    PHASE_SELECT = "select"
    PHASE_FUSING = "fusing"
    PHASE_RESULT = "result"

    def __init__(self, manager):
        super().__init__(manager)

        # Calcul dynamique des colonnes en attributs d'instance
        self._lcw  = int(self.W * 0.28)   # self._lcw
        self._rcx  = self._lcw + 20        # self._rcx (séparateur)
        self._gl   = self._rcx + 8         # self._gl (début cartes)

        self._phase      = self.PHASE_SELECT
        self._slots      = [None, None, None]   # cartes déposées dans les 3 slots
        self._grid_cards = []                   # cartes disponibles dans la grille
        self._scroll_y   = 0
        self._max_scroll = 0

        # Animation
        self._particles:  list[Particle] = []
        self._anim_timer  = 0
        self._flash_alpha = 0
        self._result_dict = None   # retour de FusionSystem.fuse()
        self._result_card_anim = 0.0   # 0→1 apparition de la carte résultat

        self._coin_display = CoinDisplay(
            (self.W - 20, 22), self.font("body", 18), self.assets
        )
        self._btn_back = Button(
            (20, self.H - 106, 130, 44), "< Retour",
            self.font("body", 17), on_click=self._go_back
        )
        self._btn_fuse = Button(
            (self._lcw // 2 - 100, SLOTS_Y + SLOT_H + 170, 200, 46),
            "Fusionner", self.font("title", 18),
            color=Colors.ORANGE, on_click=self._launch_fusion,
            radius=12
        )
        self._btn_retry = Button(
            (self.W // 2 - 210, self.H - 70, 200, 44),
            "Nouvelle fusion", self.font("body", 16),
            color=Colors.BLUE, on_click=self._reset,
            radius=10
        )

        self._build_grid()
        self._compute_slots_rects()

    # Construction

    def _compute_slots_rects(self):
        """Calcule les rects des 3 slots dans la colonne gauche."""
        total_w = 3 * SLOT_W + 2 * SLOT_GAP
        ox      = (self._lcw - total_w) // 2
        self._slot_rects = [
            pygame.Rect(ox + i * (SLOT_W + SLOT_GAP), SLOTS_Y, SLOT_W, SLOT_H)
            for i in range(3)
        ]

    def _build_grid(self):
        """Reconstruit la grille avec les cartes fusionnables de l'inventaire."""
        if not self.player:
            self._grid_cards = []
            return

        # Compter les cartes par (card_id, rarity)
        counts = defaultdict(int)
        cards_by_id = {}
        for card in self.player.inventory.cards:
            if card.rarity in FUSION_RULES:
                counts[card.card_id] += 1
                cards_by_id[card.card_id] = card

        self._grid_cards = [
            {"card": card, "qty": counts[cid], "selected_count": 0}
            for cid, card in cards_by_id.items()
        ]
        # Trier par rareté décroissante puis nom
        self._grid_cards.sort(key=lambda x: (
            -(x["card"].rarity.value if hasattr(x["card"].rarity, "value") else 0),
            x["card"].name.lower()
        ))
        self._layout_grid()

    def _layout_grid(self):
        grid_w = self.W - self._gl - 16
        cols   = max(1, (grid_w + CARD_GAP) // (CARD_W + CARD_GAP))
        for i, item in enumerate(self._grid_cards):
            item["col"] = i % cols
            item["row"] = i // cols
            item["x"]   = (i % cols) * (CARD_W + CARD_GAP)  # offset seul, self._gl ajouté au blit
            item["y"]   = i // cols * (CARD_H + CARD_GAP)

        rows = (len(self._grid_cards) + cols - 1) // cols if self._grid_cards else 1
        content_h    = rows * (CARD_H + CARD_GAP)
        visible_h    = self.H - GRID_TOP - BOTTOM_H
        self._max_scroll = max(0, content_h - visible_h)
        self._scroll_y   = max(0, min(self._scroll_y, self._max_scroll))

    # Navigation

    def _go_back(self):
        from scenes.menu_scene import MenuScene
        self.goto(MenuScene)

    def _reset(self):
        """Revenir à la sélection pour une nouvelle fusion."""
        self._phase      = self.PHASE_SELECT
        self._slots      = [None, None, None]
        self._particles  = []
        self._anim_timer = 0
        self._flash_alpha = 0
        self._result_dict = None
        self._result_card_anim = 0.0
        self._build_grid()

    # Logique des slots

    def _slot_rarity(self) -> Rarity | None:
        """Rareté des cartes actuellement dans les slots (None si slots vides)."""
        cards = [s for s in self._slots if s is not None]
        if not cards:
            return None
        return cards[0].rarity

    def _slots_full(self) -> bool:
        return all(s is not None for s in self._slots)

    def _slots_valid(self) -> bool:
        """Tous les slots pleins ET toutes les cartes de même rareté fusionnable."""
        if not self._slots_full():
            return False
        r = self._slots[0].rarity
        return (all(s.rarity == r for s in self._slots)
                and r in FUSION_RULES)

    def _add_to_slot(self, card):
        """Place une carte dans le premier slot libre."""
        for i in range(3):
            if self._slots[i] is None:
                self._slots[i] = card
                # Marquer la carte comme utilisée dans la grille
                for item in self._grid_cards:
                    if item["card"].card_id == card.card_id:
                        item["selected_count"] += 1
                        break
                return True
        return False

    def _remove_from_slot(self, slot_idx: int):
        """Retire la carte d'un slot et la remet disponible."""
        card = self._slots[slot_idx]
        if card is None:
            return
        self._slots[slot_idx] = None
        for item in self._grid_cards:
            if item["card"].card_id == card.card_id:
                item["selected_count"] = max(0, item["selected_count"] - 1)
                break

    def _can_add_card(self, card) -> bool:
        """Vérifie qu'on peut ajouter cette carte (même rareté que les slots existants)."""
        existing_rarity = self._slot_rarity()
        if existing_rarity is not None and card.rarity != existing_rarity:
            return False
        if card.rarity not in FUSION_RULES:
            return False
        # Vérifier qu'on ne dépasse pas la quantité disponible
        for item in self._grid_cards:
            if item["card"].card_id == card.card_id:
                used = item["selected_count"]
                return used < item["qty"]
        return False

    def _available_in_grid(self, item) -> int:
        """Nombre d'exemplaires encore disponibles (non dans les slots)."""
        return item["qty"] - item["selected_count"]

    # Fusion

    def _launch_fusion(self):
        if not self._slots_valid():
            return
        self._phase      = self.PHASE_FUSING
        self._anim_timer = 0
        self._particles  = []
        self.assets.play("sfx_fusion_start", 0.8)

    def _do_fusion(self):
        """Exécute la fusion via FusionSystem."""
        from fusion_system import FusionSystem
        rarity = self._slots[0].rarity
        system = FusionSystem()
        result = self._do_fusion_with_specific_cards()
        self._result_dict = result
        self._phase = self.PHASE_RESULT
        self._result_card_anim = 0.0

    def _do_fusion_with_specific_cards(self) -> dict:
        """
        Effectue la fusion avec les 3 cartes sélectionnées dans les slots.
        Contourne FusionSystem pour utiliser exactement ces cartes.
        """
        import database_manager as db_mod
        from card_repository import CardRepository
        import random as rd

        rarity = self._slots[0].rarity
        rule   = FUSION_RULES[rarity]
        cost   = rule["cost"]
        cards_used = list(self._slots)

        if not self.player.can_buy(cost):
            return {"success": False, "cost": 0, "result_card": None,
                    "new_achievements": [],
                    "message": "Pas assez de pieces !"}

        # Débiter les pièces
        self.player.coins -= cost
        self.player.stats.coins_spent += cost
        self.player.stats.fusions_attempted += 1

        # Retirer les cartes de l'inventaire
        for card in cards_used:
            if card in self.player.inventory.cards:
                self.player.inventory.cards.remove(card)

        # Résoudre le succès
        success = rd.random() < rule["success"]
        result_card = None

        if success:
            self.player.stats.fusions_success += 1
            repo = CardRepository()
            result_card = repo.get_random_card(rule["result"])
            self.player.inventory.add_card(result_card)
            self.player.carddex.add_card(result_card)
            self.player.stats.cards_obtained += 1
            self.player.stats.cards_by_rarity[result_card.rarity] += 1
        else:
            self.player.stats.fusions_failed += 1

        # Persistance DB
        if self.player.id is not None:
            fusion_data = {
                "cards_used":  cards_used,
                "result_card": result_card,
                "is_success":  success,
                "cost":        cost,
            }
            db_mod.db_register_fusion(self.player.id, fusion_data)
            db_mod.db_update_max_coins(self.player.id, self.player.stats.max_coins_held)

        new_ach = self.player.check_achievements()
        if self.player.id is not None:
            db_mod.db_sync_achievements(self.player.id, new_ach)
        for a in new_ach:
            self.manager.show_achievement(a)

        msg = (f"Fusion reussie ! Tu obtiens une carte {RESULT_LABELS.get(rarity, '???')}."
               if success else
               f"Fusion echouee. Tes 3 cartes ont ete consommees.")

        # Sons de résultat
        if success:
            self.assets.play("sfx_fusion_success", 1.0)
        else:
            self.assets.play("sfx_fusion_fail", 0.9)

        return {
            "success":          success,
            "cost":             cost,
            "result_card":      result_card,
            "new_achievements": new_ach,
            "message":          msg,
        }

    # Boucle

    def handle_events(self, events):
        for e in events:
            if self._phase == self.PHASE_SELECT:
                self._btn_back.handle_event(e)
                self._btn_fuse.handle_event(e)
                self._handle_select_events(e)
            elif self._phase == self.PHASE_RESULT:
                self._btn_retry.handle_event(e)
                self._btn_back.handle_event(e)

    def _handle_select_events(self, e):
        if e.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if GRID_TOP <= my <= self.H - BOTTOM_H and mx >= self._rcx - 12:
                self._scroll_y = max(0, min(
                    self._scroll_y - e.y * 35, self._max_scroll
                ))

        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            mx, my = e.pos

            # Clic sur un slot de depot → retirer la carte
            for i, rect in enumerate(self._slot_rects):
                if rect.collidepoint(mx, my) and self._slots[i] is not None:
                    self._remove_from_slot(i)
                    return

            # Clic sur une carte de la grille
            if GRID_TOP <= my <= self.H - BOTTOM_H and mx >= self._rcx - 12:
                for item in self._grid_cards:
                    cx = self._gl + item["x"]
                    cy = GRID_TOP  + item["y"] - self._scroll_y
                    if (cx <= mx <= cx + CARD_W and cy <= my <= cy + CARD_H):
                        card = item["card"]
                        if self._available_in_grid(item) > 0 and self._can_add_card(card):
                            self._add_to_slot(card)
                        elif not self._can_add_card(card) and self._slot_rarity() is not None:
                            self.manager.show_toast(
                                "Rareté différente de celles dans les slots", Colors.RED
                            )
                        break

    def update(self, dt: int):
        if self._phase == self.PHASE_FUSING:
            self._update_fusing(dt)
        elif self._phase == self.PHASE_RESULT:
            self._result_card_anim = min(1.0, self._result_card_anim + dt / 600)

    def _update_fusing(self, dt: int):
        self._anim_timer += dt

        # Générer des particules en continu
        if self._anim_timer < 1800:
            cx = self.W // 2
            cy = SLOTS_Y + SLOT_H // 2 + 20
            for _ in range(int(dt / 16)):   # ~1 particule par frame
                self._particles.append(Particle(cx, cy))

        # Flash au milieu
        if 800 < self._anim_timer < 1200:
            self._flash_alpha = min(180,
                int(180 * (1 - abs(self._anim_timer - 1000) / 200)))
        else:
            self._flash_alpha = max(0, self._flash_alpha - dt * 0.8)

        # Mettre à jour les particules
        for p in self._particles:
            p.update(dt)
        self._particles = [p for p in self._particles if not p.done]

        # Lancer la vraie fusion à mi-animation
        if self._anim_timer >= 1000 and self._result_dict is None:
            self._do_fusion()

        # Fin de l'animation → phase résultat
        if self._anim_timer >= 2000 and self._result_dict is not None:
            self._phase = self.PHASE_RESULT
            self._result_card_anim = 0.0

    # Draw

    def draw(self):
        self.screen.fill(Colors.BG_DARK)

        if self._phase == self.PHASE_SELECT:
            self._draw_select()
        elif self._phase == self.PHASE_FUSING:
            self._draw_fusing()
        elif self._phase == self.PHASE_RESULT:
            self._draw_result()

        self._coin_display.draw(self.screen,
                                self.player.coins if self.player else 0)

    # Draw SELECT

    def _draw_select(self):
        # Titre colonne gauche
        f_title = self.font("title", 24)
        t = f_title.render("Fusion", True, Colors.TEXT_WHITE)
        self.screen.blit(t, t.get_rect(centerx=self._lcw // 2, y=18))

        # Séparateur vertical
        import pygame as _pg
        _pg.draw.line(self.screen, Colors.BORDER,
                      (self._rcx - 12, 10), (self._rcx - 12, self.H - BOTTOM_H), 1)

        # Titre colonne droite
        f2 = self.font("body", 13)
        t2 = f2.render("Cartes disponibles", True, Colors.TEXT_GRAY)
        self.screen.blit(t2, (self._rcx, 18))

        self._draw_slots()
        self._draw_fusion_info()
        self._draw_inventory_grid()
        self._draw_bottom_bar()
        self._btn_back.draw(self.screen)

    def _draw_slots(self):
        f_label = self.font("body", 13)
        f_hint  = self.font("body", 11)

        for i, rect in enumerate(self._slot_rects):
            card = self._slots[i]

            if card:
                rc = _rarity_color(card)
                draw_rounded_rect(self.screen, Colors.BG_PANEL, rect, 10,
                                  border_color=rc, border_width=2)
                img = self.assets.card_image(card.image_path, (SLOT_W - 8, SLOT_H - 40))
                self.screen.blit(img, (rect.x + 4, rect.y + 4))
                # Nom tronqué
                name = card.name[:14] + "..." if len(card.name) > 14 else card.name
                nt   = f_label.render(name, True, rc)
                self.screen.blit(nt, nt.get_rect(
                    centerx=rect.centerx, y=rect.bottom - 32))
                # Hint retirer
                ht = f_hint.render("Clic pour retirer", True, Colors.TEXT_MUTED)
                self.screen.blit(ht, ht.get_rect(
                    centerx=rect.centerx, y=rect.bottom - 16))
            else:
                draw_rounded_rect(self.screen, Colors.BG_PANEL2, rect, 10,
                                  border_color=Colors.BORDER, border_width=1,
                                  alpha=160)
                # Croix centrale
                cx, cy = rect.center
                pygame.draw.line(self.screen, Colors.BORDER,
                                 (cx - 15, cy), (cx + 15, cy), 2)
                pygame.draw.line(self.screen, Colors.BORDER,
                                 (cx, cy - 15), (cx, cy + 15), 2)
                ht = f_hint.render(f"Slot {i+1}", True, Colors.TEXT_MUTED)
                self.screen.blit(ht, ht.get_rect(centerx=rect.centerx, y=rect.bottom - 16))

        # Flèches entre les slots
        f_arrow = self.font("body", 20)
        for i in range(2):
            ax = self._slot_rects[i].right + SLOT_GAP // 2
            ay = SLOTS_Y + SLOT_H // 2
            pygame.draw.polygon(self.screen, Colors.BORDER,
                                [(ax - 8, ay - 8), (ax + 8, ay), (ax - 8, ay + 8)])

    def _draw_fusion_info(self):
        """Panneau d'infos : rareté, taux, coût, résultat attendu."""
        rarity = self._slot_rarity()
        f = self.font("body", 15)
        fy = self.font("body", 13)

        # Infos dans la colonne gauche, sous les slots
        info_y  = SLOTS_Y + SLOT_H + 16
        col_cx  = self._lcw // 2   # centre colonne gauche
        panel_w = self._lcw - 20
        panel_x = 10

        if rarity and rarity in FUSION_RULES:
            rule = FUSION_RULES[rarity]
            rc   = _rarity_color_r(rarity)
            rl   = RARITY_LABELS.get(rarity, rarity.name)
            res  = RESULT_LABELS.get(rarity, "???")
            rate = int(rule["success"] * 100)
            cost = rule["cost"]

            # Panel fond
            draw_rounded_rect(self.screen, Colors.BG_PANEL,
                              (panel_x, info_y, panel_w, 130), 10,
                              border_color=rc, border_width=1, alpha=200)

            line_y = info_y + 14
            gap    = 24

            t1 = f.render(f"Rareté : {rl}", True, rc)
            self.screen.blit(t1, t1.get_rect(centerx=col_cx, y=line_y))

            color_rate = (Colors.GREEN if rate >= 50
                          else Colors.ORANGE if rate >= 20 else Colors.RED)
            t2 = f.render(f"Taux de reussite : {rate}%", True, color_rate)
            self.screen.blit(t2, t2.get_rect(centerx=col_cx, y=line_y + gap))

            t3 = f.render(f"Cout : {cost} pièces", True, Colors.GOLD)
            self.screen.blit(t3, t3.get_rect(centerx=col_cx, y=line_y + gap * 2))

            t4 = fy.render(f"Resultat possible : {res}", True, Colors.TEXT_GRAY)
            self.screen.blit(t4, t4.get_rect(centerx=col_cx, y=line_y + gap * 3))

            # Barre taux
            bar_w = panel_w - 40
            bar_x = panel_x + 20
            bar_y = info_y + 110
            pygame.draw.rect(self.screen, Colors.BG_PANEL2,
                             (bar_x, bar_y, bar_w, 8), border_radius=4)
            fill = int(bar_w * rule["success"])
            if fill > 0:
                pygame.draw.rect(self.screen, color_rate,
                                 (bar_x, bar_y, fill, 8), border_radius=4)

        elif not self._slots_full():
            hint_f = self.font("body", 13)
            hint   = hint_f.render("Selectionnez 3 cartes de", True, Colors.TEXT_MUTED)
            hint2  = hint_f.render("meme rarete depuis la grille", True, Colors.TEXT_MUTED)
            self.screen.blit(hint,  hint.get_rect( centerx=col_cx, y=info_y + 20))
            self.screen.blit(hint2, hint2.get_rect(centerx=col_cx, y=info_y + 40))

        # Bouton fusionner
        self._btn_fuse.disabled = not self._slots_valid()
        self._btn_fuse.color    = Colors.ORANGE if self._slots_valid() else Colors.BG_PANEL2
        self._btn_fuse.draw(self.screen)

    def _draw_inventory_grid(self):
        """Grille des cartes fusionnables en bas."""
        # Titre affiché dans _draw_select, pas ici

        clip = pygame.Rect(self._rcx - 12, GRID_TOP,
                           self.W - self._rcx + 12, self.H - GRID_TOP - BOTTOM_H)
        self.screen.set_clip(clip)

        for item in self._grid_cards:
            x = self._gl + item["x"]
            y = GRID_TOP  + item["y"] - self._scroll_y

            if y + CARD_H < GRID_TOP or y > self.H - BOTTOM_H:
                continue

            card  = item["card"]
            avail = self._available_in_grid(item)
            rc    = _rarity_color(card)

            # Grisé si non disponible ou mauvaise rareté
            slot_r  = self._slot_rarity()
            can_add = avail > 0 and (slot_r is None or card.rarity == slot_r)
            alpha   = 255 if can_add else 80

            img = self.assets.card_image(card.image_path, (CARD_W, CARD_H))
            if alpha < 255:
                img = img.copy()
                img.set_alpha(alpha)
            self.screen.blit(img, (x, y))

            border_color = rc if can_add else Colors.BORDER
            pygame.draw.rect(self.screen, border_color,
                             (x, y, CARD_W, CARD_H), 2, border_radius=5)

            # Badge quantité disponible
            if item["qty"] > 1:
                qty_f   = pygame.font.SysFont("freesansbold", 11)
                qty_lbl = f"x{avail}/{item['qty']}"
                qs      = qty_f.render(qty_lbl, True, (255, 255, 255))
                qw      = qs.get_width() + 6
                pygame.draw.rect(self.screen, (40, 40, 60),
                                 (x + CARD_W - qw - 2, y + CARD_H - 16, qw, 14),
                                 border_radius=4)
                self.screen.blit(qs, (x + CARD_W - qw, y + CARD_H - 15))

        self.screen.set_clip(None)

        # Scrollbar à droite de la colonne droite
        if self._max_scroll > 0:
            visible_h = self.H - GRID_TOP - BOTTOM_H
            ratio  = visible_h / (visible_h + self._max_scroll)
            bar_h  = max(20, int(visible_h * ratio))
            bar_y  = GRID_TOP + int(
                (self._scroll_y / self._max_scroll) * (visible_h - bar_h)
            )
            pygame.draw.rect(self.screen, Colors.BORDER_H,
                             (self.W - 7, bar_y, 4, bar_h), border_radius=2)

        # Message si vide
        if not self._grid_cards:
            f = self.font("body", 16)
            t = f.render("Aucune carte fusionnable dans l'inventaire.",
                         True, Colors.TEXT_MUTED)
            self.screen.blit(t, t.get_rect(center=(self.W // 2, GRID_TOP + 60)))

    def _draw_bottom_bar(self):
        bar_rect = (0, self.H - BOTTOM_H, self.W, BOTTOM_H)
        draw_rounded_rect(self.screen, Colors.BG_PANEL, bar_rect, 0,
                          border_color=Colors.BORDER, border_width=1, alpha=220)

    # Draw FUSING

    def _draw_fusing(self):
        # Fond sombre
        self.screen.fill((8, 8, 20))

        # Les 3 cartes qui "brûlent"
        cx = self.W // 2
        for i, card in enumerate(self._slots):
            if card is None:
                continue
            x = cx - 180 + i * 160
            y = self.H // 2 - 80
            img = self.assets.card_image(card.image_path, (110, 154))
            # Tremblement
            shake_x = random.randint(-3, 3)
            shake_y = random.randint(-2, 2)
            self.screen.blit(img, (x + shake_x, y + shake_y))

        # Particules
        for p in self._particles:
            p.draw(self.screen)

        # Flash
        if self._flash_alpha > 0:
            flash = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            flash.fill((255, 180, 50, int(self._flash_alpha)))
            self.screen.blit(flash, (0, 0))

        # Texte
        f = self.font("title", 26)
        t = f.render("Fusion en cours...", True, Colors.GOLD)
        self.screen.blit(t, t.get_rect(center=(self.W // 2, self.H // 2 + 120)))

    # Draw RESULT

    def _draw_result(self):
        if self._result_dict is None:
            return

        success     = self._result_dict["success"]
        result_card = self._result_dict["result_card"]
        t_anim      = self._result_card_anim   # 0→1

        if success and result_card:
            self._draw_success(result_card, t_anim)
        else:
            self._draw_failure(t_anim)

        # Boutons
        self._btn_retry.draw(self.screen)
        self._btn_back.draw(self.screen)

    def _draw_success(self, card, t: float):
        """Affiche la carte résultat avec apparition animée."""
        rc = _rarity_color(card)

        # Glow de fond
        glow_r = int(200 * t)
        if glow_r > 0:
            glow = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            r, g, b = rc
            glow.fill((r, g, b, int(30 * t)))
            self.screen.blit(glow, (0, 0))

        # Titre
        f_title = self.font("title", 30)
        t1 = f_title.render("Fusion reussie !", True, Colors.GREEN)
        self.screen.blit(t1, t1.get_rect(centerx=self.W // 2, y=60))

        # Carte (scale 0→1 + légère translation)
        scale = min(1.0, t * 1.2)
        cw    = int(180 * scale)
        ch    = int(252 * scale)
        if cw > 0 and ch > 0:
            img = self.assets.card_image(card.image_path, (180, 252))
            scaled = pygame.transform.smoothscale(img, (cw, ch))
            cx = self.W // 2 - cw // 2
            cy = self.H // 2 - ch // 2 - 30
            self.screen.blit(scaled, (cx, cy))
            # Bordure
            pygame.draw.rect(self.screen, rc, (cx, cy, cw, ch), 2, border_radius=8)

        # Infos carte
        if t > 0.7:
            f_name = self.font("title", 20)
            f_info = self.font("body", 15)
            alpha  = int(255 * min(1.0, (t - 0.7) / 0.3))

            name_s = f_name.render(card.name, True, Colors.TEXT_WHITE)
            name_s.set_alpha(alpha)
            self.screen.blit(name_s, name_s.get_rect(
                centerx=self.W // 2, y=self.H // 2 + 148))

            rl   = RARITY_LABELS.get(card.rarity, _rarity_name(card))
            rar_s = f_info.render(rl, True, rc)
            rar_s.set_alpha(alpha)
            self.screen.blit(rar_s, rar_s.get_rect(
                centerx=self.W // 2, y=self.H // 2 + 174))

    def _draw_failure(self, t: float):
        """Affiche le résultat d'échec avec fumée."""
        self.screen.fill((10, 8, 8))

        # Particules de fumée (gris)
        if t < 0.8:
            cx = self.W // 2
            cy = self.H // 2
            for _ in range(2):
                p = Particle(cx, cy)
                p.color  = (80, 80, 90)
                p.size   = random.uniform(6, 14)
                p.vy     = random.uniform(-2, -0.5)
                p.life   = random.uniform(600, 1200)
                p.max_life = p.life
                self._particles.append(p)
        for p in self._particles:
            p.update(16)
        self._particles = [p for p in self._particles if not p.done]
        for p in self._particles:
            p.draw(self.screen)

        if t > 0.3:
            alpha  = int(255 * min(1.0, (t - 0.3) / 0.4))
            f_fail = self.font("title", 34)
            t1 = f_fail.render("Fusion echouee", True, Colors.RED)
            t1.set_alpha(alpha)
            self.screen.blit(t1, t1.get_rect(center=(self.W // 2, self.H // 2 - 20)))

            f_sub = self.font("body", 16)
            t2 = f_sub.render("Les 3 cartes ont ete consommees.",
                               True, Colors.TEXT_GRAY)
            t2.set_alpha(alpha)
            self.screen.blit(t2, t2.get_rect(center=(self.W // 2, self.H // 2 + 30)))