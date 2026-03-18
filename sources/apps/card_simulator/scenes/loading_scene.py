#Projet : Card Opening Simulator
#Auteurs : Fahreddin, Thyraël, Tristan, Augustin

"""
loading_scene.py
Premier écran affiché.
Charge la DB et le joueur dans un thread séparé pendant que
la barre de progression s'anime. Redirige vers MenuScene.
"""

import pygame
import threading
from engine.scene_manager import BaseScene, TransitionType
from engine.ui_components  import Colors, ProgressBar, draw_rounded_rect


class LoadingScene(BaseScene):

    def __init__(self, manager):
        super().__init__(manager)
        self._progress  = 0.0
        self._status    = "Initialisation…"
        self._done      = False
        self._error     = None
        self._thread    = threading.Thread(target=self._load, daemon=True)

        self._bar = ProgressBar(
            rect=(self.W // 2 - 200, self.H // 2 + 50, 400, 20),
            color=Colors.BLUE
        )
        self._logo_alpha = 255
        self._logo_dir   = -1

    def on_enter(self):
        self._thread.start()
        self.assets.play_music("music_menu", volume=0.4)

    # Chargement en thread
    def _load(self):
        try:
            import database_manager as db

            self._status   = "Vérification de la base de données…"
            self._progress = 0.1

            if not db.check_db_integrity():
                self._error = "Base de données corrompue ou incomplète."
                return

            self._status   = "Chargement du joueur…"
            self._progress = 0.35
            player = db.load_player(1)
            if player is None:
                pid    = db.create_new_player("Joueur1")
                player = db.load_player(pid)
            self.manager.player = player

            self._status   = "Préchargement des illustrations…"
            self._progress = 0.6
            paths = [
                c.image_path for c in player.inventory.cards
                if hasattr(c, "image_path") and c.image_path
            ]
            self.assets.preload_card_images(paths)

            self._status   = "Prêt !"
            self._progress = 1.0
            self._done     = True

        except Exception as e:
            self._error  = str(e)
            self._status = f"Erreur : {e}"
            print(f"[LoadingScene] [X] {e}")

    # Boucle
    def handle_events(self, events):
        pass   # rien à gérer pendant le chargement

    def update(self, dt):
        self._bar.value = self._progress

        # Pulsation du logo
        self._logo_alpha += self._logo_dir * dt * 0.18
        if self._logo_alpha <= 130:
            self._logo_dir = 1
        elif self._logo_alpha >= 255:
            self._logo_dir = -1
        self._logo_alpha = max(130, min(255, int(self._logo_alpha)))

        if self._done:
            self._done = False
            from scenes.menu_scene import MenuScene
            self.goto(MenuScene, TransitionType.FADE)

    def draw(self):
        self.screen.fill(Colors.BG_DARK)

        # Logo avec pulsation
        logo = self.assets.image("logo", (420, 135))
        logo = logo.copy()
        logo.set_alpha(self._logo_alpha)
        self.screen.blit(logo,
            (self.W // 2 - logo.get_width() // 2, self.H // 2 - 130))

        # Barre de progression
        self._bar.draw(self.screen)

        # Texte de statut
        font = self.font("body", 15)
        surf = font.render(self._status, True, Colors.TEXT_GRAY)
        self.screen.blit(surf, surf.get_rect(center=(self.W // 2, self.H // 2 + 88)))

        # Erreur
        if self._error:
            ef   = self.font("body", 13)
            esurf = ef.render(f"Erreur : {self._error}", True, Colors.RED)
            self.screen.blit(esurf,
                esurf.get_rect(center=(self.W // 2, self.H // 2 + 115)))