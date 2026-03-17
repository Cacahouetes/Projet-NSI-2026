"""
asset_manager.py
================
Charge, met en cache et distribue tous les assets du jeu.

Arborescence réelle :
  Projet-NSI-2026/
  +── assets/
  |   +── card_game/          ← placeholders UI, coffres, sons, achievements
  |   |   +── Chests/
  |   |   |   +── MEME/chest-1.png … chest-6.png
  |   |   +── achievements/
  |   |   +── sounds/
  |   |   +── *.png           ← UI placeholders
  |   +── Cards/              ← illustrations des cartes
  |   |   +── Commune/1.png
  |   |   +── [Rareté]/[id].png
  |   |   +── card_back.png
  |   +── shared/
  +── apps/card_simulator/    ← le code tourne ici
  +── data/game.db
"""

import os
import pygame
from pathlib import Path


CHEST_CATEGORIES = ["MEME", "MOTS", "OBJETS", "PERSONNAGES", "CONCEPTS", "OMNI"]
CHEST_FRAMES     = 6

RARITY_KEY_MAP = {
    "Commune":    "commune",
    "Rare":       "rare",
    "Épique":     "epique",
    "Légendaire": "legendaire",
    "Mythique":   "mythique",
    "Unique":     "unique",
    "Divine":     "divine",
}

FONT_PATHS = {
    "title": "title.ttf",
    "body":  "body.ttf",
    "mono":  "mono.ttf",
}
FONT_FALLBACK = "freesansbold"


class AssetManager:
    """
    Gestionnaire central de tous les assets.

    Paramètres du constructeur (tous résolus par main_pygame.py) :
        project_root : chemin absolu vers Projet-NSI-2026/
    """

    def __init__(self, project_root: str):
        root = Path(project_root)

        # Répertoires calculés une seule fois
        self._card_game  = root / "assets" / "card_game"   # UI + coffres + sons
        self._cards_dir  = root / "assets" / "Cards"       # illustrations de cartes
        self._shared_dir = root / "assets" / "shared"
        self._fonts_dir  = root / "assets" / "shared" / "fonts"

        self._images: dict[str, pygame.Surface] = {}
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._fonts:  dict[tuple, pygame.font.Font] = {}
        self._missing: set[str] = set()

    # ---------------------------------------------------------------------------
    # Chargement initial
    # ---------------------------------------------------------------------------

    def load_all(self):
        """Charge tous les assets. Appeler une fois après pygame.init()."""
        self._load_card_game_assets()
        self._load_chest_frames()
        self._load_sounds()
        print(f"[AssetManager] {len(self._images)} images, "
              f"{len(self._sounds)} sons chargés.")

    def _load_card_game_assets(self):
        """Charge tous les PNG de assets/card_game/ (placeholders UI + achievements)."""
        if not self._card_game.exists():
            print(f"[AssetManager] [!]  assets/card_game/ introuvable : {self._card_game}")
            return
        for path in self._card_game.rglob("*.png"):
            # Clé relative à card_game/ : "btn_play.png", "achievements/achievement_icon_first_chest.png"
            key = path.relative_to(self._card_game).as_posix()
            self._cache_image(key, path)

    def _load_chest_frames(self):
        """
        Charge les 6 frames par coffre.
        Chemin source : assets/card_game/Chests/[CAT]/chest-N.png
        Clé cache    : "Chests/MEME/chest-1"
        """
        chests_root = self._card_game / "Chests"
        if not chests_root.exists():
            print(f"[AssetManager] [!]  Chests/ introuvable : {chests_root}")
            return
        for cat in CHEST_CATEGORIES:
            for frame in range(1, CHEST_FRAMES + 1):
                path = chests_root / cat / f"chest-{frame}.png"
                key  = f"Chests/{cat}/chest-{frame}"
                self._cache_image(key, path)

    def _load_sounds(self):
        """Charge les WAV/MP3 depuis assets/card_game/sounds/"""
        sounds_dir = self._card_game / "sounds"
        if not sounds_dir.exists():
            return
        for path in sounds_dir.iterdir():
            if path.suffix.lower() in (".wav", ".mp3", ".ogg"):
                try:
                    self._sounds[path.stem] = pygame.mixer.Sound(str(path))
                except pygame.error as e:
                    print(f"[AssetManager] [!]  Son {path.name} : {e}")

    def _cache_image(self, key: str, path: Path):
        """Charge et met en cache silencieusement."""
        try:
            surf = pygame.image.load(str(path)).convert_alpha()
            self._images[key] = surf
        except (pygame.error, FileNotFoundError):
            pass

    # ---------------------------------------------------------------------------
    # Accès images
    # ---------------------------------------------------------------------------

    def image(self, key: str, size: tuple = None) -> pygame.Surface:
        """
        Récupère une image du cache par sa clé (sans extension si besoin).
        Retourne un placeholder magenta si manquante.
        """
        surf = (self._images.get(key)
                or self._images.get(key + ".png")
                or self._images.get(key.removesuffix(".png")))

        if surf is None:
            if key not in self._missing:
                print(f"[AssetManager] [!]  Manquant : '{key}'")
                self._missing.add(key)
            surf = self._make_placeholder(size or (64, 64))

        if size and surf.get_size() != size:
            surf = pygame.transform.smoothscale(surf, size)
        return surf

    def card_image(self, image_path: str, size: tuple = None) -> pygame.Surface:
        """
        Charge l'illustration d'une carte depuis son image_path DB.
        image_path : "Cards/Commune/1.png"  (tel que stocké en DB)
        Résolu vers : Projet-NSI-2026/assets/Cards/Commune/1.png
        """
        key = image_path.replace("\\", "/")

        if key in self._images:
            surf = self._images[key]
        else:
            # image_path commence par "Cards/" — chercher dans assets/
            full_path = self._cards_dir.parent / key   # assets/ + Cards/Commune/1.png
            if full_path.exists():
                self._cache_image(key, full_path)
                surf = self._images.get(key)
            else:
                surf = None

            if surf is None:
                if key not in self._missing:
                    print(f"[AssetManager] [!]  Carte manquante : '{key}'")
                    self._missing.add(key)
                surf = self._make_placeholder(size or (300, 420))

        if size and surf.get_size() != size:
            surf = pygame.transform.smoothscale(surf, size)
        return surf

    def card_back(self, size: tuple = None) -> pygame.Surface:
        """Dos de carte : assets/Cards/card_back.png"""
        key = "card_back"
        if key not in self._images:
            path = self._cards_dir / "card_back.png"
            self._cache_image(key, path)
        return self.image(key, size)

    def chest_frame(self, category: str, frame: int,
                    size: tuple = None) -> pygame.Surface:
        """
        Frame N (1–6) d'un coffre.
        category : "MEME" | "MOTS" | "OBJETS" | "PERSONNAGES" | "CONCEPTS" | "OMNI"
        """
        frame = max(1, min(frame, CHEST_FRAMES))
        return self.image(f"Chests/{category}/chest-{frame}", size)

    def card_frame(self, rarity_name: str, size: tuple = None) -> pygame.Surface:
        key = f"cards/card_frame_{RARITY_KEY_MAP.get(rarity_name, rarity_name.lower())}"
        return self.image(key, size)

    def rarity_badge(self, rarity_name: str, size: tuple = None) -> pygame.Surface:
        key = f"cards/card_rarity_badge_{RARITY_KEY_MAP.get(rarity_name, rarity_name.lower())}"
        return self.image(key, size)

    def category_icon(self, category: str, size: tuple = None) -> pygame.Surface:
        return self.image(f"cards/category_icon_{category.lower()}", size)

    def achievement_icon(self, ach_id: str, size: tuple = None) -> pygame.Surface:
        return self.image(f"achievements/achievement_icon_{ach_id}", size)

    def preload_card_images(self, image_paths: list):
        """Précharge une liste d'image_path (après load_player)."""
        for p in image_paths:
            self.card_image(p)

    # ---------------------------------------------------------------------------
    # Sons
    # ---------------------------------------------------------------------------

    def sound(self, key: str):
        sfx = self._sounds.get(key)
        if sfx is None and key not in self._missing:
            print(f"[AssetManager] [!]  Son manquant : '{key}'")
            self._missing.add(key)
        return sfx

    def play(self, key: str, volume: float = 1.0):
        sfx = self.sound(key)
        if sfx:
            sfx.set_volume(volume)
            sfx.play()

    def play_music(self, key: str, volume: float = 0.6, loops: int = -1):
        for ext in (".mp3", ".ogg", ".wav"):
            path = self._card_game / "sounds" / (key + ext)
            if path.exists():
                pygame.mixer.music.load(str(path))
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loops)
                return
        print(f"[AssetManager] [!]  Musique manquante : '{key}'")

    def stop_music(self, fadeout_ms: int = 500):
        pygame.mixer.music.fadeout(fadeout_ms)

    # ---------------------------------------------------------------------------
    # Polices
    # ---------------------------------------------------------------------------

    def font(self, style: str = "body", size: int = 18) -> pygame.font.Font:
        key = (style, size)
        if key in self._fonts:
            return self._fonts[key]
        fname = FONT_PATHS.get(style, "")
        path  = self._fonts_dir / fname if fname else None
        f = None
        if path and path.exists():
            try:
                f = pygame.font.Font(str(path), size)
            except pygame.error:
                pass
        if f is None:
            f = pygame.font.SysFont(FONT_FALLBACK, size)
        self._fonts[key] = f
        return f

    # ---------------------------------------------------------------------------
    # Utilitaires
    # ---------------------------------------------------------------------------

    def _make_placeholder(self, size: tuple) -> pygame.Surface:
        w, h = size
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((255, 0, 255, 150))
        pygame.draw.line(surf, (0, 0, 0), (0, 0), (w - 1, h - 1), 2)
        pygame.draw.line(surf, (0, 0, 0), (w - 1, 0), (0, h - 1), 2)
        return surf

    @property
    def loaded_count(self) -> int:
        return len(self._images)