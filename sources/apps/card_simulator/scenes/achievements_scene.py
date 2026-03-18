#Projet : Card Opening Simulator
#Auteurs : Fahreddin, Thyraël, Tristan, Augustin

"""
achievements_scene.py
Ecran des succès du joueur.
"""

import pygame
import time
from engine.scene_manager import BaseScene, TransitionType
from engine.ui_components  import (
    Colors, Button, CoinDisplay, ProgressBar, draw_rounded_rect
)
from achievements import ACHIEVEMENTS


# Constantes layout
HEADER_H   = 130    # hauteur du header (titre + barre + filtres)
BOTTOM_H   = 55
ROW_H      = 80     # hauteur d'une ligne d'achievement
ROW_GAP    = 8
ROW_LEFT   = 20
ICON_SIZE  = 48

# Couleurs par catégorie d'achievement (basé sur le préfixe de l'ID)
CATEGORY_COLORS = {
    "first":   (210, 150,  20),   # or - premières fois
    "chest":   ( 60, 130, 255),   # bleu - coffres
    "fusion":  (220, 110,  40),   # orange - fusions
    "earn":    ( 50, 195,  90),   # vert - économie
    "sell":    (200,  80,  80),   # rouge - ventes
    "shop":    ( 80, 180, 220),   # cyan - shop
    "daily":   (240, 200,  50),   # jaune - daily
    "carddex": (150,  50, 210),   # violet - carddex
}

def _category_color(ach_id: str) -> tuple:
    for prefix, color in CATEGORY_COLORS.items():
        if ach_id.startswith(prefix):
            return color
    return Colors.BORDER_H

def _fmt_date(timestamp: int) -> str:
    if not timestamp:
        return ""
    t = time.localtime(timestamp)
    return f"{t.tm_mday:02d}/{t.tm_mon:02d}/{t.tm_year}  {t.tm_hour:02d}:{t.tm_min:02d}"


# AchievementsScene

class AchievementsScene(BaseScene):

    FILTER_ALL      = "all"
    FILTER_UNLOCKED = "unlocked"
    FILTER_LOCKED   = "locked"

    def __init__(self, manager):
        super().__init__(manager)

        self._scroll_y   = 0
        self._max_scroll = 0
        self._filter     = self.FILTER_ALL

        # Données : {ach, unlocked: bool, unlocked_at: int|None}
        self._all_rows = []
        self._visible  = []

        self._progress_bar = ProgressBar(
            rect=(ROW_LEFT, 55, self.W - ROW_LEFT * 2, 14),
            color=Colors.GOLD
        )
        self._btn_back = Button(
            (ROW_LEFT, self.H - BOTTOM_H + 8, 130, 40),
            "< Retour", self.font("body", 15),
            on_click=self._go_back
        )

        self._build_filter_buttons()
        self._load_achievements()
        self._apply_filter()

    # Chargement

    def _load_achievements(self):
        """Charge tous les achievements + dates de déblocage depuis la DB."""
        import database_manager as db

        # Récupérer les unlocked_at depuis la DB
        unlocked_map = {}   # id → unlocked_at timestamp
        if self.player:
            try:
                rows = db.fetch_unlocked_achievements(self.player.id)
                for row in rows:
                    unlocked_map[row["achievement_id"]] = row["unlocked_at"]
            except Exception as e:
                print(f"[AchievementsScene] {e}")

        unlocked_ids = self.player.stats.achievements if self.player else set()

        self._all_rows = [
            {
                "ach":         ach,
                "unlocked":    ach.id in unlocked_ids,
                "unlocked_at": unlocked_map.get(ach.id, None),
            }
            for ach in ACHIEVEMENTS
        ]

    # Filtres

    def _build_filter_buttons(self):
        f   = self.font("body", 14)
        bw  = 120
        gap = 10
        total_w = 3 * bw + 2 * gap
        sx  = self.W // 2 - total_w // 2

        self._filter_btns = [
            (self.FILTER_ALL,      Button((sx,             80, bw, 32), "Tous",         f, radius=8)),
            (self.FILTER_UNLOCKED, Button((sx + bw + gap,  80, bw, 32), "Obtenus",      f, radius=8)),
            (self.FILTER_LOCKED,   Button((sx + 2*(bw+gap), 80, bw, 32), "Non obtenus", f, radius=8)),
        ]
        self._update_filter_colors()

    def _update_filter_colors(self):
        for key, btn in self._filter_btns:
            if key == self._filter:
                btn.color       = Colors.GOLD
                btn.hover_color = Colors.GOLD
            else:
                btn.color       = Colors.BG_PANEL2
                btn.hover_color = Colors.BG_PANEL

    def _apply_filter(self):
        if self._filter == self.FILTER_ALL:
            self._visible = list(self._all_rows)
        elif self._filter == self.FILTER_UNLOCKED:
            self._visible = [r for r in self._all_rows if r["unlocked"]]
        else:
            self._visible = [r for r in self._all_rows if not r["unlocked"]]

        # Tri : obtenus en premier (par date desc), puis verrouillés
        self._visible.sort(key=lambda r: (
            0 if r["unlocked"] else 1,
            -(r["unlocked_at"] or 0)
        ))

        self._compute_scroll()
        self._scroll_y = 0

    def _compute_scroll(self):
        content_h    = len(self._visible) * (ROW_H + ROW_GAP)
        visible_h    = self.H - HEADER_H - BOTTOM_H
        self._max_scroll = max(0, content_h - visible_h)

    # Navigation

    def _go_back(self):
        from scenes.menu_scene import MenuScene
        self.goto(MenuScene)

    # Boucle

    def handle_events(self, events):
        for e in events:
            self._btn_back.handle_event(e)

            if e.type == pygame.MOUSEWHEEL:
                self._scroll_y = max(0, min(
                    self._scroll_y - e.y * 40, self._max_scroll
                ))

            for key, btn in self._filter_btns:
                if btn.handle_event(e):
                    self._filter = key
                    self._update_filter_colors()
                    self._apply_filter()

    def update(self, dt):
        pass

    def on_resume(self):
        self._load_achievements()
        self._apply_filter()

    # Draw

    def draw(self):
        self.screen.fill(Colors.BG_DARK)
        self._draw_header()
        self._draw_list()
        self._draw_bottom()

    def _draw_header(self):
        total    = len(self._all_rows)
        unlocked = sum(1 for r in self._all_rows if r["unlocked"])
        pct      = unlocked / total if total else 0

        # Titre
        f_title = self.font("title", 26)
        t = f_title.render(f"Succes  {unlocked}/{total}", True, Colors.TEXT_WHITE)
        self.screen.blit(t, (ROW_LEFT, 14))

        # Barre de progression
        self._progress_bar.value = pct
        self._progress_bar.color = Colors.GOLD if pct >= 1.0 else Colors.GREEN
        self._progress_bar.draw(self.screen)

        f_pct = self.font("body", 13)
        tp = f_pct.render(f"{pct*100:.1f}%", True,
                          Colors.GOLD if pct >= 1.0 else Colors.TEXT_GRAY)
        self.screen.blit(tp, (self.W - ROW_LEFT - tp.get_width(), 55))

        # Filtres
        for _, btn in self._filter_btns:
            btn.draw(self.screen)

        # Séparateur
        pygame.draw.line(self.screen, Colors.BORDER,
                         (ROW_LEFT, HEADER_H - 6),
                         (self.W - ROW_LEFT, HEADER_H - 6), 1)

    def _draw_list(self):
        clip = pygame.Rect(0, HEADER_H, self.W, self.H - HEADER_H - BOTTOM_H)
        self.screen.set_clip(clip)

        f_name = self.font("body", 16)
        f_desc = self.font("body", 13)
        f_date = self.font("body", 12)

        row_w = self.W - ROW_LEFT * 2

        for i, row in enumerate(self._visible):
            y = HEADER_H + i * (ROW_H + ROW_GAP) - self._scroll_y
            if y + ROW_H < HEADER_H or y > self.H - BOTTOM_H:
                continue

            ach      = row["ach"]
            unlocked = row["unlocked"]
            color    = _category_color(ach.id)

            # Fond de la ligne
            bg    = Colors.BG_PANEL if unlocked else Colors.BG_DARK
            bc    = color if unlocked else Colors.BORDER
            bw    = 2 if unlocked else 1
            draw_rounded_rect(self.screen, bg,
                              (ROW_LEFT, y, row_w, ROW_H), 10,
                              border_color=bc, border_width=bw,
                              alpha=220 if unlocked else 140)

            # Icône
            icon = self.assets.achievement_icon(ach.id, (ICON_SIZE, ICON_SIZE))
            ix   = ROW_LEFT + 14
            iy   = y + (ROW_H - ICON_SIZE) // 2

            if unlocked:
                self.screen.blit(icon, (ix, iy))
                # Cercle coloré autour de l'icône
                pygame.draw.circle(self.screen, color,
                                   (ix + ICON_SIZE // 2, iy + ICON_SIZE // 2),
                                   ICON_SIZE // 2 + 4, 2)
            else:
                # Icône grisée
                gray = icon.copy()
                gray_surf = pygame.Surface(gray.get_size(), pygame.SRCALPHA)
                gray_surf.fill((40, 45, 65, 200))
                gray.blit(gray_surf, (0, 0))
                self.screen.blit(gray, (ix, iy))
                # Cadenas
                f_lock = pygame.font.SysFont("freesansbold", 14)
                lock   = f_lock.render("X", True, (60, 65, 85))
                self.screen.blit(lock, lock.get_rect(
                    center=(ix + ICON_SIZE // 2, iy + ICON_SIZE // 2)))

            # Textes
            tx = ix + ICON_SIZE + 16

            name_color = color if unlocked else Colors.TEXT_MUTED
            nt = f_name.render(ach.name, True, name_color)
            self.screen.blit(nt, (tx, y + 14))

            dt = f_desc.render(ach.description, True,
                               Colors.TEXT_GRAY if unlocked else Colors.TEXT_MUTED)
            self.screen.blit(dt, (tx, y + 36))

            # Date de déblocage
            if unlocked and row["unlocked_at"]:
                date_str = _fmt_date(row["unlocked_at"])
                ds = f_date.render(f"Debloque le {date_str}", True,
                                   (100, 110, 80))
                self.screen.blit(ds, (tx, y + 56))

            # Badge statut (droite)
            bx = ROW_LEFT + row_w - 110
            by = y + (ROW_H - 28) // 2
            if unlocked:
                draw_rounded_rect(self.screen, (30, 60, 30),
                                  (bx, by, 100, 28), 8,
                                  border_color=(50, 180, 50), border_width=1)
                f_ok = pygame.font.SysFont("freesansbold", 13)
                ok_t = f_ok.render("OBTENU", True, (80, 220, 80))
                self.screen.blit(ok_t, ok_t.get_rect(
                    center=(bx + 50, by + 14)))
            else:
                draw_rounded_rect(self.screen, (40, 40, 55),
                                  (bx, by, 100, 28), 8,
                                  border_color=Colors.BORDER, border_width=1)
                f_lk = pygame.font.SysFont("freesansbold", 13)
                lk_t = f_lk.render("VERROUILLE", True, Colors.TEXT_MUTED)
                self.screen.blit(lk_t, lk_t.get_rect(
                    center=(bx + 50, by + 14)))

        self.screen.set_clip(None)

        # Scrollbar
        if self._max_scroll > 0:
            visible_h = self.H - HEADER_H - BOTTOM_H
            ratio  = visible_h / (visible_h + self._max_scroll)
            bar_h  = max(30, int(visible_h * ratio))
            bar_y  = HEADER_H + int(
                (self._scroll_y / self._max_scroll) * (visible_h - bar_h)
            )
            pygame.draw.rect(self.screen, Colors.BG_PANEL2,
                             (self.W - 8, HEADER_H, 6, visible_h), border_radius=3)
            pygame.draw.rect(self.screen, Colors.BORDER_H,
                             (self.W - 8, bar_y, 6, bar_h), border_radius=3)

        # Message si vide
        if not self._visible:
            f = self.font("body", 16)
            t = f.render("Aucun succes dans cette categorie.", True, Colors.TEXT_MUTED)
            self.screen.blit(t, t.get_rect(
                center=(self.W // 2, HEADER_H + (self.H - HEADER_H - BOTTOM_H) // 2)))

    def _draw_bottom(self):
        bar = (0, self.H - BOTTOM_H, self.W, BOTTOM_H)
        draw_rounded_rect(self.screen, Colors.BG_PANEL, bar, 0,
                          border_color=Colors.BORDER, border_width=1, alpha=220)
        self._btn_back.draw(self.screen)

        # Compteur visible
        f  = self.font("body", 13)
        tv = f.render(f"{len(self._visible)} succes affiches", True, Colors.TEXT_MUTED)
        self.screen.blit(tv, tv.get_rect(
            center=(self.W // 2, self.H - BOTTOM_H // 2)))