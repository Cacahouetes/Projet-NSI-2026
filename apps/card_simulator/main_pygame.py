"""
apps/card_simulator/main_pygame.py — CORRIGÉ
Passe project_root à SceneManager. Échap depuis MenuScene = retour launcher.
"""
import pygame
import sys
import os

HERE         = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

# Chemins Python
sys.path.insert(0, os.path.join(HERE, 'core'))
sys.path.insert(0, os.path.join(HERE, 'logic'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'data'))

from engine.scene_manager import SceneManager
from scenes.loading_scene import LoadingScene


def main():
    manager = SceneManager(project_root=PROJECT_ROOT)

    # On remplace manager.run() pour injecter la gestion Échap
    def patched_run():
        manager._running = True
        clock = manager._clock
        session_ms = 0

        while manager._running:
            dt = clock.tick(manager.FPS)
            session_ms += dt
            events = pygame.event.get()

            for e in events:
                if e.type == pygame.QUIT:
                    manager._running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                # Échap depuis le menu principal → ferme le jeu (retour launcher)
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    from scenes.menu_scene import MenuScene
                    if isinstance(manager._current, MenuScene):
                        manager._running = False

            current = manager._current

            if manager._transition and not manager._transition.done:
                mid = manager._transition.update(dt)
                if mid and manager._next_scene is not None:
                    manager._apply_pending()
                if current:
                    current.update(dt)
                    current.draw()
                manager._transition.draw(manager.screen)
            else:
                if current:
                    current.handle_events(events)
                    current.update(dt)
                    current.draw()
                if manager._pending:
                    manager._start_transition()

            manager._update_overlays(dt)
            manager._draw_overlays()
            pygame.display.flip()

        # Sauvegarde du play time
        if manager.player and manager.player.id is not None:
            try:
                import database_manager as db
                db.db_update_play_time(manager.player.id, session_ms // 1000)
            except Exception:
                pass

        pygame.quit()
        sys.exit(0)   # retour propre → le launcher reprend

    manager.run = patched_run
    manager.push(LoadingScene)
    manager.run()


if __name__ == "__main__":
    main()