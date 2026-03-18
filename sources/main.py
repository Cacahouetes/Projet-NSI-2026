#Projet : Card Opening Simulator
#Auteurs : Fafa, Thyraël, Tristan, Augustin

"""
main.py
Lance Card Simulator, Arcade Game et WebStats.
Inclut un reset de sauvegarde avec popup de confirmation.
"""

import pygame
import subprocess
import sys
import os
import webbrowser
import time
import sqlite3

# Chemins
HERE        = os.path.dirname(os.path.abspath(__file__))
CARD_MAIN   = os.path.join(HERE, *["apps", "card_simulator", "main_pygame.py"])
ARCADE_MAIN = os.path.join(HERE, *["apps", "arcade_game",    "main.py"])
SERVER_PY   = os.path.join(HERE, "server.py")
DB_PATH     = os.path.join(HERE, *["data", "game.db"])
SERVER_URL  = "http://localhost:5000"

# Palette
BG      = (14,  16,  28)
PANEL   = (22,  26,  44)
BORDER  = (45,  50,  80)
TEXT_W  = (230, 232, 245)
TEXT_M  = (130, 135, 165)
TEXT_D  = (70,  75,  105)
GOLD    = (220, 175,  50)
BLUE    = (60,  130, 255)
GREEN   = (55,  190,  80)
RED     = (200,  60,  60)
ORANGE  = (220, 110,  40)
OVERLAY = (0,     0,   0, 180)

W, H = 800, 520


# DB helpers

def _db_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def db_get_save_info() -> dict | None:
    """Résumé de la sauvegarde du premier joueur actif."""
    try:
        conn = _db_connect()
        cur  = conn.cursor()
        cur.execute("SELECT player_id, username, created_at FROM PLAYERS ORDER BY player_id LIMIT 1")
        row = cur.fetchone()
        if not row:
            conn.close()
            return None
        pid = row["player_id"]
        cur.execute("SELECT coins, coins_earned, chests_opened FROM PLAYER_STATS WHERE player_id=?", (pid,))
        stats = cur.fetchone()
        cur.execute("SELECT COUNT(*) FROM PLAYER_CARDS   WHERE player_id=?", (pid,))
        cards = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM PLAYER_CARDDEX WHERE player_id=?", (pid,))
        carddex = cur.fetchone()[0]
        coins_earned = stats["coins_earned"] if stats else 0
        chests       = stats["chests_opened"] if stats else 0
        conn.close()
        return {
            "player_id":  pid,
            "username":   row["username"],
            "created_at": row["created_at"],
            "coins":      stats["coins"] if stats else 0,
            "cards":      cards,
            "carddex":    carddex,
            "chests":     chests,
            "is_empty":   (cards == 0 and coins_earned == 0 and chests == 0),
        }
    except Exception as e:
        print(f"[db_get_save_info] {e}")
        return None


def db_reset_player(player_id: int) -> bool:
    """Reset complet de la progression du joueur."""
    try:
        conn = _db_connect()
        cur  = conn.cursor()
        cur.execute("SELECT 1 FROM PLAYERS WHERE player_id=?", (player_id,))
        if not cur.fetchone():
            conn.close()
            return False
        with conn:
            for table in ["PLAYER_CARDS", "PLAYER_CARDDEX", "PLAYER_ACHIEVEMENTS",
                          "PLAYER_FUSIONS", "PLAYER_RARITY_STATS",
                          "CHEST_OPENINGS", "DAILY_HISTORY", "SHOP_HISTORY"]:
                cur.execute(f"DELETE FROM {table} WHERE player_id=?", (player_id,))
            cur.execute("""DELETE FROM PLAYER_FUSIONS_CARDS
                           WHERE fusion_id NOT IN (SELECT fusion_id FROM PLAYER_FUSIONS)""")
            cur.execute("""
                UPDATE PLAYER_STATS SET
                    last_daily_timestamp=0, daily_current_streak=0,
                    daily_best_streak=0,    daily_streak_breaks=0,
                    coins=0,                coins_earned=0,
                    coins_spent=0,          max_coins_held=0,
                    play_time_seconds=0
                WHERE player_id=?
            """, (player_id,))
        conn.close()
        return True
    except Exception as e:
        print(f"[db_reset_player] {e}")
        return False


# Serveur Flask

_server_proc = None

def server_start():
    global _server_proc
    if _server_proc and _server_proc.poll() is None:
        return
    _server_proc = subprocess.Popen(
        [sys.executable, SERVER_PY], cwd=HERE,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    webbrowser.open(SERVER_URL)

def server_stop():
    global _server_proc
    if _server_proc and _server_proc.poll() is None:
        _server_proc.terminate()
        try:    _server_proc.wait(timeout=3)
        except: _server_proc.kill()
    _server_proc = None

def server_running():
    return _server_proc is not None and _server_proc.poll() is None


# UI helpers

def draw_rrect(surf, color, rect, r=12, border=None, bw=1, alpha=255):
    x, y, w, h = rect
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), (0, 0, w, h), border_radius=r)
    if border:
        pygame.draw.rect(s, (*border, min(alpha + 40, 255)), (0, 0, w, h), bw, border_radius=r)
    surf.blit(s, (x, y))


class Button:
    def __init__(self, rect, label, font, color=BLUE, radius=12, on_click=None):
        self.rect     = pygame.Rect(rect)
        self.label    = label
        self.font     = font
        self.color    = color
        self.radius   = radius
        self.on_click = on_click
        self._hover   = False

    def handle_event(self, e):
        if e.type == pygame.MOUSEMOTION:
            self._hover = self.rect.collidepoint(e.pos)
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if self.rect.collidepoint(e.pos) and self.on_click:
                self.on_click()
                return True
        return False

    def draw(self, surf):
        c = tuple(min(v + 28, 255) for v in self.color) if self._hover else self.color
        draw_rrect(surf, c, self.rect, self.radius, BORDER, 1)
        t = self.font.render(self.label, True, TEXT_W)
        surf.blit(t, t.get_rect(center=self.rect.center))


# Popup reset

class ResetPopup:
    PW, PH = 460, 290

    def __init__(self, fonts):
        self.f_title = fonts["title"]
        self.f_body  = fonts["body"]
        self.f_small = fonts["small"]
        self.visible = False
        self.state   = "confirm"   # 'confirm' | 'empty' | 'done'
        self._save   = None
        self._timer  = 0

        px = (W - self.PW) // 2
        py = (H - self.PH) // 2

        self._btn_confirm = Button(
            (px + 24, py + self.PH - 62, 180, 42),
            "Confirmer", fonts["body"], color=RED)
        self._btn_cancel = Button(
            (px + self.PW - 204, py + self.PH - 62, 180, 42),
            "Annuler", fonts["body"], color=(50, 55, 85))
        self._btn_ok = Button(
            (px + self.PW // 2 - 75, py + self.PH - 62, 150, 42),
            "OK", fonts["body"], color=BLUE)

        self._btn_confirm.on_click = self._do_reset
        self._btn_cancel.on_click  = self.close
        self._btn_ok.on_click      = self.close

    def open(self):
        self._save = db_get_save_info()
        if self._save is None or self._save["is_empty"]:
            self.state = "empty"
        else:
            self.state = "confirm"
        self.visible = True
        self._timer  = 0

    def close(self):
        self.visible = False

    def _do_reset(self):
        if self._save:
            ok = db_reset_player(self._save["player_id"])
            self.state = "done" if ok else "empty"
            self._timer = 0

    def handle_event(self, e):
        if not self.visible:
            return
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.close()
            return
        if self.state == "confirm":
            self._btn_confirm.handle_event(e)
            self._btn_cancel.handle_event(e)
        else:
            self._btn_ok.handle_event(e)

    def update(self, dt):
        if self.state == "done":
            self._timer += dt
            if self._timer > 2200:
                self.close()

    def draw(self, surf):
        if not self.visible:
            return
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        surf.blit(overlay, (0, 0))

        px = (W - self.PW) // 2
        py = (H - self.PH) // 2
        draw_rrect(surf, PANEL, (px, py, self.PW, self.PH), r=16, border=BORDER, bw=2)

        if   self.state == "confirm": self._draw_confirm(surf, px, py)
        elif self.state == "empty":   self._draw_empty(surf, px, py)
        elif self.state == "done":    self._draw_done(surf, px, py)

    def _draw_confirm(self, surf, px, py):
        s = self._save
        t = self.f_title.render("Effacer la sauvegarde ?", True, RED)
        surf.blit(t, t.get_rect(centerx=px + self.PW // 2, y=py + 16))
        pygame.draw.line(surf, BORDER, (px + 18, py + 48), (px + self.PW - 18, py + 48), 1)

        import time as _t
        created = _t.strftime("%d/%m/%Y", _t.localtime(s["created_at"])) if s["created_at"] else "?"
        lines = [
            f"Joueur   :  {s['username']}   (compte créé le {created})",
            f"Pièces   :  {s['coins']}",
            f"Cartes   :  {s['cards']}  —  CardDex : {s['carddex']} / 756",
            f"Coffres  :  {s['chests']}",
        ]
        for i, line in enumerate(lines):
            c = TEXT_M if i > 0 else TEXT_W
            surf.blit(self.f_body.render(line, True, c), (px + 24, py + 60 + i * 24))

        warn = self.f_small.render("Cette action est irréversible — le compte reste créé.", True, (210, 80, 80))
        surf.blit(warn, warn.get_rect(centerx=px + self.PW // 2, y=py + 172))

        pygame.draw.line(surf, BORDER, (px + 18, py + 198), (px + self.PW - 18, py + 198), 1)
        self._btn_confirm.draw(surf)
        self._btn_cancel.draw(surf)

    def _draw_empty(self, surf, px, py):
        t1 = self.f_title.render("Rien à effacer", True, TEXT_W)
        surf.blit(t1, t1.get_rect(centerx=px + self.PW // 2, y=py + 80))
        t2 = self.f_body.render("La sauvegarde est déjà vide.", True, TEXT_M)
        surf.blit(t2, t2.get_rect(centerx=px + self.PW // 2, y=py + 125))
        self._btn_ok.draw(surf)

    def _draw_done(self, surf, px, py):
        t1 = self.f_title.render("Sauvegarde effacée !", True, GREEN)
        surf.blit(t1, t1.get_rect(centerx=px + self.PW // 2, y=py + 75))
        t2 = self.f_body.render("Prêt pour une nouvelle partie.", True, TEXT_M)
        surf.blit(t2, t2.get_rect(centerx=px + self.PW // 2, y=py + 120))
        # Barre de fermeture auto
        ratio = min(1.0, self._timer / 2200)
        bw    = int((self.PW - 60) * ratio)
        pygame.draw.rect(surf, TEXT_D, (px + 30, py + 185, self.PW - 60, 6), border_radius=3)
        if bw > 0:
            pygame.draw.rect(surf, GREEN, (px + 30, py + 185, bw, 6), border_radius=3)
        self._btn_ok.draw(surf)


# Lancement jeux

def run_game(script_path):
    subprocess.Popen(
        [sys.executable, script_path],
        cwd=os.path.dirname(script_path)
    ).wait()


# Main

def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("NSI 2026 — Launcher")
    clock  = pygame.time.Clock()

    fonts = {
        "big":   pygame.font.SysFont("freesansbold", 28),
        "title": pygame.font.SysFont("freesansbold", 18),
        "body":  pygame.font.SysFont("freesansbold", 14),
        "small": pygame.font.SysFont("freesansbold", 12),
    }

    CARD_W, CARD_H = 210, 265
    CARD_GAP = 30
    total_w  = 3 * CARD_W + 2 * CARD_GAP
    ox       = (W - total_w) // 2
    CARDS_Y  = 148

    games = [
        {"title": "Card Simulator", "color": GOLD,   "tag": "CARDS",
         "sub": "Ouvre des coffres,\nfusionne, collectionne", "x": ox},
        {"title": "Arcade Game",    "color": ORANGE, "tag": "ARCADE",
         "sub": "Survie par vagues,\ngagne des pièces", "x": ox + CARD_W + CARD_GAP},
        {"title": "WebStats",       "color": GREEN,  "tag": "STATS",
         "sub": "Tes statistiques\ndans le navigateur", "x": ox + 2 * (CARD_W + CARD_GAP)},
    ]

    btn_card   = Button((games[0]["x"]+20, CARDS_Y+CARD_H-50, CARD_W-40, 36),
                        "Jouer", fonts["body"], GOLD,   on_click=lambda: run_game(CARD_MAIN))
    btn_arcade = Button((games[1]["x"]+20, CARDS_Y+CARD_H-50, CARD_W-40, 36),
                        "Jouer", fonts["body"], ORANGE, on_click=lambda: run_game(ARCADE_MAIN))
    btn_web    = Button((games[2]["x"]+20, CARDS_Y+CARD_H-50, CARD_W-40, 36),
                        "Ouvrir", fonts["body"], GREEN)
    btn_reset  = Button((20, H-48, 210, 32), "Effacer la sauvegarde",
                        fonts["small"], (60, 28, 28), radius=8)
    _quit = [False]  # conteneur mutable pour la closure
    btn_quit = Button((W-130, H-48, 110, 32), "Quitter",
                      fonts["small"], RED, radius=8,
                      on_click=lambda: _quit.__setitem__(0, True))

    popup = ResetPopup(fonts)

    btn_web.on_click   = lambda: (server_stop() if server_running() else server_start())
    btn_reset.on_click = popup.open

    running = True
    while running:
        dt     = clock.tick(60)
        events = pygame.event.get()

        for e in events:
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE and not popup.visible:
                running = False

            if popup.visible:
                popup.handle_event(e)
            else:
                btn_card.handle_event(e)
                btn_arcade.handle_event(e)
                btn_web.handle_event(e)
                btn_reset.handle_event(e)
                if btn_quit.handle_event(e):
                    running = False

        popup.update(dt)

        # Dessin
        screen.fill(BG)

        # Titre
        t = fonts["big"].render("NSI 2026  —  Launcher", True, TEXT_W)
        screen.blit(t, t.get_rect(centerx=W//2, y=20))
        s = fonts["small"].render("Sélectionne un jeu  •  Échap pour quitter", True, TEXT_M)
        screen.blit(s, s.get_rect(centerx=W//2, y=58))
        pygame.draw.line(screen, BORDER, (40, 78), (W-40, 78), 1)

        # Cartes jeux
        for i, g in enumerate(games):
            rx, ry = g["x"], CARDS_Y
            is_ws  = (i == 2)
            ws_on  = server_running()
            bc     = g["color"] if (not is_ws or ws_on) else BORDER
            alpha  = 255 if (not is_ws or ws_on) else 150

            draw_rrect(screen, PANEL, (rx, ry, CARD_W, CARD_H), r=14, border=bc, bw=2, alpha=alpha)

            ic = fonts["small"].render(g["tag"], True, g["color"])
            screen.blit(ic, ic.get_rect(centerx=rx+CARD_W//2, y=ry+14))
            ft = fonts["title"].render(g["title"], True, g["color"])
            screen.blit(ft, ft.get_rect(centerx=rx+CARD_W//2, y=ry+32))

            for li, line in enumerate(g["sub"].split("\n")):
                ls = fonts["small"].render(line, True, TEXT_M)
                screen.blit(ls, ls.get_rect(centerx=rx+CARD_W//2, y=ry+60+li*17))

            if is_ws:
                sc = GREEN if ws_on else RED
                st = fonts["small"].render("● Actif" if ws_on else "○ Arrêté", True, sc)
                screen.blit(st, st.get_rect(centerx=rx+CARD_W//2, y=ry+100))
                url = fonts["small"].render(SERVER_URL, True, TEXT_D)
                screen.blit(url, url.get_rect(centerx=rx+CARD_W//2, y=ry+116))

        btn_card.draw(screen)
        btn_arcade.draw(screen)
        btn_web.label = "Fermer" if server_running() else "Ouvrir"
        btn_web.draw(screen)

        # Barre bas
        pygame.draw.line(screen, BORDER, (0, H-62), (W, H-62), 1)
        note = fonts["small"].render("Appuie sur Échap dans un jeu pour revenir ici", True, TEXT_D)
        screen.blit(note, note.get_rect(centerx=W//2, y=H-76))

        btn_reset.draw(screen)
        btn_quit.draw(screen)

        # Popup
        popup.draw(screen)
        pygame.display.flip()

    server_stop()
    pygame.quit()


if __name__ == "__main__":
    main()