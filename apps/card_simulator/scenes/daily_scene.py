"""
daily_scene.py
==============
Ecran de récompense journalière.

Fonctionnalités :
  - 7 cases disposées en ligne (Jour 1 → Jour 7)
  - Case du jour actif mise en valeur (pulsation dorée)
  - Cases réclamées grisées avec coche
  - Cases futures verrouillées
  - Streak actuel + meilleur streak
  - Compte à rebours jusqu'à la prochaine récompense
  - Animation de récompense (pluie de pièces / carte qui tombe)
"""

import pygame
import random
import time
from engine.scene_manager import BaseScene, TransitionType
from engine.ui_components  import Colors, Button, CoinDisplay, draw_rounded_rect
from daily_manager import DAILY_REWARDS, DailyRewardManager, DAY_DURATION


# ── Constantes layout ─────────────────────────────────────────────────────────
SLOT_W     = 140
SLOT_H     = 200
SLOT_GAP   = 16
SLOTS_Y    = 220     # y du haut des cases
BOTTOM_H   = 60

RARITY_LABELS = {
    "COMMUNE":    "Commune",
    "RARE":       "Rare",
    "EPIQUE":     "Epique",
    "ÉPIQUE":     "Epique",
    "LEGENDAIRE": "Legendaire",
    "LÉGENDAIRE": "Legendaire",
    "MYTHIQUE":   "Mythique",
}


def _fmt_time(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m:02d}m {s:02d}s"


# ═══════════════════════════════════════════════════════════════════════════════
# Particule de récompense (pièces / étoiles)
# ═══════════════════════════════════════════════════════════════════════════════

class RewardParticle:
    def __init__(self, x: int, y: int, is_coin: bool = True):
        self.x     = float(x)
        self.y     = float(y)
        self.vx    = random.uniform(-3, 3)
        self.vy    = random.uniform(-5, -1)
        self.life  = random.uniform(600, 1100)
        self.max_life = self.life
        self.size  = random.randint(4, 10)
        self.color = (255, 200, 50) if is_coin else (200, 150, 255)
        self.done  = False

    def update(self, dt: int):
        self.life -= dt
        if self.life <= 0:
            self.done = True
            return
        self.x  += self.vx * dt * 0.05
        self.y  += self.vy * dt * 0.05
        self.vy += 0.004 * dt  # gravité

    def draw(self, surface: pygame.Surface):
        if self.done:
            return
        alpha = int(255 * (self.life / self.max_life))
        size  = max(1, int(self.size * (self.life / self.max_life)))
        r, g, b = self.color
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (r, g, b, alpha), (size, size), size)
        surface.blit(s, (int(self.x) - size, int(self.y) - size))


# ═══════════════════════════════════════════════════════════════════════════════
# DailyScene
# ═══════════════════════════════════════════════════════════════════════════════

class DailyScene(BaseScene):

    def __init__(self, manager):
        super().__init__(manager)

        self._manager_daily = DailyRewardManager()
        self._particles: list[RewardParticle] = []
        self._claimed_this_session = False
        self._claim_anim_t = 0.0      # 0→1 animation après réclamation
        self._claimed_reward = None    # DailyReward récemment réclamé
        self._pulse_t = 0.0           # timer pulsation case active

        self._coin_display = CoinDisplay(
            (self.W - 20, 22), self.font("body", 18), self.assets
        )
        self._btn_back = Button(
            (20, self.H - BOTTOM_H + 10, 130, 40), "< Retour",
            self.font("body", 15), on_click=self._go_back
        )
        self._btn_claim = Button(
            (self.W // 2 - 120, SLOTS_Y + SLOT_H + 40, 240, 54),
            "Reclamer", self.font("title", 22),
            color=Colors.GOLD, radius=14,
            on_click=self._claim
        )

        self._compute_slots()

    # ── Calcul des positions ──────────────────────────────────────────────────

    def _compute_slots(self):
        total_w = 7 * SLOT_W + 6 * SLOT_GAP
        ox      = (self.W - total_w) // 2
        self._slot_rects = [
            pygame.Rect(ox + i * (SLOT_W + SLOT_GAP), SLOTS_Y, SLOT_W, SLOT_H)
            for i in range(7)
        ]

    # ── Logique ───────────────────────────────────────────────────────────────

    def _current_day_index(self) -> int:
        """Index (0-6) de la case correspondant au streak actuel."""
        if not self.player:
            return 0
        streak = self.player.stats.daily_current_streak
        return (streak - 1) % 7 if streak > 0 else 0

    def _slot_state(self, slot_idx: int) -> str:
        """
        Retourne l'état d'un slot :
          'claimed'  — déjà réclamé dans ce cycle
          'active'   — le jour actuel (réclamable ou non)
          'locked'   — jour futur
        """
        if not self.player:
            return 'locked'

        can_claim  = self._manager_daily.can_claim(self.player)
        curr       = self._current_day_index()
        streak     = self.player.stats.daily_current_streak

        if can_claim:
            # Peut réclamer : jours < curr sont réclamés, curr = actif, > curr = locked
            if slot_idx < curr:
                return 'claimed'
            elif slot_idx == curr:
                return 'active'
            else:
                return 'locked'
        else:
            # Déjà réclamé aujourd'hui : jours <= curr sont réclamés, > curr = locked
            if slot_idx <= curr:
                return 'claimed'
            else:
                return 'locked'

    # ── Navigation ────────────────────────────────────────────────────────────

    def _go_back(self):
        from scenes.menu_scene import MenuScene
        self.goto(MenuScene)

    # ── Réclamation ───────────────────────────────────────────────────────────

    def _claim(self):
        if not self.player:
            return
        if not self._manager_daily.can_claim(self.player):
            return

        try:
            reward = self._manager_daily.claim_reward(self.player)
            self._claimed_reward = reward
            self._claimed_this_session = True
            self._claim_anim_t = 0.0

            # Synchroniser achievements
            import database_manager as db
            db.db_update_max_coins(self.player.id, self.player.stats.max_coins_held)
            new_ach = self.player.check_achievements()
            db.db_sync_achievements(self.player.id, new_ach)
            for a in new_ach:
                self.manager.show_achievement(a)

            # Lancer les particules
            cx = self.W // 2
            cy = SLOTS_Y + SLOT_H // 2
            has_card = reward.card is not None
            for _ in range(60):
                self._particles.append(
                    RewardParticle(cx, cy, is_coin=not has_card or random.random() > 0.3)
                )

            self.assets.play("sfx_daily")

        except ValueError:
            pass

    # ── Boucle ────────────────────────────────────────────────────────────────

    def handle_events(self, events):
        for e in events:
            self._btn_back.handle_event(e)
            if self._manager_daily.can_claim(self.player) and not self._claimed_this_session:
                self._btn_claim.handle_event(e)

    def update(self, dt: int):
        self._pulse_t = (self._pulse_t + dt * 0.003) % (2 * 3.14159)

        if self._claimed_this_session:
            self._claim_anim_t = min(1.0, self._claim_anim_t + dt / 800)

        for p in self._particles:
            p.update(dt)
        self._particles = [p for p in self._particles if not p.done]

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self):
        self.screen.fill(Colors.BG_DARK)
        self._draw_header()
        self._draw_slots()
        self._draw_claim_button()
        self._draw_timer()
        self._draw_bottom()

        # Particules par-dessus tout
        for p in self._particles:
            p.draw(self.screen)

        # Animation résultat
        if self._claimed_this_session and self._claimed_reward:
            self._draw_claim_result()

        self._coin_display.draw(self.screen,
                                self.player.coins if self.player else 0)

    def _draw_header(self):
        f_title = self.font("title", 30)
        t = f_title.render("Recompense quotidienne", True, Colors.TEXT_WHITE)
        self.screen.blit(t, t.get_rect(centerx=self.W // 2, y=18))

        if not self.player:
            return

        # Streak actuel
        streak = self.player.stats.daily_current_streak
        best   = self.player.stats.daily_best_streak
        f_s    = self.font("body", 16)

        # Flamme streak
        flame_color = Colors.ORANGE if streak >= 3 else Colors.TEXT_GRAY
        ts = f_s.render(f"Streak : {streak} jour(s)", True, flame_color)
        self.screen.blit(ts, ts.get_rect(centerx=self.W // 2 - 120, y=72))

        tb = f_s.render(f"Record : {best} jour(s)", True, Colors.TEXT_MUTED)
        self.screen.blit(tb, tb.get_rect(centerx=self.W // 2 + 120, y=72))

        # Séparateur
        pygame.draw.line(self.screen, Colors.BORDER,
                         (80, 105), (self.W - 80, 105), 1)

    def _draw_slots(self):
        import math
        f_day   = self.font("body", 13)
        f_coins = self.font("body", 14)
        f_rar   = self.font("body", 11)

        for i, rect in enumerate(self._slot_rects):
            reward = DAILY_REWARDS[i]
            state  = self._slot_state(i)

            # ── Couleur de fond selon état ─────────────────────────────────
            if state == 'active':
                pulse  = (math.sin(self._pulse_t) + 1) / 2   # 0→1
                r      = int(50 + 30 * pulse)
                g      = int(40 + 20 * pulse)
                b      = int(10)
                bg     = (r, g, b)
                border = (int(255 * (0.7 + 0.3 * pulse)),
                          int(180 * (0.7 + 0.3 * pulse)), 30)
                alpha  = 240
            elif state == 'claimed':
                bg     = (20, 35, 20)
                border = (40, 120, 40)
                alpha  = 180
            else:  # locked
                bg     = (18, 20, 32)
                border = Colors.BORDER
                alpha  = 140

            draw_rounded_rect(self.screen, bg, rect, 12,
                              border_color=border, border_width=2, alpha=alpha)

            # ── Label "Jour N" ────────────────────────────────────────────
            lbl_color = (Colors.GOLD if state == 'active'
                         else Colors.GREEN if state == 'claimed'
                         else Colors.TEXT_MUTED)
            t_day = f_day.render(f"Jour {i + 1}", True, lbl_color)
            self.screen.blit(t_day, t_day.get_rect(centerx=rect.centerx, y=rect.y + 10))

            # ── Contenu ───────────────────────────────────────────────────
            if state == 'locked':
                # Cadenas
                font_lock = pygame.font.SysFont("freesansbold", 28)
                lock      = font_lock.render("X", True, (50, 55, 75))
                self.screen.blit(lock, lock.get_rect(center=rect.center))
            else:
                # Icône pièce ou carte
                mid_y = rect.y + 55
                if reward.card:
                    # Petit aperçu de la rareté (carré coloré)
                    rname = (reward.card.rarity.name
                             if hasattr(reward.card.rarity, "name")
                             else str(reward.card.rarity))
                    rc    = Colors.RARITY.get(rname, Colors.BORDER)
                    card_preview = pygame.Surface((60, 84), pygame.SRCALPHA)
                    pygame.draw.rect(card_preview, (*rc, 180),
                                     (0, 0, 60, 84), border_radius=6)
                    pygame.draw.rect(card_preview, (*rc, 255),
                                     (0, 0, 60, 84), 2, border_radius=6)
                    # Point d'interrogation si locked ou silhouette
                    fq = pygame.font.SysFont("freesansbold", 20)
                    q  = fq.render("?", True, (255, 255, 255))
                    card_preview.blit(q, q.get_rect(center=(30, 42)))
                    self.screen.blit(card_preview,
                                     (rect.centerx - 30, mid_y))
                    # Label rareté
                    rl = RARITY_LABELS.get(rname.upper(), rname)
                    tr = f_rar.render(rl, True, rc)
                    self.screen.blit(tr, tr.get_rect(
                        centerx=rect.centerx, y=mid_y + 90))
                else:
                    # Cercle doré = pièce
                    pygame.draw.circle(self.screen, Colors.GOLD,
                                       (rect.centerx, mid_y + 30), 24)
                    pygame.draw.circle(self.screen, (200, 150, 20),
                                       (rect.centerx, mid_y + 30), 24, 2)
                    font_pc = pygame.font.SysFont("freesansbold", 11)
                    pc = font_pc.render("pc", True, (40, 30, 10))
                    self.screen.blit(pc, pc.get_rect(center=(rect.centerx, mid_y + 30)))

                # Valeur pièces
                tc = f_coins.render(f"+{reward.coins}", True, Colors.GOLD)
                self.screen.blit(tc, tc.get_rect(
                    centerx=rect.centerx, y=rect.bottom - 38))

            # ── Overlay réclamé ───────────────────────────────────────────
            if state == 'claimed':
                ov = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                ov.fill((0, 0, 0, 60))
                self.screen.blit(ov, rect.topleft)
                # Coche verte
                font_check = pygame.font.SysFont("freesansbold", 22)
                check = font_check.render("OK", True, (60, 200, 80))
                self.screen.blit(check, check.get_rect(
                    center=(rect.right - 20, rect.y + 18)))

    def _draw_claim_button(self):
        can_claim = self._manager_daily.can_claim(self.player) if self.player else False

        if can_claim and not self._claimed_this_session:
            self._btn_claim.disabled = False
            self._btn_claim.color    = Colors.GOLD
            self._btn_claim.draw(self.screen)
        elif self._claimed_this_session:
            f = self.font("body", 16)
            t = f.render("Recompense reclamee aujourd'hui !", True, Colors.GREEN)
            self.screen.blit(t, t.get_rect(
                centerx=self.W // 2, y=SLOTS_Y + SLOT_H + 50))

    def _draw_timer(self):
        if not self.player:
            return
        remaining = self._manager_daily.time_until_next(self.player)
        if remaining <= 0:
            return

        f_label = self.font("body", 14)
        f_time  = self.font("title", 20)

        tl = f_label.render("Prochaine recompense dans :", True, Colors.TEXT_MUTED)
        self.screen.blit(tl, tl.get_rect(
            centerx=self.W // 2, y=SLOTS_Y + SLOT_H + 90))

        tt = f_time.render(_fmt_time(remaining), True, Colors.TEXT_GRAY)
        self.screen.blit(tt, tt.get_rect(
            centerx=self.W // 2, y=SLOTS_Y + SLOT_H + 114))

        # Barre de progression
        total  = DAY_DURATION
        elapsed = total - remaining
        ratio  = max(0.0, min(1.0, elapsed / total))
        bar_w  = 360
        bar_x  = self.W // 2 - bar_w // 2
        bar_y  = SLOTS_Y + SLOT_H + 148
        pygame.draw.rect(self.screen, Colors.BG_PANEL2,
                         (bar_x, bar_y, bar_w, 8), border_radius=4)
        if ratio > 0:
            pygame.draw.rect(self.screen, Colors.BLUE,
                             (bar_x, bar_y, int(bar_w * ratio), 8), border_radius=4)

    def _draw_claim_result(self):
        """Affiche le résumé de la récompense réclamée (fade-in)."""
        t    = self._claim_anim_t
        if t < 0.1:
            return

        alpha  = int(255 * min(1.0, (t - 0.1) / 0.4))
        reward = self._claimed_reward

        f_title = self.font("title", 22)
        f_body  = self.font("body", 16)

        # Panel flottant centré
        pw, ph = 420, 120
        px     = self.W // 2 - pw // 2
        py     = SLOTS_Y - ph - 20

        panel  = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 40, 20, int(220 * min(1.0, t))),
                         (0, 0, pw, ph), border_radius=12)
        pygame.draw.rect(panel, (*Colors.GREEN, int(200 * min(1.0, t))),
                         (0, 0, pw, ph), 2, border_radius=12)
        self.screen.blit(panel, (px, py))

        t1 = f_title.render("Recompense recue !", True, Colors.GREEN)
        t1.set_alpha(alpha)
        self.screen.blit(t1, t1.get_rect(centerx=self.W // 2, y=py + 14))

        desc = f"+{reward.coins} pc"
        if reward.card:
            rname = (reward.card.rarity.name
                     if hasattr(reward.card.rarity, "name")
                     else str(reward.card.rarity))
            rl    = RARITY_LABELS.get(rname.upper(), rname)
            desc += f"  +  carte {rl}"
        t2 = f_body.render(desc, True, Colors.GOLD)
        t2.set_alpha(alpha)
        self.screen.blit(t2, t2.get_rect(centerx=self.W // 2, y=py + 54))

        streak = self.player.stats.daily_current_streak if self.player else 1
        t3 = f_body.render(f"Streak : {streak} jour(s)", True, Colors.ORANGE)
        t3.set_alpha(alpha)
        self.screen.blit(t3, t3.get_rect(centerx=self.W // 2, y=py + 82))

    def _draw_bottom(self):
        bar = (0, self.H - BOTTOM_H, self.W, BOTTOM_H)
        draw_rounded_rect(self.screen, Colors.BG_PANEL, bar, 0,
                          border_color=Colors.BORDER, border_width=1, alpha=220)
        self._btn_back.draw(self.screen)