"""
menu_scene.py
=============
Menu principal du jeu.
Affiche le solde, les boutons de navigation vers chaque écran.
"""

import pygame
from engine.scene_manager import BaseScene, TransitionType
from engine.ui_components  import (
    Colors, Button, Panel, CoinDisplay, draw_rounded_rect
)


class MenuScene(BaseScene):

    def __init__(self, manager):
        super().__init__(manager)
        self._build_ui()

    def _build_ui(self):
        f_title = self.font("title", 28)
        f_body  = self.font("body",  20)
        cx      = self.W // 2

        # Boutons de navigation centrés
        btn_w, btn_h = 280, 58
        gap          = 18
        start_y      = 280

        self._buttons = []
        entries = [
            ("Ouvrir un coffre",  self._go_chest),
            ("Inventaire",        self._go_inventory),
            ("Shop",              self._go_shop),
            ("Fusion",            self._go_fusion),
            ("CardDex",           self._go_carddex),
            ("Recompense daily",  self._go_daily),
        ]
        for i, (label, cb) in enumerate(entries):
            y = start_y + i * (btn_h + gap)
            self._buttons.append(
                Button((cx - btn_w // 2, y, btn_w, btn_h),
                       label, f_body, on_click=cb, radius=12)
            )

        # CoinDisplay en haut à droite
        self._coins = CoinDisplay((self.W - 20, 22), self.font("body", 20),
                                  self.assets)

        # Bouton quitter (coin bas droit)
        self._btn_quit = Button(
            (self.W - 160, self.H - 60, 140, 42),
            "Quitter", self.font("body", 16),
            color=Colors.RED, on_click=self.manager.quit, radius=10
        )

    # ── Navigation ────────────────────────────────────────────────────────────
    def _go_chest(self):
        from scenes.chest_scene import ChestScene
        self.goto(ChestScene)

    def _go_inventory(self):
        from scenes.inventory_scene import InventoryScene
        self.goto(InventoryScene)

    def _go_shop(self):
        from scenes.shop_scene import ShopScene
        self.goto(ShopScene)

    def _go_fusion(self):
        from scenes.fusion_scene import FusionScene
        self.goto(FusionScene)

    def _go_carddex(self):
        from scenes.carddex_scene import CardDexScene
        self.goto(CardDexScene)

    def _go_daily(self):
        from scenes.daily_scene import DailyScene
        self.goto(DailyScene)

    # ── Boucle ────────────────────────────────────────────────────────────────
    def handle_events(self, events):
        for e in events:
            for btn in self._buttons:
                btn.handle_event(e)
            self._btn_quit.handle_event(e)

    def update(self, dt):
        pass

    def on_resume(self):
        """Mise à jour du solde quand on revient d'un sous-écran."""
        pass

    def draw(self):
        # Fond
        bg = self.assets.image("bg_menu", (self.W, self.H))
        self.screen.blit(bg, (0, 0))

        # Logo
        logo = self.assets.image("logo", (380, 120))
        self.screen.blit(logo, (self.W // 2 - 190, 80))

        # Nom du joueur
        if self.player:
            name_f = self.font("body", 16)
            name_s = name_f.render(
                f"Joueur #{self.player.id}", True, Colors.TEXT_GRAY
            )
            self.screen.blit(name_s, (self.W // 2 - name_s.get_width() // 2, 215))

        # Boutons
        for btn in self._buttons:
            btn.draw(self.screen)

        self._btn_quit.draw(self.screen)

        # Solde
        if self.player:
            self._coins.draw(self.screen, self.player.coins)
