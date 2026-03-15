"""
scene_manager.py
================
Moteur principal : boucle de jeu 60 FPS + pile de scènes + transitions.

Utilisation dans main_pygame.py :
    manager = SceneManager(project_root="chemin/vers/Projet-NSI-2026", fullscreen=False)
    manager.push(LoadingScene)
    manager.run()
"""

import pygame
from abc import ABC, abstractmethod
from enum import Enum, auto


# ── Transitions ────────────────────────────────────────────────────────────────

class TransitionType(Enum):
    NONE        = auto()
    FADE        = auto()
    SLIDE_LEFT  = auto()
    SLIDE_RIGHT = auto()

TRANSITION_MS = 300   # durée d'un fondu complet


class Transition:
    def __init__(self, ttype: TransitionType = TransitionType.FADE,
                 duration: int = TRANSITION_MS):
        self.type     = ttype
        self.duration = duration
        self.elapsed  = 0
        self.done     = False
        self._phase   = "out"   # "out" → écran noir → "in"
        self._overlay = None

    def start(self, screen_size: tuple):
        self.elapsed = 0
        self.done    = False
        self._phase  = "out"
        self._overlay = pygame.Surface(screen_size, pygame.SRCALPHA)

    def update(self, dt: int) -> bool:
        """Retourne True au mi-chemin → signal pour changer la scène."""
        self.elapsed += dt
        half = self.duration // 2
        if self._phase == "out" and self.elapsed >= half:
            self._phase  = "in"
            self.elapsed = 0
            return True
        if self._phase == "in" and self.elapsed >= half:
            self.done = True
        return False

    def draw(self, screen: pygame.Surface):
        if self.type == TransitionType.NONE or self.done:
            return
        half  = self.duration // 2
        alpha = int(255 * min(self.elapsed / half, 1.0))
        if self._phase == "in":
            alpha = 255 - alpha
        self._overlay.fill((0, 0, 0, alpha))
        screen.blit(self._overlay, (0, 0))


# ── Scène de base ──────────────────────────────────────────────────────────────

class BaseScene(ABC):
    """Tous les écrans héritent de cette classe."""

    def __init__(self, manager: "SceneManager"):
        self.manager = manager
        self.screen  = manager.screen
        self.assets  = manager.assets
        self.player  = manager.player

    # ── Interface obligatoire ──────────────────────────────────────────────────
    @abstractmethod
    def handle_events(self, events: list): ...

    @abstractmethod
    def update(self, dt: int): ...

    @abstractmethod
    def draw(self): ...

    # ── Hooks optionnels ───────────────────────────────────────────────────────
    def on_enter(self):  pass
    def on_exit(self):   pass
    def on_resume(self): pass

    # ── Navigation ────────────────────────────────────────────────────────────
    def goto(self, scene_cls, transition=TransitionType.FADE, **kw):
        """Remplace l'écran courant."""
        self.manager.replace(scene_cls, transition, **kw)

    def push(self, scene_cls, transition=TransitionType.FADE, **kw):
        """Empile un nouvel écran (le courant reste en mémoire)."""
        self.manager.push(scene_cls, transition, **kw)

    def pop(self, transition=TransitionType.FADE):
        """Revient à l'écran précédent."""
        self.manager.pop(transition)

    # ── Raccourcis ────────────────────────────────────────────────────────────
    @property
    def W(self) -> int: return self.screen.get_width()
    @property
    def H(self) -> int: return self.screen.get_height()

    def font(self, style="body", size=18) -> pygame.font.Font:
        return self.assets.font(style, size)

    def play(self, sfx: str, volume: float = 1.0):
        self.assets.play(sfx, volume)


# ── SceneManager ───────────────────────────────────────────────────────────────

class SceneManager:
    """Boucle principale et gestionnaire de la pile de scènes."""

    FPS    = 60
    WIDTH  = 1280
    HEIGHT = 720

    def __init__(self, project_root: str, player=None, fullscreen: bool = False):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.display.set_caption("Card Simulator")

        flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), flags)

        # Icône de fenêtre (si disponible)
        try:
            import os
            icon_path = os.path.join(project_root, "assets", "card_game", "logo.png")
            if os.path.exists(icon_path):
                icon = pygame.image.load(icon_path)
                pygame.display.set_icon(icon)
        except Exception:
            pass

        from engine.asset_manager import AssetManager
        self.assets = AssetManager(project_root)
        self.assets.load_all()

        self.player  = player
        self._stack: list[BaseScene] = []
        self._clock  = pygame.time.Clock()
        self._running = False

        # Gestion des transitions
        self._pending: tuple | None  = None
        self._transition: Transition | None = None
        self._next_scene: BaseScene | None  = None
        self._pending_action: str           = ""

        # Toasts / banners globaux (affichés par-dessus toutes les scènes)
        self._toasts  = []
        self._banners = []

    # ── API publique ──────────────────────────────────────────────────────────

    def push(self, scene_cls, transition=TransitionType.FADE, **kw):
        self._schedule("push", scene_cls, transition, kw)

    def replace(self, scene_cls, transition=TransitionType.FADE, **kw):
        self._schedule("replace", scene_cls, transition, kw)

    def pop(self, transition=TransitionType.FADE):
        self._schedule("pop", None, transition, {})

    def quit(self):
        self._running = False

    def show_toast(self, text: str, color=None):
        """Affiche une notification temporaire par-dessus toutes les scènes."""
        from engine.ui_components import Toast, Colors
        self._toasts.append(Toast(text, self.assets.font("body", 16),
                                  (self.WIDTH, self.HEIGHT),
                                  color or Colors.GREEN))

    def show_achievement(self, achievement):
        """Affiche le bandeau de succès débloqué."""
        from engine.ui_components import AchievementBanner
        self._banners.append(
            AchievementBanner(achievement,
                              self.assets.font("title", 18),
                              self.assets.font("body", 13),
                              self.WIDTH, self.assets)
        )
        self.assets.play("sfx_achievement", 0.9)

    # ── Boucle principale ─────────────────────────────────────────────────────

    def run(self):
        self._running = True
        while self._running:
            dt     = self._clock.tick(self.FPS)
            events = pygame.event.get()

            for e in events:
                if e.type == pygame.QUIT:
                    self._running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

            current = self._current

            if self._transition and not self._transition.done:
                # ── Frame de transition ────────────────────────────────────
                mid = self._transition.update(dt)
                if mid and self._next_scene is not None:
                    self._apply_pending()
                if current:
                    current.update(dt)
                    current.draw()
                self._transition.draw(self.screen)
            else:
                # ── Frame normale ──────────────────────────────────────────
                if current:
                    current.handle_events(events)
                    current.update(dt)
                    current.draw()
                if self._pending:
                    self._start_transition()

            # ── Overlays globaux (toasts, banners) ─────────────────────────
            self._update_overlays(dt)
            self._draw_overlays()

            pygame.display.flip()

        # Sauvegarde du play time avant de quitter
        if self.player and self.player.id is not None:
            try:
                import database_manager as db
                db.db_update_play_time(self.player.id,
                                       int(self._clock.get_time() / 1000))
            except Exception:
                pass

        pygame.quit()

    # ── Internals ─────────────────────────────────────────────────────────────

    def _schedule(self, action: str, scene_cls, transition, kw: dict):
        self._pending = (action, scene_cls, transition, kw)

    def _start_transition(self):
        action, scene_cls, ttype, kw = self._pending
        self._pending = None

        self._next_scene      = scene_cls(self, **kw) if scene_cls else None
        self._pending_action  = action

        if ttype == TransitionType.NONE:
            self._apply_pending()
        else:
            self._transition = Transition(ttype)
            self._transition.start(self.screen.get_size())

    def _apply_pending(self):
        action = self._pending_action
        ns     = self._next_scene
        self._next_scene = None

        if action == "push":
            if self._current: self._current.on_exit()
            self._stack.append(ns)
            ns.on_enter()
        elif action == "replace":
            if self._current:
                self._current.on_exit()
                self._stack.pop()
            self._stack.append(ns)
            ns.on_enter()
        elif action == "pop":
            if self._current:
                self._current.on_exit()
                self._stack.pop()
            if self._current:
                self._current.on_resume()

    def _update_overlays(self, dt: int):
        for t in self._toasts:
            t.update(dt)
        self._toasts  = [t for t in self._toasts  if not t.done]
        for b in self._banners:
            b.update(dt)
        self._banners = [b for b in self._banners if not b.done]

    def _draw_overlays(self):
        for t in self._toasts:
            t.draw(self.screen)
        for b in self._banners:
            b.draw(self.screen)

    @property
    def _current(self) -> BaseScene | None:
        return self._stack[-1] if self._stack else None