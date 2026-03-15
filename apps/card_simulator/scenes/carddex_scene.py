"""
carddex_scene.py
================
CardDex — toutes les 756 cartes du jeu.

Fonctionnalités :
  - Grille de toutes les cartes (découvertes + silhouettes)
  - Barre de progression globale
  - Filtres rareté + catégorie + recherche (même système que l'inventaire)
  - Tri : rareté, nom, ID
  - Popup de détail sur clic d'une carte découverte
"""

import pygame
from engine.scene_manager import BaseScene, TransitionType
from engine.ui_components  import (
    Colors, Button, CoinDisplay, ProgressBar, draw_rounded_rect
)
from card import Rarity, Category

# Réutilisation des composants de l'inventaire
from scenes.inventory_scene import SearchBar, FilterChip


# ── Constantes layout ─────────────────────────────────────────────────────────
CARD_W     = 100
CARD_H     = 140
CARD_GAP   = 10
GRID_TOP   = 168
GRID_LEFT  = 20
BOTTOM_H   = 50

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
SORT_OPTIONS = ["Rareté", "Nom", "ID"]


def _rarity_color(rarity_name: str) -> tuple:
    return Colors.RARITY.get(rarity_name, Colors.BORDER)


# ═══════════════════════════════════════════════════════════════════════════════
# CardDetailPopup — popup de détail d'une carte découverte
# ═══════════════════════════════════════════════════════════════════════════════

class CardDetailPopup:
    W = 520
    H = 340

    def __init__(self, card, screen_size, font_title, font_body, assets):
        sw, sh     = screen_size
        self.rect  = pygame.Rect((sw - self.W) // 2, (sh - self.H) // 2,
                                  self.W, self.H)
        self._card = card
        self._ft   = font_title
        self._fb   = font_body
        self._assets = assets
        self._btn_close = Button(
            (self.rect.right - 100, self.rect.bottom - 56, 84, 36),
            "Fermer", font_body,
            color=Colors.BG_PANEL2, on_click=lambda: None
        )

    def handle_event(self, e) -> bool:
        """Retourne True si on doit fermer le popup."""
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if not self.rect.collidepoint(e.pos):
                return True
            if self._btn_close.rect.collidepoint(e.pos):
                return True
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            return True
        self._btn_close.handle_event(e)
        return False

    def draw(self, surface):
        # Dim
        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 170))
        surface.blit(dim, (0, 0))

        # Panel
        rname = (self._card.rarity.name
                 if hasattr(self._card.rarity, "name") else str(self._card.rarity))
        rc = _rarity_color(rname)
        draw_rounded_rect(surface, Colors.BG_PANEL, self.rect, 14,
                          border_color=rc, border_width=2)

        # Image à gauche
        img_w, img_h = 140, 196
        img = self._assets.card_image(self._card.image_path, (img_w, img_h))
        img_x = self.rect.x + 20
        img_y = self.rect.y + (self.H - img_h) // 2
        surface.blit(img, (img_x, img_y))
        pygame.draw.rect(surface, rc, (img_x, img_y, img_w, img_h), 2, border_radius=8)

        # Infos à droite
        tx = img_x + img_w + 22
        ty = self.rect.y + 24

        # Nom
        t_name = self._ft.render(self._card.name, True, Colors.TEXT_WHITE)
        surface.blit(t_name, (tx, ty))

        # Rareté
        rl = RARITY_LABELS.get(self._card.rarity, rname)
        t_rar = self._fb.render(rl, True, rc)
        surface.blit(t_rar, (tx, ty + 32))

        # Catégorie
        cat = self._card.category
        cat_str = (CAT_LABELS.get(cat, cat.name)
                   if hasattr(cat, "name") else str(cat)) if cat else "?"
        t_cat = self._fb.render(f"Cat. : {cat_str}", True, Colors.TEXT_GRAY)
        surface.blit(t_cat, (tx, ty + 56))

        # Stats
        f_stat = pygame.font.SysFont("freesansbold", 13)
        for i, (label, val) in enumerate([
            ("Impact",    self._card.stat1),
            ("Popularité", self._card.stat2),
            ("Longévité", self._card.stat3),
        ]):
            ts = f_stat.render(f"{label} : {val}", True, Colors.TEXT_GRAY)
            surface.blit(ts, (tx, ty + 86 + i * 20))

        # Description
        desc = self._card.description or ""
        if len(desc) > 60:
            desc = desc[:58] + "..."
        t_desc = self._fb.render(desc, True, Colors.TEXT_MUTED)
        surface.blit(t_desc, (tx, ty + 158))

        # Auteur
        t_auth = self._fb.render(f"Par : {self._card.author or '?'}", True, Colors.TEXT_MUTED)
        surface.blit(t_auth, (tx, ty + 182))

        # ID
        t_id = self._fb.render(f"#{self._card.card_id}", True, Colors.TEXT_MUTED)
        surface.blit(t_id, (tx, ty + 206))

        self._btn_close.draw(surface)


# ═══════════════════════════════════════════════════════════════════════════════
# CardDexScene
# ═══════════════════════════════════════════════════════════════════════════════

class CardDexScene(BaseScene):

    def __init__(self, manager):
        super().__init__(manager)

        self._all_cards    = []   # toutes les cartes DB [{card, discovered}]
        self._visible      = []   # après filtres
        self._scroll_y     = 0
        self._max_scroll   = 0
        self._search_text  = ""
        self._sort_idx     = 0
        self._popup        = None

        self._coin_display = CoinDisplay(
            (self.W - 20, 22), self.font("body", 18), self.assets
        )
        self._btn_back = Button(
            (20, self.H - BOTTOM_H + 5, 130, 40), "< Retour",
            self.font("body", 15), on_click=self._go_back
        )
        self._progress_bar = ProgressBar(
            rect=(self.W // 2 - 200, 35, 400, 14),
            color=Colors.GREEN
        )

        self._load_all_cards()
        self._build_chips()
        self._apply_filters()

    # ── Chargement ────────────────────────────────────────────────────────────

    def _load_all_cards(self):
        """Charge toutes les 756 cartes depuis la DB + marque les découvertes."""
        import database_manager as db
        from card import Card

        discovered_ids = set()
        if self.player:
            discovered_ids = self.player.carddex.collected_cards

        conn = db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM CARDS ORDER BY rarity, card_id ASC"
            )
            rows = cursor.fetchall()
        finally:
            conn.close()

        self._all_cards = []
        for row in rows:
            from database_manager import _db_str_to_rarity, _db_str_to_category
            card = Card(
                card_id=row["card_id"], name=row["name"],
                rarity=_db_str_to_rarity(row["rarity"]),
                category=_db_str_to_category(row["category"]),
                stat1=row["stat1"], stat2=row["stat2"], stat3=row["stat3"],
                description=row["description"], author=row["author"],
                image_path=row["image_path"],
            )
            self._all_cards.append({
                "card":       card,
                "discovered": card.card_id in discovered_ids,
                "x": 0, "y": 0,
            })

    def _build_chips(self):
        gap  = 8
        y_r  = 55
        y_c  = 95
        x    = GRID_LEFT
        f    = self.font("body", 13)

        self._rarity_chips = []
        for r in RARITY_ORDER:
            label = RARITY_LABELS[r]
            color = Colors.RARITY.get(r.name, Colors.BORDER)
            chip  = FilterChip(label, r, color, x, y_r)
            x    += chip.rect.w + gap
            self._rarity_chips.append(chip)

        x = GRID_LEFT
        self._cat_chips = []
        for cat in Category:
            label = CAT_LABELS.get(cat, cat.name)
            chip  = FilterChip(label, cat, Colors.BLUE, x, y_c)
            x    += chip.rect.w + gap
            self._cat_chips.append(chip)

        # Chips "Découvertes / Non découvertes"
        self._discovered_chip = FilterChip("Decouvertes",     "discovered", Colors.GREEN,
                                            x + gap * 2, y_c)
        self._undiscovered_chip = FilterChip("Non decouvertes", "undiscovered", Colors.RED,
                                              self._discovered_chip.rect.right + gap, y_c)

        # Tri
        self._sort_buttons = []
        sx = self.W - 20
        for opt in reversed(SORT_OPTIONS):
            bw = f.size(opt)[0] + 24
            sx -= bw + 6
            btn = Button((sx, 55, bw, 26), opt, f,
                         color=Colors.BG_PANEL2, hover_color=Colors.BG_PANEL, radius=6)
            self._sort_buttons.insert(0, btn)

        # Barre de recherche
        self._search_bar = SearchBar(
            (GRID_LEFT, 128, 300, SearchBar.H),
            self.font("body", 13),
            placeholder="Rechercher une carte..."
        )

    # ── Filtres ───────────────────────────────────────────────────────────────

    def _apply_filters(self):
        active_r   = {c.key for c in self._rarity_chips if c.active}
        active_c   = {c.key for c in self._cat_chips    if c.active}
        show_disc  = self._discovered_chip.active
        show_undisc = self._undiscovered_chip.active
        search     = self._search_text.strip().lower()

        filtered = []
        for item in self._all_cards:
            card = item["card"]
            disc = item["discovered"]

            if active_r and card.rarity not in active_r:
                continue
            if active_c and card.category not in active_c:
                continue
            if show_disc and not disc:
                continue
            if show_undisc and disc:
                continue
            if search and search not in card.name.lower():
                continue
            filtered.append(item)

        sort_key = SORT_OPTIONS[self._sort_idx]
        if sort_key == "Rareté":
            filtered.sort(key=lambda i: (
                -(i["card"].rarity.value if hasattr(i["card"].rarity, "value") else 0),
                i["card"].name.lower()
            ))
        elif sort_key == "Nom":
            filtered.sort(key=lambda i: i["card"].name.lower())
        elif sort_key == "ID":
            filtered.sort(key=lambda i: i["card"].card_id)

        self._visible = filtered
        self._layout_grid()
        self._scroll_y = 0

    def _layout_grid(self):
        grid_w = self.W - GRID_LEFT * 2
        cols   = max(1, (grid_w + CARD_GAP) // (CARD_W + CARD_GAP))

        for i, item in enumerate(self._visible):
            item["x"] = GRID_LEFT + (i % cols) * (CARD_W + CARD_GAP)
            item["y"] = (i // cols) * (CARD_H + CARD_GAP)

        rows      = (len(self._visible) + cols - 1) // cols if self._visible else 1
        content_h = rows * (CARD_H + CARD_GAP)
        visible_h = self.H - GRID_TOP - BOTTOM_H
        self._max_scroll = max(0, content_h - visible_h)

    # ── Navigation ────────────────────────────────────────────────────────────

    def _go_back(self):
        from scenes.menu_scene import MenuScene
        self.goto(MenuScene)

    # ── Boucle ────────────────────────────────────────────────────────────────

    def handle_events(self, events):
        for e in events:
            if self._popup:
                if self._popup.handle_event(e):
                    self._popup = None
                return

            self._btn_back.handle_event(e)

            if e.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                if GRID_TOP <= my <= self.H - BOTTOM_H:
                    self._scroll_y = max(0, min(
                        self._scroll_y - e.y * 40, self._max_scroll
                    ))

            # Chips + recherche → refiltrer
            changed = False
            for chip in (self._rarity_chips + self._cat_chips +
                         [self._discovered_chip, self._undiscovered_chip]):
                if chip.handle_event(e):
                    changed = True
            if changed:
                self._apply_filters()

            for i, btn in enumerate(self._sort_buttons):
                if btn.handle_event(e):
                    self._sort_idx = i
                    self._apply_filters()

            if self._search_bar.handle_event(e):
                self._search_text = self._search_bar.text
                self._apply_filters()

            # Clic sur une carte → popup si découverte
            if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                mx, my = e.pos
                if GRID_TOP <= my <= self.H - BOTTOM_H:
                    for item in self._visible:
                        cx = item["x"]
                        cy = GRID_TOP + item["y"] - self._scroll_y
                        if (cx <= mx <= cx + CARD_W and cy <= my <= cy + CARD_H):
                            if item["discovered"]:
                                self._popup = CardDetailPopup(
                                    item["card"], (self.W, self.H),
                                    self.font("title", 20),
                                    self.font("body", 15),
                                    self.assets
                                )
                            break

    def update(self, dt):
        self._search_bar.update(dt)

    def on_resume(self):
        self._load_all_cards()
        self._apply_filters()

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self):
        self.screen.fill(Colors.BG_DARK)
        self._draw_header()
        self._draw_grid()
        self._draw_bottom()
        self._coin_display.draw(self.screen,
                                self.player.coins if self.player else 0)
        if self._popup:
            self._popup.draw(self.screen)

    def _draw_header(self):
        # Titre + compteur découvertes
        total = len(self._all_cards)
        disc  = sum(1 for i in self._all_cards if i["discovered"])
        pct   = disc / total * 100 if total else 0

        f_title = self.font("title", 26)
        t = f_title.render(f"CardDex  {disc}/{total}", True, Colors.TEXT_WHITE)
        self.screen.blit(t, (GRID_LEFT, 14))

        # Barre de progression
        self._progress_bar.value = pct / 100
        self._progress_bar.draw(self.screen)

        f_pct = self.font("body", 13)
        tp = f_pct.render(f"{pct:.1f}%", True, Colors.GREEN if pct > 50 else Colors.TEXT_GRAY)
        self.screen.blit(tp, (self.W // 2 + 206, 32))

        # Chips rareté
        for chip in self._rarity_chips:
            chip.draw(self.screen)

        # Chips catégorie + découverte
        for chip in self._cat_chips:
            chip.draw(self.screen)
        self._discovered_chip.draw(self.screen)
        self._undiscovered_chip.draw(self.screen)

        # Tri
        f_s = self.font("body", 13)
        ts  = f_s.render(f"Tri: {SORT_OPTIONS[self._sort_idx]}", True, Colors.TEXT_GRAY)
        self.screen.blit(ts, (self.W - 20 - ts.get_width(), 92))
        for btn in self._sort_buttons:
            btn.draw(self.screen)

        # Recherche
        self._search_bar.draw(self.screen)

        # Séparateur
        pygame.draw.line(self.screen, Colors.BORDER,
                         (GRID_LEFT, GRID_TOP - 8),
                         (self.W - GRID_LEFT, GRID_TOP - 8), 1)

    def _draw_grid(self):
        clip = pygame.Rect(0, GRID_TOP, self.W, self.H - GRID_TOP - BOTTOM_H)
        self.screen.set_clip(clip)

        silhouette = self.assets.image("card_silhouette", (CARD_W, CARD_H))

        for item in self._visible:
            x    = item["x"]
            y    = GRID_TOP + item["y"] - self._scroll_y
            card = item["card"]
            disc = item["discovered"]

            if y + CARD_H < GRID_TOP or y > self.H - BOTTOM_H:
                continue

            if disc:
                img = self.assets.card_image(card.image_path, (CARD_W, CARD_H))
                self.screen.blit(img, (x, y))
                rname = (card.rarity.name if hasattr(card.rarity, "name")
                         else str(card.rarity))
                rc = _rarity_color(rname)
                pygame.draw.rect(self.screen, rc,
                                 (x, y, CARD_W, CARD_H), 2, border_radius=5)
            else:
                # Silhouette + point d'interrogation
                self.screen.blit(silhouette, (x, y))
                f_q = pygame.font.SysFont("freesansbold", 28)
                q   = f_q.render("?", True, (50, 55, 75))
                self.screen.blit(q, q.get_rect(center=(x + CARD_W // 2,
                                                        y + CARD_H // 2)))

        self.screen.set_clip(None)

        # Scrollbar
        if self._max_scroll > 0:
            visible_h = self.H - GRID_TOP - BOTTOM_H
            ratio  = visible_h / (visible_h + self._max_scroll)
            bar_h  = max(30, int(visible_h * ratio))
            bar_y  = GRID_TOP + int(
                (self._scroll_y / self._max_scroll) * (visible_h - bar_h)
            )
            pygame.draw.rect(self.screen, Colors.BG_PANEL2,
                             (self.W - 8, GRID_TOP, 6, visible_h), border_radius=3)
            pygame.draw.rect(self.screen, Colors.BORDER_H,
                             (self.W - 8, bar_y, 6, bar_h), border_radius=3)

        # Message si vide
        if not self._visible:
            f = self.font("body", 16)
            t = f.render("Aucune carte ne correspond aux filtres.",
                         True, Colors.TEXT_MUTED)
            self.screen.blit(t, t.get_rect(center=(self.W // 2, self.H // 2)))

    def _draw_bottom(self):
        bar = (0, self.H - BOTTOM_H, self.W, BOTTOM_H)
        draw_rounded_rect(self.screen, Colors.BG_PANEL, bar, 0,
                          border_color=Colors.BORDER, border_width=1, alpha=220)
        self._btn_back.draw(self.screen)
        # Compteur visible
        f  = self.font("body", 14)
        tv = f.render(f"{len(self._visible)} carte(s) affichee(s)", True, Colors.TEXT_MUTED)
        self.screen.blit(tv, tv.get_rect(center=(self.W // 2, self.H - BOTTOM_H // 2)))