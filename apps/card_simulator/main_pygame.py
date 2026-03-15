"""
main_pygame.py
==============
Point d'entrée Pygame du Card Simulator.

À lancer depuis n'importe où :
    python Projet-NSI-2026/apps/card_simulator/main_pygame.py
ou depuis le dossier card_simulator/ :
    python main_pygame.py
"""

import sys
import os

# ── Résolution de la racine du projet ─────────────────────────────────────────
# Ce fichier : Projet-NSI-2026/apps/card_simulator/main_pygame.py
HERE         = os.path.dirname(os.path.abspath(__file__))          # apps/card_simulator
APPS_DIR     = os.path.dirname(HERE)                                # apps
PROJECT_ROOT = os.path.dirname(APPS_DIR)                            # Projet-NSI-2026

# ── sys.path ──────────────────────────────────────────────────────────────────
for p in [
    HERE,                                    # main_pygame.py lui-même
    os.path.join(HERE, "core"),              # card.py, player.py, inventory.py...
    os.path.join(HERE, "logic"),             # generator.py, shop_system.py...
    os.path.join(HERE, "engine"),            # asset_manager, scene_manager, ui
    os.path.join(HERE, "scenes"),            # loading_scene, menu_scene...
    os.path.join(PROJECT_ROOT, "data"),      # database_manager.py + game.db
]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Vérification pygame ────────────────────────────────────────────────────────
try:
    import pygame
except ImportError:
    print("[X]  Pygame non installé. Lance : pip install pygame")
    sys.exit(1)

# ── Lancement ─────────────────────────────────────────────────────────────────
from engine.scene_manager import SceneManager
from scenes.loading_scene import LoadingScene


def main():
    manager = SceneManager(
        project_root=PROJECT_ROOT,
        fullscreen=False
    )
    manager.push(LoadingScene)
    manager.run()


if __name__ == "__main__":
    main()