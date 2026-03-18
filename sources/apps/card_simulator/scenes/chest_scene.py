#Projet : Card Opening Simulator
#Auteurs : Fahreddin, Thyraël, Tristan, Augustin

"""
chest_scene.py
Scène d'ouverture de coffre
"""

import pygame
import math
import threading
from engine.scene_manager import BaseScene, TransitionType
from engine.ui_components  import (
    Colors, Button, Panel, CoinDisplay, Label,
    draw_rounded_rect
)
from card import Rarity, Category, RARITY_SELL_VALUE
from chest import ChestType


# Constantes visuelles
# Importé depuis generator.py pour rester en sync
from generator import CHEST_COST

# Couleurs de flash selon type de coffre révélé
FLASH_COLORS = {
    ChestType.NORMAL: (200, 200, 255),
    ChestType.GOD:    (255, 210,  50),
    ChestType.DIVINE: (200,  80, 255),
}

# Libellés catégories
CAT_LABELS = {
    "MEME":        "MEME",
    "MOTS":        "MOTS",
    "OBJETS":      "OBJETS",
    "PERSONNAGES": "PERSO.",
    "CONCEPTS":    "CONCEPTS",
    "OMNI":        "** OMNI **",
}

# Couleurs distinctives par catégorie (fond du slot)
CAT_COLORS = {
    "MEME":        ( 15,  35,  80),   # BLEU foncé
    "MOTS":        ( 15,  65,  30),   # VERT foncé
    "OBJETS":      ( 80,  38,  10),   # ORANGE foncé
    "PERSONNAGES": ( 80,  15,  30),   # ROUGE/ROSE foncé
    "CONCEPTS":    ( 50,  15,  80),   # VIOLET foncé
    "OMNI":        ( 55,  55,  65),   # BLANC/GRIS
}

# Couleur d'accent (bordure hover + label)
CAT_ACCENT = {
    "MEME":        ( 60, 130, 255),   # BLEU vif
    "MOTS":        ( 50, 200,  80),   # VERT vif
    "OBJETS":      (255, 140,  30),   # ORANGE vif
    "PERSONNAGES": (240,  70, 100),   # ROUGE/ROSE vif
    "CONCEPTS":    (160,  80, 255),   # VIOLET vif
    "OMNI":        (230, 230, 240),   # BLANC
}

# Ordre d'affichage dans la grille (2 lignes × 3)
CATEGORIES = ["MEME", "MOTS", "OBJETS", "PERSONNAGES", "CONCEPTS", "OMNI"]

# Dimensions des slots de sélection
SLOT_W, SLOT_H = 310, 200
SLOT_GAP       = 24
GRID_COLS      = 3


# Helpers d'animation

def lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))

def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    return t * t * (3 - 2 * t)


# CardReveal — animation d'une carte qui se retourne

class CardReveal:
    """
    Anime le flip d'une carte (dos → face).
    Durée totale : FLIP_MS ms.
    États : WAITING → FLIPPING → DONE
    """
    FLIP_MS   = 500     # durée du flip
    DELAY_MS  = 120     # délai entre deux cartes

    CARD_W = 140
    CARD_H = 196

    def __init__(self, card, x: int, y: int, assets, delay_ms: int = 0):
        self.card      = card
        self.x         = x
        self.y         = y
        self.assets    = assets
        self._delay    = delay_ms
        self._elapsed  = 0
        self._flipped  = False   # dos visible jusqu'à mi-flip
        self.done      = False

        self._back_img = assets.card_back((self.CARD_W, self.CARD_H))
        self._face_img = assets.card_image(card.image_path,
                                           (self.CARD_W, self.CARD_H))
        self._scale_x  = 1.0    # 1 → 0 → 1 (effet flip)
        self._glow     = 0.0    # intensité du glow rareté au reveal

    def update(self, dt: int):
        if self.done:
            return
        self._elapsed += dt
        if self._elapsed < self._delay:
            return

        t = (self._elapsed - self._delay) / self.FLIP_MS
        if t >= 1.0:
            self._scale_x = 1.0
            self._flipped = True
            self.done     = True
            self._glow    = 1.0
            return

        # Première moitié : dos → bord (scale_x 1→0)
        # Deuxième moitié : bord → face (scale_x 0→1)
        if t < 0.5:
            self._scale_x = 1.0 - ease_in_out(t * 2)
        else:
            self._scale_x = ease_in_out((t - 0.5) * 2)
            self._flipped = True

        # Glow apparaît dans la 2ème moitié
        if t > 0.5:
            self._glow = ease_out_cubic((t - 0.5) * 2)

    def draw(self, surface: pygame.Surface):
        if self._elapsed < self._delay:
            # Carte face cachée (juste le dos)
            surface.blit(self._back_img, (self.x, self.y))
            return

        img  = self._face_img if self._flipped else self._back_img
        sw   = max(1, int(self.CARD_W * self._scale_x))
        scaled = pygame.transform.scale(img, (sw, self.CARD_H))
        blit_x = self.x + (self.CARD_W - sw) // 2
        surface.blit(scaled, (blit_x, self.y))

        # Glow rareté
        if self._glow > 0.05 and self._flipped:
            rarity_str = (self.card.rarity.name
                          if hasattr(self.card.rarity, "name")
                          else str(self.card.rarity))
            rc = Colors.RARITY.get(rarity_str, Colors.BORDER)
            glow_surf = pygame.Surface((self.CARD_W + 12, self.CARD_H + 12),
                                       pygame.SRCALPHA)
            pygame.draw.rect(glow_surf,
                             (*rc, int(80 * self._glow)),
                             (0, 0, self.CARD_W + 12, self.CARD_H + 12),
                             border_radius=8)
            surface.blit(glow_surf, (self.x - 6, self.y - 6))

    @property
    def is_waiting(self):
        return self._elapsed < self._delay


# ChestScene

class ChestScene(BaseScene):

    PHASE_SELECT  = "select"
    PHASE_OPENING = "opening"
    PHASE_REVEAL  = "reveal"

    def __init__(self, manager):
        super().__init__(manager)

        self._phase          = self.PHASE_SELECT
        self._selected_cat   = None   # catégorie choisie
        self._chest          = None   # objet Chest généré
        self._chest_type_real = None  # révélé à l'ouverture

        self._anim_frame     = 1      # frame 1→6
        self._anim_timer     = 0
        self._anim_frame_ms  = 80     # ms par frame
        self._flash_alpha    = 0      # flash blanc/coloré
        self._shake_offset   = (0, 0)
        self._shake_timer    = 0

        # Cartes reveal (phase REVEAL)
        self._card_reveals   = []
        self._reveal_done    = False
        self._recap_buttons  = []   # initialisé ici pour éviter AttributeError

        # Résultat (pour vente rapide)
        self._result_cards   = []

        self._current_cost   = 250   # coût du coffre en cours d'achat

        # Loading en thread
        self._loading        = False

        # UI
        self._coin_display   = CoinDisplay(
            (self.W - 20, 22), self.font("body", 20), self.assets
        )
        self._build_select_ui()

    # Construction UI sélection

    def _build_select_ui(self):
        """Construit la grille de sélection des coffres."""
        f_label = self.font("body", 16)
        f_price = self.font("body", 14)

        grid_w = GRID_COLS * SLOT_W + (GRID_COLS - 1) * SLOT_GAP
        ox     = (self.W - grid_w) // 2
        oy     = 160

        self._slots = []
        for i, cat in enumerate(CATEGORIES):
            col = i % GRID_COLS
            row = i // GRID_COLS
            x   = ox + col * (SLOT_W + SLOT_GAP)
            y   = oy + row * (SLOT_H + SLOT_GAP)
            self._slots.append({
                "cat":     cat,
                "rect":    pygame.Rect(x, y, SLOT_W, SLOT_H),
                "hovered": False,
                "hover_t": 0.0,
            })

        self._btn_back = Button(
            (30, 30, 130, 44), "< Retour",
            self.font("body", 17),
            on_click=self._go_back
        )

    # Navigation

    def _go_back(self):
        from scenes.menu_scene import MenuScene
        self.goto(MenuScene)

    # Gestion des événements

    def handle_events(self, events):
        for e in events:
            if self._phase == self.PHASE_SELECT:
                self._btn_back.handle_event(e)
                self._handle_select_events(e)
            elif self._phase == self.PHASE_REVEAL:
                self._handle_reveal_events(e)
                # Bouton retour toujours actif en phase reveal
                self._btn_back.handle_event(e)

    def _handle_select_events(self, e):
        if e.type == pygame.MOUSEMOTION:
            for slot in self._slots:
                slot["hovered"] = slot["rect"].collidepoint(e.pos)

        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            for slot in self._slots:
                if slot["rect"].collidepoint(e.pos):
                    self._buy_chest(slot["cat"])
                    break

    def _handle_reveal_events(self, e):
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if self._reveal_done:
                # Boutons du récap : dispatcher le clic à chaque bouton
                for btn in self._recap_buttons:
                    btn.handle_event(e)
            else:
                # Clic pendant le reveal → tout révéler instantanément
                for cr in self._card_reveals:
                    cr._elapsed  = cr._delay + CardReveal.FLIP_MS + 1
                    cr._flipped  = True
                    cr._scale_x  = 1.0
                    cr.done      = True
                # Construire les boutons immédiatement (sans attendre _update_reveal)
                self._reveal_done = True
                self._build_recap_buttons()

        elif e.type == pygame.MOUSEMOTION and self._reveal_done:
            # Propager le hover aux boutons du récap
            for btn in self._recap_buttons:
                btn.handle_event(e)

    # Achat et génération

    def _buy_chest(self, category: str):
        if not self.player:
            return
        cost = CHEST_COST.get("omni" if category == "OMNI" else "normal", 250)
        if self.player.coins < cost:
            self.manager.show_toast("Pas assez de pieces !", Colors.RED)
            return
        self._current_cost = cost   # mémorisé pour l'affichage

        self._selected_cat = category
        self._phase        = self.PHASE_OPENING
        self._anim_frame   = 1
        self._anim_timer   = 0
        self._flash_alpha  = 0
        self._shake_timer  = 200   # ms de shake


        # Générer le coffre en arrière-plan
        self._loading = True
        t = threading.Thread(target=self._generate_chest, daemon=True)
        t.start()

    def _generate_chest(self):
        """Génère le coffre dans un thread pour ne pas bloquer l'animation."""
        try:
            import database_manager as db
            from generator import generate_normal_chest, generate_omni_chest

            cat = self._selected_cat
            if cat == "OMNI":
                chest = generate_omni_chest()
            else:
                from card import Category
                cat_enum = Category[cat]
                chest = generate_normal_chest(cat_enum)

            self._chest           = chest
            self._chest_type_real = chest.type
            self._result_cards    = list(chest.cards)

            # Persistance DB
            cat_str  = cat if cat != "OMNI" else None
            chest_id = db.db_register_generated_chest(
                cat_str, chest.cost, chest.type.name, chest.cards
            )
            new_ach = self.player.buy_chest(chest)
            db.db_open_chest(self.player.id, chest_id, chest.cost, chest.cards)
            db.db_update_max_coins(self.player.id, self.player.stats.max_coins_held)
            db.db_sync_achievements(self.player.id, new_ach)
            for a in new_ach:
                self.manager.show_achievement(a)

        except Exception as ex:
            print(f"[ChestScene] [X] Erreur génération coffre : {ex}")
            self._chest = None
        finally:
            self._loading = False

    # Update

    def update(self, dt: int):
        if self._phase == self.PHASE_SELECT:
            self._update_select(dt)
        elif self._phase == self.PHASE_OPENING:
            self._update_opening(dt)
        elif self._phase == self.PHASE_REVEAL:
            self._update_reveal(dt)

    def _update_select(self, dt):
        for slot in self._slots:
            target        = 1.0 if slot["hovered"] else 0.0
            slot["hover_t"] = lerp(slot["hover_t"], target, dt / 120)

    def _update_opening(self, dt):
        # Shake
        if self._shake_timer > 0:
            self._shake_timer -= dt
            intensity = min(self._shake_timer / 200, 1.0) * 8
            import random
            self._shake_offset = (
                int(random.uniform(-intensity, intensity)),
                int(random.uniform(-intensity, intensity))
            )
        else:
            self._shake_offset = (0, 0)

        # Avancer les frames de l'animation
        self._anim_timer += dt
        if self._anim_timer >= self._anim_frame_ms:
            self._anim_timer = 0
            if self._anim_frame < 6:
                self._anim_frame += 1
                # Flash au moment de l'ouverture (frame 4)
                if self._anim_frame == 4 and self._chest_type_real:
                    self._flash_alpha = 255
                    sfx = {
                        ChestType.NORMAL: "sfx_chest_open",
                        ChestType.GOD:    "sfx_chest_open",
                        ChestType.DIVINE: "sfx_chest_open",
                    }.get(self._chest_type_real, "sfx_chest_open")
                    self.assets.play(sfx)

        # Diminuer le flash
        if self._flash_alpha > 0:
            self._flash_alpha = max(0, self._flash_alpha - dt * 1.5)

        # Passer au reveal quand l'animation est finie ET le coffre généré
        if self._anim_frame == 6 and not self._loading and self._chest:
            self._start_reveal()

    def _update_reveal(self, dt):
        all_done = True
        prev_done = [cr.done for cr in self._card_reveals]
        for cr in self._card_reveals:
            cr.update(dt)
            if not cr.done:
                all_done = False
        # Son flip pour chaque carte qui vient de se retourner
        for i, cr in enumerate(self._card_reveals):
            if cr.done and not prev_done[i]:
                rarity_val = (cr.card.rarity.value
                              if hasattr(cr.card.rarity, "value") else 0)
                self.assets.play("sfx_card_flip", 0.5)

        if all_done and not self._reveal_done:
            self._reveal_done = True
            self._build_recap_buttons()


        # les boutons n'ont pas de methode update, rien a faire ici

    # Démarrage du reveal

    def _start_reveal(self):
        self._phase       = self.PHASE_REVEAL
        self._reveal_done = False
        self._card_reveals = []

        cards = self._result_cards
        n     = len(cards)

        # Disposition : 2 rangées (5 + reste) centrées
        CW   = CardReveal.CARD_W
        CH   = CardReveal.CARD_H
        GAP  = 16
        ROW1 = min(5, n)
        ROW2 = n - ROW1

        def row_x(count, idx):
            total_w = count * CW + (count - 1) * GAP
            ox      = (self.W - total_w) // 2
            return ox + idx * (CW + GAP)

        row1_y = self.H // 2 - CH - 30
        row2_y = self.H // 2 + 30

        for i, card in enumerate(cards):
            if i < ROW1:
                x = row_x(ROW1, i)
                y = row1_y
            else:
                x = row_x(ROW2, i - ROW1)
                y = row2_y

            delay = i * (CardReveal.FLIP_MS + 80)  # séquentiel : attendre la fin du flip précédent
            cr    = CardReveal(card, x, y, self.assets, delay)
            self._card_reveals.append(cr)

            # Son pour les cartes rares+
            rarity_val = (card.rarity.value
                          if hasattr(card.rarity, "value") else 0)
            if rarity_val >= Rarity.ÉPIQUE.value:
                # Programmer le son au bon moment (approximation)
                pass

    # Boutons récapitulatif

    def _build_recap_buttons(self):
        f = self.font("body", 18)
        cy = self.H - 65

        self._recap_buttons = [
            Button((self.W // 2 - 320, cy, 200, 48),
                   "Ouvrir un autre", f,
                   color=Colors.BLUE,
                   on_click=self._open_another),
            Button((self.W // 2 - 100, cy, 200, 48),
                   "Vendre communes", f,
                   color=Colors.ORANGE,
                   on_click=self._sell_commons),
            Button((self.W // 2 + 120, cy, 200, 48),
                   "< Menu", f,
                   on_click=self._go_back),
        ]

    def _open_another(self):
        """Revenir à la sélection pour ouvrir un autre coffre."""
        self._phase        = self.PHASE_SELECT
        self._chest        = None
        self._card_reveals = []
        self._reveal_done  = False
        self._result_cards = []
        self._recap_buttons = []
        # Remettre les hovers à zéro
        for slot in self._slots:
            slot["hover_t"] = 0.0

    def _sell_commons(self):
        """Vend toutes les Communes de ce coffre directement."""
        if not self.player:
            return
        import database_manager as db
        from card import Rarity

        commons = [c for c in self._result_cards if c.rarity == Rarity.COMMUNE]
        if not commons:
            self.manager.show_toast("Aucune commune à vendre.", Colors.TEXT_GRAY)
            return

        gained = self.player.player_sell_all_by_rarity(Rarity.COMMUNE)
        db.db_sell_all_by_rarity(self.player.id, Rarity.COMMUNE,
                                 self.player.coins, commons)
        db.db_update_max_coins(self.player.id, self.player.stats.max_coins_held)
        new_ach = self.player.check_achievements()
        db.db_sync_achievements(self.player.id, new_ach)
        for a in new_ach:
            self.manager.show_achievement(a)

        self.assets.play("sfx_coin", 0.7)
        self.manager.show_toast(f"+{gained} pieces  Communes vendues", Colors.GOLD)
        # Griser les cartes communes dans le reveal
        for cr in self._card_reveals:
            if cr.card.rarity == Rarity.COMMUNE:
                cr._face_img.set_alpha(80)

    # Draw

    def draw(self):
        bg = self.assets.image("bg_chest", (self.W, self.H))
        self.screen.blit(bg, (0, 0))

        if self._phase == self.PHASE_SELECT:
            self._draw_select()
        elif self._phase == self.PHASE_OPENING:
            self._draw_opening()
        elif self._phase == self.PHASE_REVEAL:
            self._draw_reveal()

        # HUD permanent
        self._coin_display.draw(self.screen,
                                self.player.coins if self.player else 0)

    # Draw : sélection

    def _draw_select(self):
        self._btn_back.draw(self.screen)

        # Titre
        f_title = self.font("title", 36)
        t = f_title.render("Choisir un coffre", True, Colors.TEXT_WHITE)
        self.screen.blit(t, t.get_rect(center=(self.W // 2, 95)))

        # Sous-titre mystère
        f_sub = self.font("body", 14)
        sub   = f_sub.render(
            "Chaque coffre peut être Normal, God ou Divin… à vous de tenter !",
            True, Colors.TEXT_GRAY
        )
        self.screen.blit(sub, sub.get_rect(center=(self.W // 2, 130)))

        for slot in self._slots:
            self._draw_chest_slot(slot)

    def _draw_chest_slot(self, slot):
        rect   = slot["rect"]
        cat    = slot["cat"]
        ht     = slot["hover_t"]
        accent = CAT_ACCENT[cat]
        base   = CAT_COLORS[cat]

        # Élévation au hover
        draw_y = rect.y - int(ht * 8)
        draw_rect = (rect.x, draw_y, rect.w, rect.h)

        # Fond
        draw_rounded_rect(self.screen, base, draw_rect, 14,
                          border_color=accent if ht > 0.1 else Colors.BORDER,
                          border_width=2 if ht > 0.1 else 1,
                          alpha=220)

        # Coffre centré (frame 1 = fermé pour tous)
        chest_img = self.assets.chest_frame(cat, 1, (120, 120))
        cx = rect.x + (rect.w - 120) // 2
        cy = draw_y + 18
        self.screen.blit(chest_img, (cx, cy))

        # Label catégorie
        f_cat  = self.font("body", 15)
        f_price = self.font("body", 13)
        label  = CAT_LABELS[cat]

        lt = f_cat.render(label, True,
                          accent if ht > 0.3 else Colors.TEXT_WHITE)
        self.screen.blit(lt, lt.get_rect(center=(rect.x + rect.w // 2,
                                                  draw_y + 150)))

        # Prix
        slot_cost = CHEST_COST.get("omni" if cat == "OMNI" else "normal", 250)
        pt = f_price.render(f"{slot_cost} pieces", True, Colors.GOLD)
        self.screen.blit(pt, pt.get_rect(center=(rect.x + rect.w // 2,
                                                  draw_y + 172)))

        # Hover : indication "Cliquer pour ouvrir"
        if ht > 0.5:
            ht2 = f_price.render("Cliquer pour ouvrir", True, Colors.TEXT_GRAY)
            alpha_surf = ht2.copy()
            alpha_surf.set_alpha(int(200 * ht))
            self.screen.blit(alpha_surf,
                             alpha_surf.get_rect(center=(rect.x + rect.w // 2,
                                                          draw_y + rect.h - 12)))

    # Draw : ouverture

    def _draw_opening(self):
        cat = self._selected_cat

        # Coffre animé centré
        frame_img = self.assets.chest_frame(cat, self._anim_frame, (260, 260))
        ox, oy    = self._shake_offset
        cx = self.W // 2 - 130 + ox
        cy = self.H // 2 - 160 + oy
        self.screen.blit(frame_img, (cx, cy))

        # Nom catégorie
        f = self.font("title", 28)
        t = f.render(CAT_LABELS.get(cat, cat), True, Colors.TEXT_WHITE)
        self.screen.blit(t, t.get_rect(center=(self.W // 2, cy + 280)))

        # Flash coloré (révèle le type)
        if self._flash_alpha > 0 and self._chest_type_real:
            fc    = FLASH_COLORS.get(self._chest_type_real, (255, 255, 255))
            flash = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            flash.fill((*fc, int(self._flash_alpha)))
            self.screen.blit(flash, (0, 0))

            # Label du type révélé
            if self._flash_alpha > 100:
                type_labels = {
                    ChestType.NORMAL: "",
                    ChestType.GOD:    "-- COFFRE DE DIEU --",
                    ChestType.DIVINE: "** COFFRE DIVIN **",
                }
                lbl = type_labels.get(self._chest_type_real, "")
                if lbl:
                    f2 = self.font("title", 44)
                    t2 = f2.render(lbl, True, Colors.TEXT_WHITE)
                    self.screen.blit(t2, t2.get_rect(center=(self.W // 2,
                                                              self.H // 2)))

        # Chargement en cours
        if self._loading:
            f_load = self.font("body", 14)
            dots   = "." * (int(pygame.time.get_ticks() / 400) % 4)
            lt     = f_load.render(f"Generation{dots}", True, Colors.TEXT_MUTED)
            self.screen.blit(lt, lt.get_rect(center=(self.W // 2, self.H - 60)))

    # Draw : reveal

    def _draw_reveal(self):
        # Bandeau type coffre en haut
        if self._chest_type_real and self._chest_type_real != ChestType.NORMAL:
            type_labels = {
                ChestType.GOD:    "-- COFFRE DE DIEU",
                ChestType.DIVINE: "** COFFRE DIVIN **",
            }
            lbl = type_labels.get(self._chest_type_real, "")
            if lbl:
                fc = FLASH_COLORS.get(self._chest_type_real, Colors.GOLD)
                f  = self.font("title", 22)
                t  = f.render(lbl, True, fc)
                self.screen.blit(t, t.get_rect(center=(self.W // 2, 45)))

        # Cartes
        for cr in self._card_reveals:
            cr.draw(self.screen)

        # Noms des cartes révélées (en dessous de chaque carte)
        f_name = self.font("body", 11)
        for cr in self._card_reveals:
            if cr.done:
                rarity_str = (cr.card.rarity.name
                              if hasattr(cr.card.rarity, "name")
                              else str(cr.card.rarity))
                rc   = Colors.RARITY.get(rarity_str, Colors.TEXT_GRAY)
                name = cr.card.name[:16] + ("…" if len(cr.card.name) > 16 else "")
                nt   = f_name.render(name, True, rc)
                self.screen.blit(nt, nt.get_rect(
                    center=(cr.x + CardReveal.CARD_W // 2,
                             cr.y + CardReveal.CARD_H + 8)
                ))

        # Boutons récapitulatif
        if self._reveal_done:
            # Fond semi-transparent sous les boutons
            btn_bg = pygame.Surface((self.W, 70), pygame.SRCALPHA)
            btn_bg.fill((0, 0, 0, 140))
            self.screen.blit(btn_bg, (0, self.H - 75))

            for btn in self._recap_buttons:
                btn.draw(self.screen)
        else:
            # Indication "Cliquer pour tout révéler"
            f_hint = self.font("body", 13)
            hint   = f_hint.render("Clic pour tout reveler",
                                   True, Colors.TEXT_MUTED)
            self.screen.blit(hint, hint.get_rect(center=(self.W // 2, self.H - 25)))