#Projet : Card Opening Simulator
#Auteurs : Fahreddin, Thyraël, Tristan, Augustin

"""
inventory_scene.py
Inventaire du joueur.
"""

import pygame
from collections import defaultdict
from engine.scene_manager import BaseScene, TransitionType
from engine.ui_components  import (
    Colors, Button, Panel, CoinDisplay, ProgressBar,
    ScrollView, draw_rounded_rect
)
from card import Rarity, Category, RARITY_SELL_VALUE


# Constantes layout
CARD_W      = 105
CARD_H      = 147
CARD_GAP    = 12
GRID_COLS   = 8
GRID_TOP    = 168    # y de début de la grille (sous les filtres + searchbar)
GRID_LEFT   = 20
BOTTOM_BAR  = 70     # hauteur de la barre du bas

# Couleurs des chips de filtre par rareté
RARITY_ORDER = [
    Rarity.COMMUNE, Rarity.RARE, Rarity.ÉPIQUE,
    Rarity.LÉGENDAIRE, Rarity.MYTHIQUE, Rarity.UNIQUE, Rarity.DIVINE,
]
RARITY_LABELS = {
    Rarity.COMMUNE:    "Commune",
    Rarity.RARE:       "Rare",
    Rarity.ÉPIQUE:     "Epique",
    Rarity.LÉGENDAIRE: "Legendaire",
    Rarity.MYTHIQUE:   "Mythique",
    Rarity.UNIQUE:     "Unique",
    Rarity.DIVINE:     "Divine",
}
CAT_LABELS = {
    Category.MEME:        "MEME",
    Category.MOTS:        "MOTS",
    Category.OBJETS:      "OBJETS",
    Category.PERSONNAGES: "PERSO",
    Category.CONCEPTS:    "CONCEPTS",
}
SORT_OPTIONS = ["Rareté", "Nom", "Quantité"]


# Helpers

def rarity_name(card) -> str:
    return card.rarity.name if hasattr(card.rarity, "name") else str(card.rarity)

def rarity_color(card) -> tuple:
    return Colors.RARITY.get(
        card.rarity.name if hasattr(card.rarity, "name") else str(card.rarity),
        Colors.BORDER
    )

def card_sell_value(card) -> int:
    return RARITY_SELL_VALUE.get(card.rarity) or 0


# Slot de carte dans la grille

class CardSlot:
    """Un slot = une carte unique avec sa quantité et son état de sélection."""

    def __init__(self, card, quantity: int, assets):
        self.card      = card
        self.quantity  = quantity
        self.assets    = assets
        self.selected  = False
        self._hover_t  = 0.0
        self._sel_t    = 0.0    # animation sélection
        # Position dans la grille (assignée par InventoryScene)
        self.grid_x    = 0
        self.grid_y    = 0

    @property
    def rect_on_grid(self) -> pygame.Rect:
        return pygame.Rect(self.grid_x, self.grid_y, CARD_W, CARD_H)

    def update(self, dt: int, mouse_pos, scroll_y: int):
        # Rect ajusté au scroll
        screen_rect = pygame.Rect(
            GRID_LEFT + self.grid_x,
            GRID_TOP  + self.grid_y - scroll_y,
            CARD_W, CARD_H
        )
        hovered = screen_rect.collidepoint(mouse_pos)
        target_h = 1.0 if hovered else 0.0
        target_s = 1.0 if self.selected else 0.0
        spd = dt / 100
        self._hover_t = min(1.0, self._hover_t + spd) if hovered else max(0.0, self._hover_t - spd)
        self._sel_t   = min(1.0, self._sel_t   + spd) if self.selected else max(0.0, self._sel_t - spd)

    def hit_test(self, pos, scroll_y: int) -> bool:
        screen_rect = pygame.Rect(
            GRID_LEFT + self.grid_x,
            GRID_TOP  + self.grid_y - scroll_y,
            CARD_W, CARD_H
        )
        return screen_rect.collidepoint(pos)

    def draw(self, surface: pygame.Surface, scroll_y: int):
        x = GRID_LEFT + self.grid_x
        y = GRID_TOP  + self.grid_y - scroll_y

        # Clipping : ne pas dessiner hors de la grille visible
        if y + CARD_H < GRID_TOP or y > surface.get_height() - BOTTOM_BAR:
            return

        # Élévation hover
        lift = int(self._hover_t * 5)
        draw_y = y - lift

        # Image de la carte
        img = self.assets.card_image(self.card.image_path, (CARD_W, CARD_H))
        surface.blit(img, (x, draw_y))

        # Bordure rareté
        rc = rarity_color(self.card)
        pygame.draw.rect(surface, rc, (x, draw_y, CARD_W, CARD_H), 2, border_radius=5)

        # Overlay sélection (teinte bleue)
        if self._sel_t > 0.05:
            sel_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
            sel_surf.fill((60, 130, 255, int(80 * self._sel_t)))
            surface.blit(sel_surf, (x, draw_y))
            # Contour épais de sélection
            pygame.draw.rect(surface, (80, 160, 255),
                             (x - 2, draw_y - 2, CARD_W + 4, CARD_H + 4),
                             2, border_radius=6)

        # Badge quantité (si > 1)
        if self.quantity > 1:
            label = f"x{self.quantity}"
            font  = pygame.font.SysFont("freesansbold", 11)
            tw    = font.size(label)[0] + 8
            bx    = x + CARD_W - tw - 2
            by    = draw_y + CARD_H - 18
            pygame.draw.rect(surface, (200, 40, 40),
                             (bx, by, tw, 16), border_radius=4)
            surf = font.render(label, True, (255, 255, 255))
            surface.blit(surf, (bx + 4, by + 2))

        # Checkmark si sélectionné
        if self.selected:
            font  = pygame.font.SysFont("freesansbold", 14)
            check = font.render("OK", True, (255, 255, 255))
            surface.blit(check, (x + 3, draw_y + 3))



# Barre de recherche

class SearchBar:
    """Champ de saisie texte pour filtrer les cartes par nom."""

    H = 28

    def __init__(self, rect, font: pygame.font.Font, placeholder: str = "Rechercher..."):
        self.rect        = pygame.Rect(rect)
        self._font       = font
        self._placeholder = placeholder
        self._text       = ""
        self._active     = False
        self._cursor_t   = 0    # timer clignotement curseur

    @property
    def text(self) -> str:
        return self._text

    def handle_event(self, e) -> bool:
        """Retourne True si le texte a changé."""
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self._active = self.rect.collidepoint(e.pos)

        elif e.type == pygame.KEYDOWN and self._active:
            if e.key == pygame.K_BACKSPACE:
                self._text = self._text[:-1]
                return True
            elif e.key == pygame.K_ESCAPE:
                self._text = ""
                self._active = False
                return True
            elif e.key == pygame.K_RETURN:
                self._active = False
            elif len(e.unicode) == 1 and e.unicode.isprintable():
                self._text += e.unicode
                return True
        return False

    def update(self, dt: int):
        self._cursor_t = (self._cursor_t + dt) % 1000

    def draw(self, surface: pygame.Surface):
        # Fond
        bg = Colors.BG_PANEL if self._active else Colors.BG_DARK
        bc = Colors.BORDER_H  if self._active else Colors.BORDER
        draw_rounded_rect(surface, bg, self.rect, 6, bc, 1)

        # Texte ou placeholder
        if self._text:
            txt_surf = self._font.render(self._text, True, Colors.TEXT_WHITE)
            txt_color = Colors.TEXT_WHITE
        else:
            txt_surf = self._font.render(self._placeholder, True, Colors.TEXT_MUTED)

        surface.blit(txt_surf, (self.rect.x + 10,
                                 self.rect.y + (self.rect.h - txt_surf.get_height()) // 2))

        # Curseur clignotant
        if self._active and self._cursor_t < 500:
            cx  = self.rect.x + 10 + self._font.size(self._text)[0] + 1
            cy1 = self.rect.y + 5
            cy2 = self.rect.y + self.rect.h - 5
            pygame.draw.line(surface, Colors.TEXT_WHITE, (cx, cy1), (cx, cy2), 1)

        # Icone loupe (simple cercle + ligne)
        lx = self.rect.right - 22
        ly = self.rect.centery
        pygame.draw.circle(surface, Colors.TEXT_MUTED, (lx, ly), 7, 1)
        pygame.draw.line(surface, Colors.TEXT_MUTED,
                         (lx + 5, ly + 5), (lx + 10, ly + 10), 2)

# Chip de filtre (rareté ou catégorie)

class FilterChip:
    H = 30

    def __init__(self, label: str, key, color: tuple, x: int, y: int):
        self.label    = label
        self.key      = key
        self.color    = color
        self.active   = False
        font          = pygame.font.SysFont("freesansbold", 13)
        tw            = font.size(label)[0]
        self.rect     = pygame.Rect(x, y, tw + 20, self.H)
        self._font    = font
        self._hovered = False

    def handle_event(self, e) -> bool:
        if e.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(e.pos)
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if self.rect.collidepoint(e.pos):
                self.active = not self.active
                return True
        return False

    def draw(self, surface: pygame.Surface):
        r, g, b = self.color[:3]
        if self.active:
            bg    = (r, g, b)
            text_color = (255, 255, 255)
            border = (min(r+60,255), min(g+60,255), min(b+60,255))
        else:
            bg    = (max(r-100,0), max(g-100,0), max(b-100,0))
            text_color = (r, g, b)
            border = (r, g, b)

        alpha = 230 if self.active else (200 if self._hovered else 160)
        draw_rounded_rect(surface, bg, self.rect, 8,
                          border_color=border, border_width=1, alpha=alpha)
        surf = self._font.render(self.label, True, text_color)
        surface.blit(surf, surf.get_rect(center=self.rect.center))


# InventoryScene

class InventoryScene(BaseScene):

    def __init__(self, manager):
        super().__init__(manager)

        # Filtres actifs
        self._search_text    = ""            # texte de recherche
        self._filter_rarities:  set = set()   # Rarity enums actifs
        self._filter_categories: set = set()  # Category enums actifs
        self._sort_idx   = 0    # index dans SORT_OPTIONS
        self._scroll_y   = 0
        self._max_scroll = 0

        # Slots de la grille
        self._all_slots:      list[CardSlot] = []
        self._visible_slots:  list[CardSlot] = []
        self._selected_slots: list[CardSlot] = []

        # Total valeur sélectionnée
        self._selected_value = 0

        self._build_slots()
        self._build_filter_chips()
        self._build_bottom_bar()
        self._apply_filters()

        self._coin_display = CoinDisplay(
            (self.W - 20, 22), self.font("body", 18), self.assets
        )

    # Construction

    def _build_slots(self):
        """Construit un slot par carte unique depuis l'inventaire du joueur."""
        if not self.player:
            return

        # Regrouper par card_id pour obtenir les quantités
        counts: dict = defaultdict(int)
        cards_by_id:  dict = {}
        for card in self.player.inventory.cards:
            counts[card.card_id] += 1
            cards_by_id[card.card_id] = card

        self._all_slots = [
            CardSlot(card, counts[cid], self.assets)
            for cid, card in cards_by_id.items()
        ]

    def _build_filter_chips(self):
        """Construit les chips de filtre rareté et catégorie."""
        f_h      = FilterChip.H
        gap      = 8
        y_r      = 55    # ligne raretés
        y_c      = 95    # ligne catégories
        x        = GRID_LEFT

        self._rarity_chips: list[FilterChip] = []
        for r in RARITY_ORDER:
            label = RARITY_LABELS[r]
            color = Colors.RARITY.get(r.name, Colors.BORDER)
            chip  = FilterChip(label, r, color, x, y_r)
            x    += chip.rect.w + gap
            self._rarity_chips.append(chip)

        x = GRID_LEFT
        self._cat_chips: list[FilterChip] = []
        for cat in Category:
            label = CAT_LABELS.get(cat, cat.name)
            chip  = FilterChip(label, cat, Colors.BLUE, x, y_c)
            x    += chip.rect.w + gap
            self._cat_chips.append(chip)

        # Boutons de tri
        self._sort_buttons: list[Button] = []
        sort_x = self.W - 20
        f = self.font("body", 13)
        for opt in reversed(SORT_OPTIONS):
            btn_w = f.size(opt)[0] + 24
            sort_x -= btn_w + 6
            btn = Button((sort_x, 55, btn_w, 26), opt, f,
                         color=Colors.BG_PANEL2,
                         hover_color=Colors.BG_PANEL,
                         radius=6)
            self._sort_buttons.insert(0, btn)

        # Barre de recherche (ligne 3, sous les catégories)
        search_w = 300
        self._search_bar = SearchBar(
            (GRID_LEFT, 128, search_w, SearchBar.H),
            self.font("body", 13),
            placeholder="Rechercher une carte..."
        )

    def _build_bottom_bar(self):
        """Boutons permanents en bas : vendre sélection + vendre par rareté."""
        f  = self.font("body", 16)
        cy = self.H - BOTTOM_BAR // 2 - 4

        self._btn_sell_sel = Button(
            (GRID_LEFT, self.H - BOTTOM_BAR + 12, 220, 46),
            "Vendre selection (0 pièce)", f,
            color=Colors.ORANGE, on_click=self._sell_selected,
            radius=10
        )
        self._btn_back = Button(
            (self.W - 150, self.H - BOTTOM_BAR + 12, 130, 46),
            "< Retour", f,
            on_click=self._go_back, radius=10
        )

        # Boutons vente rapide par rareté (communes et rares uniquement par défaut)
        self._quick_sell_buttons: list[tuple] = []
        bx   = 260
        fb   = self.font("body", 13)
        for r in [Rarity.COMMUNE, Rarity.RARE, Rarity.ÉPIQUE]:
            label = f"Vendre {RARITY_LABELS[r]}s"
            bw    = fb.size(label)[0] + 20
            btn   = Button(
                (bx, self.H - BOTTOM_BAR + 20, bw, 30),
                label, fb,
                color=Colors.BG_PANEL2,
                hover_color=(80, 50, 20),
                radius=6,
                on_click=lambda rv=r: self._sell_all_rarity(rv)
            )
            self._quick_sell_buttons.append(btn)
            bx += bw + 8

    # Filtres et tri

    def _apply_filters(self):
        """Recalcule _visible_slots selon les filtres actifs, puis replace la grille."""
        active_r = {c.key for c in self._rarity_chips   if c.active}
        active_c = {c.key for c in self._cat_chips       if c.active}

        search = self._search_text.strip().lower()
        filtered = [
            s for s in self._all_slots
            if (not active_r or s.card.rarity in active_r)
            and (not active_c or s.card.category in active_c)
            and (not search or search in s.card.name.lower())
        ]

        # Tri
        sort_key = SORT_OPTIONS[self._sort_idx]
        if sort_key == "Rareté":
            filtered.sort(key=lambda s: -(s.card.rarity.value
                                          if hasattr(s.card.rarity, "value") else 0))
        elif sort_key == "Nom":
            filtered.sort(key=lambda s: s.card.name.lower())
        elif sort_key == "Quantité":
            filtered.sort(key=lambda s: -s.quantity)

        self._visible_slots = filtered
        self._layout_grid()
        self._scroll_y = 0

    def _layout_grid(self):
        """Assigne les positions grille à chaque slot visible."""
        grid_w    = self.W - GRID_LEFT * 2
        cols      = max(1, (grid_w + CARD_GAP) // (CARD_W + CARD_GAP))
        self._cols = cols

        for i, slot in enumerate(self._visible_slots):
            col = i % cols
            row = i // cols
            slot.grid_x = col * (CARD_W + CARD_GAP)
            slot.grid_y = row * (CARD_H + CARD_GAP)

        rows = (len(self._visible_slots) + cols - 1) // cols if self._visible_slots else 1
        content_h    = rows * (CARD_H + CARD_GAP)
        visible_h    = self.H - GRID_TOP - BOTTOM_BAR
        self._max_scroll = max(0, content_h - visible_h)

    def _update_sell_button(self):
        """Met à jour le label et la valeur du bouton vendre sélection."""
        self._selected_slots = [s for s in self._visible_slots if s.selected]
        # Valeur = 1 seul exemplaire par slot sélectionné
        self._selected_value = sum(
            card_sell_value(s.card)
            for s in self._selected_slots
            if card_sell_value(s.card) > 0
        )
        n   = len(self._selected_slots)
        lbl = f"Vendre {n} carte(s) ({self._selected_value} pièces)" if n else "Rien de selectionne"
        self._btn_sell_sel.text     = lbl
        self._btn_sell_sel.disabled = (n == 0)

    # Navigation

    def _go_back(self):
        from scenes.menu_scene import MenuScene
        self.goto(MenuScene)

    # Ventes

    def _sell_selected(self):
        if not self._selected_slots or not self.player:
            return
        import database_manager as db

        total_earned = 0
        for slot in self._selected_slots:
            if card_sell_value(slot.card) <= 0:
                continue
            # Vendre UN SEUL exemplaire (pas toutes les copies)
            val = self.player.player_sell_card(slot.card)
            if val:
                total_earned += val
                db.db_sell_card(self.player.id, slot.card, self.player.coins)

        new_ach = self.player.check_achievements()
        db.db_sync_achievements(self.player.id, new_ach)
        db.db_update_max_coins(self.player.id, self.player.stats.max_coins_held)
        for a in new_ach:
            self.manager.show_achievement(a)

        self.manager.show_toast(
            f"+{total_earned} pièces  ({len(self._selected_slots)} cartes vendues)",
            Colors.GOLD
        )
        # Reconstruire les slots depuis l'inventaire mis à jour
        self._build_slots()
        self._apply_filters()

    def _sell_all_rarity(self, rarity: Rarity):
        if not self.player:
            return
        import database_manager as db
        from card import RARITY_SELL_VALUE

        if RARITY_SELL_VALUE.get(rarity) is None:
            self.manager.show_toast("Cette rarete est invendable.", Colors.RED)
            return

        cards_to_sell = [
            c for c in self.player.inventory.cards if c.rarity == rarity
        ]
        if not cards_to_sell:
            self.manager.show_toast(f"Aucune carte {RARITY_LABELS[rarity]}.", Colors.TEXT_GRAY)
            return

        gained = self.player.player_sell_all_by_rarity(rarity)
        db.db_sell_all_by_rarity(self.player.id, rarity,
                                  self.player.coins, cards_to_sell)
        new_ach = self.player.check_achievements()
        db.db_sync_achievements(self.player.id, new_ach)
        db.db_update_max_coins(self.player.id, self.player.stats.max_coins_held)
        for a in new_ach:
            self.manager.show_achievement(a)

        self.manager.show_toast(
            f"+{gained} pièces  ({len(cards_to_sell)} {RARITY_LABELS[rarity]}s vendues)",
            Colors.GOLD
        )
        self._build_slots()
        self._apply_filters()

    # Boucle

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()

        for e in events:
            # Scroll molette (dans la zone grille)
            if e.type == pygame.MOUSEWHEEL:
                mx, my = mouse_pos
                in_grid = (GRID_LEFT <= mx <= self.W - GRID_LEFT
                           and GRID_TOP <= my <= self.H - BOTTOM_BAR)
                if in_grid:
                    self._scroll_y = max(0, min(
                        self._scroll_y - e.y * 40,
                        self._max_scroll
                    ))

            # Barre de recherche
            if self._search_bar.handle_event(e):
                self._search_text = self._search_bar.text
                self._apply_filters()
                self._update_sell_button()

            # Filtres
            filter_changed = False
            for chip in self._rarity_chips + self._cat_chips:
                if chip.handle_event(e):
                    filter_changed = True
            if filter_changed:
                self._apply_filters()
                self._update_sell_button()

            # Tri
            for i, btn in enumerate(self._sort_buttons):
                if btn.handle_event(e):
                    self._sort_idx = i
                    self._apply_filters()

            # Clic sur une carte (toggle sélection)
            if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                # Vérifier si le clic est dans la zone grille
                mx, my = e.pos
                if (GRID_LEFT <= mx <= self.W - GRID_LEFT
                        and GRID_TOP <= my <= self.H - BOTTOM_BAR):
                    for slot in self._visible_slots:
                        if slot.hit_test(e.pos, self._scroll_y):
                            slot.selected = not slot.selected
                            self.assets.play("sfx_card_flip", 0.4)
                            break
                    self._update_sell_button()

            # Boutons bas
            self._btn_sell_sel.handle_event(e)
            self._btn_back.handle_event(e)
            for btn in self._quick_sell_buttons:
                btn.handle_event(e)

    def update(self, dt: int):
        mouse_pos = pygame.mouse.get_pos()
        self._search_bar.update(dt)
        for slot in self._visible_slots:
            slot.update(dt, mouse_pos, self._scroll_y)

    def on_resume(self):
        """Rafraîchir après retour d'une autre scène."""
        self._build_slots()
        self._apply_filters()
        self._update_sell_button()

    # Draw

    def draw(self):
        self.screen.fill(Colors.BG_DARK)
        self._draw_header()
        self._draw_grid()
        self._draw_bottom_bar()
        self._coin_display.draw(self.screen,
                                self.player.coins if self.player else 0)

    def _draw_header(self):
        # Titre + compteur
        f_title = self.font("title", 28)
        total   = len(self._all_slots)
        visible = len(self._visible_slots)
        title   = f"Inventaire  ({visible}/{total} cartes)"
        t = f_title.render(title, True, Colors.TEXT_WHITE)
        self.screen.blit(t, (GRID_LEFT, 14))

        # Chips rareté
        for chip in self._rarity_chips:
            chip.draw(self.screen)

        # Chips catégorie
        for chip in self._cat_chips:
            chip.draw(self.screen)

        # Boutons tri
        f_sort = self.font("body", 13)
        label  = f_sort.render(f"Tri: {SORT_OPTIONS[self._sort_idx]}", True, Colors.TEXT_GRAY)
        self.screen.blit(label, (self.W - 20 - label.get_width(), 92))
        for btn in self._sort_buttons:
            btn.draw(self.screen)

        # Barre de recherche
        self._search_bar.draw(self.screen)

        # Séparateur
        pygame.draw.line(self.screen, Colors.BORDER,
                         (GRID_LEFT, GRID_TOP - 8),
                         (self.W - GRID_LEFT, GRID_TOP - 8), 1)

    def _draw_grid(self):
        # Zone de clipping pour ne pas déborder sur header/footer
        clip = pygame.Rect(0, GRID_TOP, self.W, self.H - GRID_TOP - BOTTOM_BAR)
        self.screen.set_clip(clip)

        for slot in self._visible_slots:
            slot.draw(self.screen, self._scroll_y)

        # Message si vide
        if not self._visible_slots:
            f = self.font("body", 18)
            t = f.render("Aucune carte ne correspond aux filtres.", True, Colors.TEXT_MUTED)
            self.screen.blit(t, t.get_rect(center=(self.W // 2, self.H // 2)))

        self.screen.set_clip(None)

        # Scrollbar
        if self._max_scroll > 0:
            visible_h = self.H - GRID_TOP - BOTTOM_BAR
            total_h   = visible_h + self._max_scroll
            ratio     = visible_h / total_h
            bar_h     = max(30, int(visible_h * ratio))
            bar_y     = GRID_TOP + int(
                (self._scroll_y / self._max_scroll) * (visible_h - bar_h)
            )
            pygame.draw.rect(self.screen, Colors.BG_PANEL2,
                             (self.W - 8, GRID_TOP, 6, visible_h), border_radius=3)
            pygame.draw.rect(self.screen, Colors.BORDER_H,
                             (self.W - 8, bar_y, 6, bar_h), border_radius=3)

    def _draw_bottom_bar(self):
        # Fond de la barre
        bar_rect = (0, self.H - BOTTOM_BAR, self.W, BOTTOM_BAR)
        draw_rounded_rect(self.screen, Colors.BG_PANEL, bar_rect, 0,
                          border_color=Colors.BORDER, border_width=1, alpha=240)

        self._btn_sell_sel.draw(self.screen)
        self._btn_back.draw(self.screen)
        for btn in self._quick_sell_buttons:
            btn.draw(self.screen)