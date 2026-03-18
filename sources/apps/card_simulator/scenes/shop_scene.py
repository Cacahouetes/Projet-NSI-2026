#Projet : Card Opening Simulator
#Auteurs : Fahreddin, Thyraël, Tristan, Augustin

"""
shop_scene.py
Scène du Shop.
"""

import pygame
import time
from engine.scene_manager import BaseScene, TransitionType
from engine.ui_components  import (
    Colors, Button, Panel, CoinDisplay, draw_rounded_rect
)
from card import RARITY_SELL_VALUE



# Objet local simple card+prix — indépendant de shop_system.ShopCard
class _DBShopCard:
    """Représente une carte de shop reconstruite depuis la DB."""
    def __init__(self, card, price: int):
        self.card  = card
        self.price = price

# Constantes layout
SLOT_W      = 300
SLOT_H      = 420
SLOT_GAP    = 40
SLOT_Y      = 160       # y du haut des slots

RARITY_LABELS = {
    "COMMUNE":    "Commune",
    "RARE":       "Rare",
    "EPIQUE":     "Epique",
    "ÉPIQUE":     "Epique",
    "LEGENDAIRE": "Legendaire",
    "LÉGENDAIRE": "Legendaire",
    "MYTHIQUE":   "Mythique",
    "UNIQUE":     "Unique",
    "DIVINE":     "Divine",
}


def _rarity_label(card) -> str:
    raw = card.rarity.name if hasattr(card.rarity, "name") else str(card.rarity)
    return RARITY_LABELS.get(raw.upper(), raw)

def _rarity_color(card) -> tuple:
    name = card.rarity.name if hasattr(card.rarity, "name") else str(card.rarity)
    return Colors.RARITY.get(name, Colors.BORDER)

def _fmt_time(seconds: int) -> str:
    """Formate un nombre de secondes en HH:MM:SS."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m:02d}m {s:02d}s"


# ShopSlotWidget — un slot visuel du shop

class ShopSlotWidget:
    """
    Affiche une carte de shop :
      - Image de la carte
      - Nom + rareté + prix
      - Overlay "VENDU" si sold=True
      - Hover animé
    """

    def __init__(self, shop_card, slot_index: int, rect: pygame.Rect, assets):
        self.shop_card   = shop_card   # objet ShopCard (card + price), ou None
        self.slot_index  = slot_index
        self.rect        = rect
        self.assets      = assets
        self.sold        = (shop_card is None)
        self._hover_t    = 0.0

    def update(self, dt: int, mouse_pos):
        if self.sold:
            self._hover_t = max(0.0, self._hover_t - dt / 100)
            return
        hovered = self.rect.collidepoint(mouse_pos)
        target  = 1.0 if hovered else 0.0
        spd     = dt / 120
        self._hover_t = (min(1.0, self._hover_t + spd)
                         if hovered else max(0.0, self._hover_t - spd))

    def hit_test(self, pos) -> bool:
        return not self.sold and self.rect.collidepoint(pos)

    def draw(self, surface: pygame.Surface, font_name, font_price, font_rarity):
        rect = self.rect
        ht   = self._hover_t

        # Élévation hover
        lift    = int(ht * 8)
        draw_y  = rect.y - lift
        draw_r  = pygame.Rect(rect.x, draw_y, rect.w, rect.h)

        # Fond du slot
        bg_color = Colors.BG_PANEL if not self.sold else (18, 20, 32)
        bc       = _rarity_color(self.shop_card.card) if (self.shop_card and not self.sold) else Colors.BORDER
        draw_rounded_rect(surface, bg_color, draw_r, 14,
                          border_color=bc if ht > 0.1 else Colors.BORDER,
                          border_width=2 if ht > 0.1 else 1,
                          alpha=220 if not self.sold else 120)

        if self.sold or self.shop_card is None:
            self._draw_sold_overlay(surface, draw_r)
            return

        card = self.shop_card.card

        # Illustration
        img_w  = rect.w - 24
        img_h  = int(img_w * 420 / 300)   # ratio carte
        img_h  = min(img_h, rect.h - 110)
        img    = self.assets.card_image(card.image_path, (img_w, img_h))
        img_x  = rect.x + (rect.w - img_w) // 2
        img_y  = draw_y + 12
        surface.blit(img, (img_x, img_y))

        # Bordure colorée sur l'image
        pygame.draw.rect(surface, bc,
                         (img_x, img_y, img_w, img_h), 2, border_radius=8)

        # Nom
        text_y = img_y + img_h + 10
        name   = card.name if len(card.name) <= 22 else card.name[:20] + "..."
        nt     = font_name.render(name, True, Colors.TEXT_WHITE)
        surface.blit(nt, nt.get_rect(centerx=rect.centerx, y=text_y))

        # Rareté
        rl  = _rarity_label(card)
        rt  = font_rarity.render(rl, True, bc)
        surface.blit(rt, rt.get_rect(centerx=rect.centerx, y=text_y + 22))

        # Prix
        price_str = f"{self.shop_card.price} pièces"
        pt        = font_price.render(price_str, True, Colors.GOLD)
        surface.blit(pt, pt.get_rect(centerx=rect.centerx,
                                      y=draw_r.bottom - 36))

        # Glow hover
        if ht > 0.05:
            glow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*bc, int(30 * ht)),
                             (0, 0, rect.w, rect.h), border_radius=14)
            surface.blit(glow, (rect.x, draw_y))

    def _draw_sold_overlay(self, surface: pygame.Surface, draw_r: pygame.Rect):
        """Overlay grisé avec texte VENDU en diagonale."""
        overlay = pygame.Surface((draw_r.w, draw_r.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, draw_r.topleft)

        font = pygame.font.SysFont("freesansbold", 32)
        txt  = font.render("VENDU", True, (120, 120, 130, 200))
        # Rotation 30 degrés
        txt_rot = pygame.transform.rotate(txt, 30)
        cx = draw_r.centerx - txt_rot.get_width() // 2
        cy = draw_r.centery - txt_rot.get_height() // 2
        surface.blit(txt_rot, (cx, cy))


# ConfirmPopup — popup de confirmation d'achat

class ConfirmPopup:
    """Popup modal de confirmation avant achat."""

    W = 440
    H = 240

    def __init__(self, shop_card, screen_size: tuple,
                 font_title, font_body, assets,
                 on_confirm, on_cancel):
        sw, sh          = screen_size
        self.rect       = pygame.Rect(
            (sw - self.W) // 2, (sh - self.H) // 2, self.W, self.H
        )
        self._sc        = shop_card
        self._ft        = font_title
        self._fb        = font_body
        self._assets    = assets
        self._confirm   = on_confirm
        self._cancel    = on_cancel

        bw, bh = 160, 44
        by     = self.rect.bottom - bh - 20
        self._btn_yes = Button(
            (self.rect.centerx - bw - 12, by, bw, bh),
            "Acheter", font_body,
            color=Colors.GREEN, on_click=on_confirm
        )
        self._btn_no = Button(
            (self.rect.centerx + 12, by, bw, bh),
            "Annuler", font_body,
            color=Colors.RED, on_click=on_cancel
        )

    def handle_event(self, e):
        self._btn_yes.handle_event(e)
        self._btn_no.handle_event(e)
        # Clic en dehors = annuler
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if not self.rect.collidepoint(e.pos):
                self._cancel()

    def draw(self, surface: pygame.Surface):
        # Dim
        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 160))
        surface.blit(dim, (0, 0))

        # Panel
        draw_rounded_rect(surface, Colors.BG_PANEL, self.rect, 14,
                          border_color=Colors.BORDER_H, border_width=2)

        card = self._sc.card
        rc   = _rarity_color(card)

        # Titre
        t1 = self._ft.render("Confirmer l'achat ?", True, Colors.TEXT_WHITE)
        surface.blit(t1, t1.get_rect(centerx=self.rect.centerx,
                                      y=self.rect.y + 20))

        # Nom + rareté
        name = card.name if len(card.name) <= 28 else card.name[:26] + "..."
        t2   = self._fb.render(name, True, Colors.TEXT_WHITE)
        surface.blit(t2, t2.get_rect(centerx=self.rect.centerx,
                                      y=self.rect.y + 62))

        rl  = _rarity_label(card)
        t3  = self._fb.render(rl, True, rc)
        surface.blit(t3, t3.get_rect(centerx=self.rect.centerx,
                                      y=self.rect.y + 88))

        # Prix
        t4 = self._fb.render(f"Prix : {self._sc.price} pièces", True, Colors.GOLD)
        surface.blit(t4, t4.get_rect(centerx=self.rect.centerx,
                                      y=self.rect.y + 118))

        self._btn_yes.draw(surface)
        self._btn_no.draw(surface)


# ShopScene

class ShopScene(BaseScene):

    def __init__(self, manager):
        super().__init__(manager)

        self._shop         = None   # objet Shop chargé
        self._slot_widgets: list[ShopSlotWidget] = []
        self._popup        = None   # ConfirmPopup actif
        self._popup_slot_idx = -1

        self._coin_display = CoinDisplay(
            (self.W - 20, 22), self.font("body", 18), self.assets
        )
        self._btn_back = Button(
            (30, 30, 130, 44), "< Retour",
            self.font("body", 17),
            on_click=self._go_back
        )

        self._load_shop()
        self._build_slot_widgets()

    # Chargement

    def _load_shop(self):
        """Charge ou génère le shop depuis la DB."""
        from shop_system import Shop
        self._shop = Shop(player_id=self.player.id if self.player else None)

    def _build_slot_widgets(self):
        """Construit les 3 widgets de slots depuis le shop."""
        self._slot_widgets = []

        # Calcul des positions : 3 slots centrés
        total_w = 3 * SLOT_W + 2 * SLOT_GAP
        start_x = (self.W - total_w) // 2

        # Construire un mapping slot_index → ShopCard (sold ou dispo)
        # Le shop charge les slots depuis la DB (sold=0 uniquement dans shop_cards)
        # On reconstruit les 3 slots en tenant compte des sold
        import database_manager as db
        all_rows = db.db_load_shop()

        now = int(time.time())

        # Si aucune ligne → shop vide (pas encore initialisé)
        # Si des lignes → les parcourir dans l'ordre slot 0,1,2
        slot_map = {}   # shop_slot → row
        for row in all_rows:
            slot_map[row["shop_slot"]] = row

        for i in range(3):
            x    = start_x + i * (SLOT_W + SLOT_GAP)
            rect = pygame.Rect(x, SLOT_Y, SLOT_W, SLOT_H)
            row  = slot_map.get(i)

            if row is None:
                # Slot inexistant (shop vide ou pas encore généré)
                widget = ShopSlotWidget(None, i, rect, self.assets)
                widget.sold = True
            elif row["sold"] == 1:
                # Slot vendu
                widget = ShopSlotWidget(None, i, rect, self.assets)
                widget.sold = True
            else:
                # Reconstruire un objet carte+prix depuis la DB
                shop_card = None
                from card_repository import CardRepository
                repo = CardRepository()
                card = repo.get_card_by_id(row["card_id"])
                if card:
                    shop_card = _DBShopCard(card, row["price"])
                widget = ShopSlotWidget(shop_card, i, rect, self.assets)
                widget.sold = (shop_card is None)

            self._slot_widgets.append(widget)

        # Mémoriser available_until pour le timer
        self._available_until = 0
        if all_rows:
            self._available_until = all_rows[0].get("available_until", 0)

    # Navigation

    def _go_back(self):
        from scenes.menu_scene import MenuScene
        self.goto(MenuScene)

    # Achat

    def _on_slot_click(self, slot_idx: int):
        """Clic sur un slot disponible → ouvrir le popup de confirmation."""
        widget = self._slot_widgets[slot_idx]
        if widget.sold or widget.shop_card is None:
            return
        if not self.player:
            return
        if self.player.coins < widget.shop_card.price:
            self.manager.show_toast("Pas assez de pieces !", Colors.RED)
            return

        self._popup_slot_idx = slot_idx
        self._popup = ConfirmPopup(
            widget.shop_card,
            (self.W, self.H),
            self.font("title", 20),
            self.font("body", 16),
            self.assets,
            on_confirm=self._confirm_purchase,
            on_cancel=self._cancel_purchase
        )

    def _confirm_purchase(self):
        """
        Achat confirme.
        On n'utilise PAS self._shop.buy_card(idx) car idx est la position
        visuelle du slot (0,1,2) et non l'index dans shop_cards qui retrecit
        apres chaque achat → IndexError.
        On effectue la transaction directement avec la carte du widget.
        """
        import database_manager as db

        idx    = self._popup_slot_idx
        widget = self._slot_widgets[idx]
        sc     = widget.shop_card

        if sc is None or not self.player:
            self._popup = None
            return

        card  = sc.card
        price = sc.price

        if not self.player.can_buy(price):
            self.manager.show_toast("Pas assez de pieces !", Colors.RED)
            self._popup          = None
            self._popup_slot_idx = -1
            return

        try:
            # Débit joueur (côté mémoire)
            self.player.coins                   -= price
            self.player.stats.coins_spent       += price
            self.player.stats.coins_spent_shop  += price
            self.player.stats.shop_cards_bought += 1
            self.player.inventory.add_card(card)
            self.player.carddex.add_card(card)
            self.player.stats.cards_obtained        += 1
            self.player.stats.cards_by_rarity[card.rarity] += 1
            self.player._update_max_coins()

            # Persistance DB
            db.db_register_shop_purchase(self.player.id, card, price, self.player.coins)
            db.db_remove_shop_slot(self.player.id, idx)   # marque sold=1 via shop_slot=idx
            db.db_update_max_coins(self.player.id, self.player.stats.max_coins_held)

            new_ach = self.player.check_achievements()
            db.db_sync_achievements(self.player.id, new_ach)
            for a in new_ach:
                self.manager.show_achievement(a)

            self.assets.play("sfx_buy")
            self.manager.show_toast(
                f"Achat : {card.name} pour {price} pièces", Colors.GREEN
            )
            # Marquer le slot comme vendu visuellement
            widget.sold      = True
            widget.shop_card = None

        except Exception as e:
            self.manager.show_toast(f"Erreur : {e}", Colors.RED)
            print(f"[ShopScene] Erreur achat : {e}")

        self._popup          = None
        self._popup_slot_idx = -1

    def _cancel_purchase(self):
        self._popup          = None
        self._popup_slot_idx = -1

    # Boucle

    def handle_events(self, events):
        for e in events:
            if self._popup:
                self._popup.handle_event(e)
                return   # bloquer tout le reste pendant le popup

            self._btn_back.handle_event(e)

            if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                for widget in self._slot_widgets:
                    if widget.hit_test(e.pos):
                        self._on_slot_click(widget.slot_index)
                        break

    def update(self, dt: int):
        mouse_pos = pygame.mouse.get_pos()
        for widget in self._slot_widgets:
            widget.update(dt, mouse_pos)

    def on_enter(self):
        self._load_shop()
        self._build_slot_widgets()

    # Draw

    def draw(self):
        self.screen.fill(Colors.BG_DARK)
        self._draw_header()
        self._draw_slots()
        self._draw_timer()
        self._btn_back.draw(self.screen)
        self._coin_display.draw(self.screen,
                                self.player.coins if self.player else 0)
        if self._popup:
            self._popup.draw(self.screen)

    def _draw_header(self):
        f = self.font("title", 32)
        t = f.render("Shop", True, Colors.TEXT_WHITE)
        self.screen.blit(t, t.get_rect(centerx=self.W // 2, y=18))

        f2  = self.font("body", 14)
        sub = f2.render("3 nouvelles cartes disponibles a chaque restock",
                        True, Colors.TEXT_GRAY)
        self.screen.blit(sub, sub.get_rect(centerx=self.W // 2, y=58))

    def _draw_slots(self):
        fn = self.font("body", 14)
        fp = self.font("title", 20)
        fr = self.font("body", 13)
        for widget in self._slot_widgets:
            widget.draw(self.screen, fn, fp, fr)

    def _draw_timer(self):
        """Affiche le compte à rebours jusqu'au prochain restock."""
        now       = int(time.time())
        remaining = max(0, self._available_until - now)

        f_label = self.font("body", 14)
        f_time  = self.font("title", 22)

        # Texte
        if remaining > 0:
            label = "Prochain restock dans :"
            time_str = _fmt_time(remaining)
            color = Colors.TEXT_GRAY
        else:
            label    = "Le shop est pret pour un restock !"
            time_str = ""
            color    = Colors.GREEN

        lt = f_label.render(label, True, Colors.TEXT_MUTED)
        self.screen.blit(lt, lt.get_rect(centerx=self.W // 2,
                                          y=SLOT_Y + SLOT_H + 30))

        if time_str:
            tt = f_time.render(time_str, True, color)
            self.screen.blit(tt, tt.get_rect(centerx=self.W // 2,
                                              y=SLOT_Y + SLOT_H + 52))

            # Barre de progression du timer
            total_s  = 24 * 3600   # 24h
            elapsed  = total_s - remaining
            ratio    = max(0.0, min(1.0, elapsed / total_s))
            bar_w    = 400
            bar_x    = self.W // 2 - bar_w // 2
            bar_y    = SLOT_Y + SLOT_H + 88

            # Fond
            pygame.draw.rect(self.screen, Colors.BG_PANEL2,
                             (bar_x, bar_y, bar_w, 10), border_radius=5)
            # Remplissage
            fill_w = max(4, int(bar_w * ratio))
            pygame.draw.rect(self.screen, Colors.BLUE,
                             (bar_x, bar_y, fill_w, 10), border_radius=5)