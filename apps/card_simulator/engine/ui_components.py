"""
ui_components.py
================
Composants UI réutilisables dans toutes les scènes.

Button, Panel, Label, CoinDisplay, ProgressBar,
ScrollView, Toast, AchievementBanner, CardWidget
"""

import pygame
from typing import Callable


# ── Palette globale ────────────────────────────────────────────────────────────
class Colors:
    BG_DARK     = ( 10,  12,  25)
    BG_PANEL    = ( 22,  26,  44)
    BG_PANEL2   = ( 30,  35,  58)
    TEXT_WHITE  = (240, 240, 245)
    TEXT_GRAY   = (140, 150, 170)
    TEXT_MUTED  = ( 80,  90, 110)
    GOLD        = (255, 195,  50)
    BLUE        = ( 65, 125, 220)
    BLUE_LIGHT  = ( 90, 155, 255)
    GREEN       = ( 50, 195,  90)
    RED         = (200,  55,  55)
    PURPLE      = (130,  60, 210)
    ORANGE      = (220, 110,  40)
    BORDER      = ( 50,  60,  90)
    BORDER_H    = ( 90, 120, 180)   # hover

    RARITY = {
        "Commune":    (130, 130, 138),
        "Rare":       ( 50, 100, 210),
        "Épique":     (150,  50, 210),
        "Légendaire": (210, 150,  20),
        "Mythique":   (210,  40,  40),
        "Unique":     ( 20, 180, 180),
        "Divine":     (240, 200,  50),
    }


def draw_rounded_rect(surface, color, rect, radius=10,
                      border_color=None, border_width=0, alpha=255):
    """Rectangle arrondi avec alpha optionnel."""
    x, y, w, h = rect
    r = min(radius, w // 2, h // 2)
    if alpha < 255:
        tmp = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(tmp, (*color[:3], alpha), (0, 0, w, h), border_radius=r)
        if border_color and border_width:
            pygame.draw.rect(tmp, (*border_color[:3], alpha),
                             (0, 0, w, h), border_width, border_radius=r)
        surface.blit(tmp, (x, y))
    else:
        pygame.draw.rect(surface, color[:3], rect, border_radius=r)
        if border_color and border_width:
            pygame.draw.rect(surface, border_color[:3], rect,
                             border_width, border_radius=r)


# -------------------------------------------------------------------------------
# Button
# -------------------------------------------------------------------------------

class Button:
    def __init__(self, rect, text: str, font: pygame.font.Font,
                 color=None, hover_color=None, text_color=None,
                 disabled=False, on_click: Callable = None,
                 icon: pygame.Surface = None, radius=10):
        self.rect        = pygame.Rect(rect)
        self.text        = text
        self.font        = font
        self.color       = color       or Colors.BLUE
        self.hover_color = hover_color or Colors.BLUE_LIGHT
        self.text_color  = text_color  or Colors.TEXT_WHITE
        self.disabled    = disabled
        self.on_click    = on_click
        self.icon        = icon
        self.radius      = radius
        self._hovered    = False
        self._pressed    = False
        self._scale      = 1.0

    def handle_event(self, event) -> bool:
        if self.disabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._pressed = True
                self._scale   = 0.95
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed   = self._pressed
            self._pressed = False
            self._scale   = 1.0
            # Déclencher si le bouton est relâché sur le rect,
            # que _pressed soit True ou non (gère le cas où le bouton
            # vient d'être créé sans avoir reçu le BUTTONDOWN)
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface):
        color = (Colors.BG_PANEL2 if self.disabled
                 else self.hover_color if self._hovered
                 else self.color)
        rect = self.rect
        if self._scale != 1.0:
            cx, cy = rect.center
            nw, nh = int(rect.w * self._scale), int(rect.h * self._scale)
            rect   = pygame.Rect(cx - nw // 2, cy - nh // 2, nw, nh)

        bc = Colors.BORDER if self.disabled else Colors.BORDER_H
        draw_rounded_rect(surface, color, rect, self.radius, bc, 1)

        txt  = self.font.render(self.text, True,
                                Colors.TEXT_MUTED if self.disabled else self.text_color)
        trct = txt.get_rect(center=rect.center)
        if self.icon:
            iw   = self.icon.get_width()
            tw   = iw + 8 + txt.get_width()
            ix   = rect.centerx - tw // 2
            iy   = rect.centery - self.icon.get_height() // 2
            surface.blit(self.icon, (ix, iy))
            trct.left = ix + iw + 8
        surface.blit(txt, trct)


# -------------------------------------------------------------------------------
# Panel
# -------------------------------------------------------------------------------

class Panel:
    def __init__(self, rect, color=None, border_color=None,
                 alpha=220, radius=12):
        self.rect   = pygame.Rect(rect)
        self.color  = color        or Colors.BG_PANEL
        self.border = border_color or Colors.BORDER
        self.alpha  = alpha
        self.radius = radius

    def draw(self, surface):
        draw_rounded_rect(surface, self.color, self.rect, self.radius,
                          self.border, 1, self.alpha)


# -------------------------------------------------------------------------------
# Label
# -------------------------------------------------------------------------------

class Label:
    def __init__(self, pos, text: str, font: pygame.font.Font,
                 color=None, anchor="topleft"):
        self.pos    = pos
        self.text   = text
        self.font   = font
        self.color  = color or Colors.TEXT_WHITE
        self.anchor = anchor

    def draw(self, surface):
        surf = self.font.render(self.text, True, self.color)
        rect = surf.get_rect(**{self.anchor: self.pos})
        surface.blit(surf, rect)


# -------------------------------------------------------------------------------
# CoinDisplay
# -------------------------------------------------------------------------------

class CoinDisplay:
    def __init__(self, pos, font: pygame.font.Font, assets):
        self.pos   = pos
        self.font  = font
        self._icon = assets.image("icon_coin", (28, 28))

    def draw(self, surface, coins: int):
        text = f"{coins:,}".replace(",", " ")
        surf = self.font.render(text, True, Colors.GOLD)
        tw   = self._icon.get_width() + 6 + surf.get_width()
        x    = self.pos[0] - tw
        y    = self.pos[1]
        surface.blit(self._icon, (x, y + 2))
        surface.blit(surf, (x + self._icon.get_width() + 6, y))


# -------------------------------------------------------------------------------
# ProgressBar
# -------------------------------------------------------------------------------

class ProgressBar:
    def __init__(self, rect, value=0.0, color=None, bg_color=None,
                 radius=6, show_text=False, font=None):
        self.rect      = pygame.Rect(rect)
        self.value     = max(0.0, min(1.0, value))
        self.color     = color    or Colors.GREEN
        self.bg_color  = bg_color or Colors.BG_PANEL2
        self.radius    = radius
        self.show_text = show_text
        self.font      = font

    def draw(self, surface):
        draw_rounded_rect(surface, self.bg_color, self.rect, self.radius,
                          Colors.BORDER, 1)
        fw = max(0, int(self.rect.w * self.value) - 2)
        if fw > 0:
            draw_rounded_rect(surface, self.color,
                              (self.rect.x + 1, self.rect.y + 1,
                               fw, self.rect.h - 2),
                              max(1, self.radius - 1))
        if self.show_text and self.font:
            t = self.font.render(f"{int(self.value * 100)} %", True, Colors.TEXT_WHITE)
            surface.blit(t, t.get_rect(center=self.rect.center))


# -------------------------------------------------------------------------------
# ScrollView
# -------------------------------------------------------------------------------

class ScrollView:
    """Zone scrollable. Dessiner le contenu sur .surface, puis appeler .draw()."""

    def __init__(self, rect, content_height: int):
        self.rect           = pygame.Rect(rect)
        self.content_height = max(content_height, rect[3])
        self._scroll_y      = 0
        self._surface       = pygame.Surface(
            (rect[2], self.content_height), pygame.SRCALPHA
        )

    @property
    def surface(self) -> pygame.Surface:
        self._surface.fill((0, 0, 0, 0))
        return self._surface

    def handle_event(self, event):
        if not self.rect.collidepoint(pygame.mouse.get_pos()):
            return
        if event.type == pygame.MOUSEWHEEL:
            self._scroll_y = max(0, min(
                self._scroll_y - event.y * 30,
                self.content_height - self.rect.h
            ))

    def draw(self, target):
        visible = pygame.Rect(0, self._scroll_y, self.rect.w, self.rect.h)
        target.blit(self._surface, self.rect.topleft, visible)
        if self.content_height > self.rect.h:
            ratio  = self.rect.h / self.content_height
            bar_h  = max(30, int(self.rect.h * ratio))
            bar_y  = self.rect.y + int(
                (self._scroll_y / max(1, self.content_height - self.rect.h))
                * (self.rect.h - bar_h)
            )
            pygame.draw.rect(target, Colors.BORDER,
                             (self.rect.right - 6, bar_y, 4, bar_h),
                             border_radius=2)

    def scroll_to_top(self):
        self._scroll_y = 0

    @property
    def scroll_y(self) -> int:
        return self._scroll_y


# -------------------------------------------------------------------------------
# Toast
# -------------------------------------------------------------------------------

class Toast:
    DURATION = 2500
    FADE_MS  = 400

    def __init__(self, text: str, font: pygame.font.Font,
                 screen_size, color=None):
        self.done       = False
        self._elapsed   = 0
        self._color     = color or Colors.GREEN
        self._sw, self._sh = screen_size
        surf            = font.render(text, True, Colors.TEXT_WHITE)
        pad             = 20
        self._w         = surf.get_width() + pad * 2
        self._h         = surf.get_height() + pad
        self._surf      = surf

    def update(self, dt):
        self._elapsed += dt
        if self._elapsed >= self.DURATION:
            self.done = True

    def draw(self, surface):
        if self.done:
            return
        alpha = 255
        if self._elapsed < self.FADE_MS:
            alpha = int(255 * self._elapsed / self.FADE_MS)
        elif self._elapsed > self.DURATION - self.FADE_MS:
            alpha = int(255 * (self.DURATION - self._elapsed) / self.FADE_MS)

        x   = (self._sw - self._w) // 2
        y   = self._sh - 120
        tmp = pygame.Surface((self._w, self._h), pygame.SRCALPHA)
        r, g, b = self._color[:3]
        pygame.draw.rect(tmp, (r, g, b, int(alpha * 0.85)),
                         (0, 0, self._w, self._h), border_radius=10)
        pygame.draw.rect(tmp, (80, 90, 110, alpha),
                         (0, 0, self._w, self._h), 1, border_radius=10)
        ts = self._surf.copy()
        ts.set_alpha(alpha)
        tmp.blit(ts, (20, (self._h - ts.get_height()) // 2))
        surface.blit(tmp, (x, y))


# -------------------------------------------------------------------------------
# AchievementBanner
# -------------------------------------------------------------------------------

class AchievementBanner:
    SLIDE_MS = 400
    HOLD_MS  = 2200

    def __init__(self, achievement, font_title, font_body,
                 screen_w: int, assets):
        self._ach      = achievement
        self._ft       = font_title
        self._fb       = font_body
        self._sw       = screen_w
        self._elapsed  = 0
        self.done      = False
        self._h        = 80
        self._y        = -self._h
        self._total    = self.SLIDE_MS * 2 + self.HOLD_MS
        try:
            self._icon = assets.achievement_icon(achievement.id, (48, 48))
        except Exception:
            self._icon = None

    def update(self, dt):
        self._elapsed += dt
        s, h = self.SLIDE_MS, self.HOLD_MS
        if self._elapsed < s:
            self._y = int(-self._h + (self._h + 10) * self._elapsed / s)
        elif self._elapsed < s + h:
            self._y = 10
        elif self._elapsed < self._total:
            self._y = int(10 - (self._h + 10) * (self._elapsed - s - h) / s)
        else:
            self.done = True

    def draw(self, surface):
        if self.done:
            return
        bw = 500
        bx = (self._sw - bw) // 2
        draw_rounded_rect(surface, (28, 32, 20),
                          (bx, self._y, bw, self._h), 10,
                          (180, 140, 40), 2, 230)
        if self._icon:
            surface.blit(self._icon, (bx + 14, self._y + 16))
        ox = bx + 70 if self._icon else bx + 16
        t1 = self._ft.render("SUCCES DEBLOQUE !", True, (255, 195, 50))
        t2 = self._fb.render(
            f"{self._ach.name} — {self._ach.description}", True, (210, 215, 225)
        )
        surface.blit(t1, (ox, self._y + 8))
        surface.blit(t2, (ox, self._y + 38))


# -------------------------------------------------------------------------------
# CardWidget
# -------------------------------------------------------------------------------

class CardWidget:
    """Mini-carte dans une grille (inventaire, carddex)."""

    SIZE = (110, 154)

    def __init__(self, card, pos, assets,
                 quantity=1, discovered=True, on_click: Callable = None):
        self.card       = card
        self.rect       = pygame.Rect(pos, self.SIZE)
        self.assets     = assets
        self.quantity   = quantity
        self.discovered = discovered
        self.on_click   = on_click
        self._hovered   = False
        self._hover_t   = 0.0

    def handle_event(self, event, offset=(0, 0)) -> bool:
        ox, oy = offset
        adj = pygame.Rect(self.rect.x - ox, self.rect.y - oy,
                          self.rect.w, self.rect.h)
        if event.type == pygame.MOUSEMOTION:
            self._hovered = adj.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if adj.collidepoint(event.pos):
                if self.on_click:
                    self.on_click(self.card)
                return True
        return False

    def update(self, dt):
        target = 1.0 if self._hovered else 0.0
        speed  = dt / 150
        self._hover_t = (min(self._hover_t + speed, 1.0)
                         if self._hovered
                         else max(self._hover_t - speed, 0.0))

    def draw(self, surface, offset=(0, 0)):
        ox, oy = offset
        x = self.rect.x - ox
        y = self.rect.y - oy - int(self._hover_t * 6)
        w, h = self.SIZE

        if not self.discovered:
            sil = self.assets.image("card_silhouette", self.SIZE)
            surface.blit(sil, (x, y))
            return

        img = self.assets.card_image(self.card.image_path, self.SIZE)
        surface.blit(img, (x, y))

        # Bordure de rareté
        rarity_str = (self.card.rarity.name
                      if hasattr(self.card.rarity, "name")
                      else str(self.card.rarity))
        rc = Colors.RARITY.get(rarity_str, Colors.BORDER)
        pygame.draw.rect(surface, rc, (x, y, w, h), 2, border_radius=6)

        # Badge quantité
        if self.quantity > 1:
            badge = pygame.Surface((36, 22), pygame.SRCALPHA)
            pygame.draw.rect(badge, (*Colors.RED, 210),
                             (0, 0, 36, 22), border_radius=6)
            surface.blit(badge, (x + w - 38, y + h - 24))

        # Glow au hover
        if self._hover_t > 0.05:
            glow = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*rc, int(40 * self._hover_t)),
                             (0, 0, w, h), border_radius=6)
            surface.blit(glow, (x, y))