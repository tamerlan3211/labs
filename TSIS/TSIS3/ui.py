"""
ui.py — All non-gameplay screens for TSIS3 Racer.
Each screen is a function that returns the next state string.
"""

import pygame
from pygame.locals import *
from persistence import load_leaderboard, load_settings, save_settings

# ─────── Colours & fonts (module-level so they're ready after pygame.init()) ─────

BG_DARK  = (15,  20,  40)
BG_MID   = (25,  35,  65)
ACCENT   = (0,   220, 120)
ACCENT2  = (255, 200, 0)
WHITE    = (255, 255, 255)
GREY     = (160, 160, 180)
RED_SOFT = (220, 60,  60)
BLACK    = (0,   0,   0)

def _fonts():
    """Lazy-load fonts (must be called after pygame.init)."""
    return {
        "title":  pygame.font.SysFont("Impact", 64),
        "large":  pygame.font.SysFont("Verdana", 36, bold=True),
        "medium": pygame.font.SysFont("Verdana", 22),
        "small":  pygame.font.SysFont("Verdana", 16),
    }

# ─────── Generic helpers ────────────────────────────────────────────────────────

def draw_bg(surface):
    surface.fill(BG_DARK)
    # Subtle grid lines for atmosphere
    for y in range(0, surface.get_height(), 40):
        pygame.draw.line(surface, (30, 40, 70), (0, y), (surface.get_width(), y))
    for x in range(0, surface.get_width(), 40):
        pygame.draw.line(surface, (30, 40, 70), (x, 0), (x, surface.get_height()))

def draw_title(surface, fonts, text, y=60):
    surf = fonts["title"].render(text, True, ACCENT)
    surface.blit(surf, surf.get_rect(centerx=surface.get_width()//2, top=y))

def make_button(surface, fonts, text, rect, hover=False, danger=False):
    """Draw a button; return the rect."""
    color   = (50, 220, 130) if not danger else (200, 60, 60)
    h_color = (80, 255, 160) if not danger else (240, 80, 80)
    bg      = h_color if hover else color
    shadow  = pygame.Rect(rect.x+3, rect.y+3, rect.width, rect.height)
    pygame.draw.rect(surface, (0, 0, 0, 100), shadow, border_radius=8)
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=8)
    lbl = fonts["medium"].render(text, True, BLACK if not danger else WHITE)
    surface.blit(lbl, lbl.get_rect(center=rect.center))
    return rect


# ─────── Main Menu ──────────────────────────────────────────────────────────────

def main_menu(surface) -> str:
    """Returns: 'play' | 'leaderboard' | 'settings' | 'quit'"""
    fonts = _fonts()
    W = surface.get_width()
    clock = pygame.time.Clock()

    buttons = {
        "play":        pygame.Rect(W//2-100, 200, 200, 50),
        "leaderboard": pygame.Rect(W//2-100, 270, 200, 50),
        "settings":    pygame.Rect(W//2-100, 340, 200, 50),
        "quit":        pygame.Rect(W//2-100, 410, 200, 50),
    }
    labels = {
        "play":        "▶  Play",
        "leaderboard": "🏆  Leaderboard",
        "settings":    "⚙  Settings",
        "quit":        "✕  Quit",
    }

    while True:
        mouse = pygame.mouse.get_pos()
        draw_bg(surface)
        draw_title(surface, fonts, "RACER", y=80)
        sub = fonts["small"].render("TSIS3 Edition", True, ACCENT2)
        surface.blit(sub, sub.get_rect(centerx=W//2, top=158))

        for key, rect in buttons.items():
            hover = rect.collidepoint(mouse)
            danger = (key == "quit")
            make_button(surface, fonts, labels[key], rect, hover, danger)

        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                for key, rect in buttons.items():
                    if rect.collidepoint(mouse):
                        return key
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return "quit"

        pygame.display.flip()
        clock.tick(60)


# ─────── Name Entry ─────────────────────────────────────────────────────────────

def name_entry(surface) -> str:
    """Returns the entered player name (stripped), or 'Player1' as fallback."""
    fonts = _fonts()
    W = surface.get_width()
    clock = pygame.time.Clock()
    name = ""
    MAX_LEN = 14

    while True:
        draw_bg(surface)
        draw_title(surface, fonts, "RACER", y=60)

        prompt = fonts["medium"].render("Enter your name:", True, WHITE)
        surface.blit(prompt, prompt.get_rect(centerx=W//2, top=200))

        # Input box
        box = pygame.Rect(W//2-120, 250, 240, 46)
        pygame.draw.rect(surface, BG_MID, box, border_radius=8)
        pygame.draw.rect(surface, ACCENT, box, 2, border_radius=8)
        name_surf = fonts["large"].render(name + "|", True, ACCENT2)
        surface.blit(name_surf, name_surf.get_rect(center=box.center))

        hint = fonts["small"].render("Press ENTER to start", True, GREY)
        surface.blit(hint, hint.get_rect(centerx=W//2, top=320))

        for event in pygame.event.get():
            if event.type == QUIT:
                return "Player1"
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    return name.strip() or "Player1"
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif event.key == K_ESCAPE:
                    return "Player1"
                elif len(name) < MAX_LEN and event.unicode.isprintable():
                    name += event.unicode

        pygame.display.flip()
        clock.tick(60)


# ─────── Settings Screen ────────────────────────────────────────────────────────

def settings_screen(surface) -> str:
    """Modifies settings in-place and returns 'menu'."""
    fonts  = _fonts()
    W      = surface.get_width()
    clock  = pygame.time.Clock()
    cfg    = load_settings()

    CAR_COLORS = ["BLUE", "RED", "GREEN", "YELLOW"]
    CAR_COLOR_HEX = {"BLUE": (30,120,255), "RED":(220,40,40), "GREEN":(30,200,80), "YELLOW":(240,200,0)}
    DIFFICULTIES = ["EASY", "MEDIUM", "HARD"]

    def idx_cycle(lst, val, step=1):
        return lst[(lst.index(val) + step) % len(lst)]

    back_btn   = pygame.Rect(W//2-80, 500, 160, 46)
    sound_btn  = pygame.Rect(W//2+60, 220, 80, 36)
    color_l    = pygame.Rect(W//2-110, 280, 36, 36)
    color_r    = pygame.Rect(W//2+74, 280, 36, 36)
    diff_l     = pygame.Rect(W//2-110, 340, 36, 36)
    diff_r     = pygame.Rect(W//2+74, 340, 36, 36)

    while True:
        mouse = pygame.mouse.get_pos()
        draw_bg(surface)
        draw_title(surface, fonts, "SETTINGS", y=60)

        # Sound
        slabel = fonts["medium"].render("Sound:", True, WHITE)
        surface.blit(slabel, (W//2-130, 228))
        sval   = "ON" if cfg["sound"] else "OFF"
        sc     = ACCENT if cfg["sound"] else RED_SOFT
        sv     = fonts["medium"].render(sval, True, sc)
        surface.blit(sv, (W//2+10, 228))
        make_button(surface, fonts, "Toggle", sound_btn, sound_btn.collidepoint(mouse))

        # Car color
        clabel = fonts["medium"].render("Car Color:", True, WHITE)
        surface.blit(clabel, (W//2-130, 288))
        pygame.draw.rect(surface, CAR_COLOR_HEX[cfg["car_color"]], (W//2-60, 288, 120, 32), border_radius=6)
        make_button(surface, fonts, "<", color_l, color_l.collidepoint(mouse))
        make_button(surface, fonts, ">", color_r, color_r.collidepoint(mouse))
        cc = fonts["small"].render(cfg["car_color"], True, WHITE)
        surface.blit(cc, cc.get_rect(centerx=W//2, top=324))

        # Difficulty
        dlabel = fonts["medium"].render("Difficulty:", True, WHITE)
        surface.blit(dlabel, (W//2-130, 348))
        dclr = {"EASY": ACCENT, "MEDIUM": ACCENT2, "HARD": RED_SOFT}[cfg["difficulty"]]
        dv   = fonts["medium"].render(cfg["difficulty"], True, dclr)
        surface.blit(dv, (W//2-20, 348))
        make_button(surface, fonts, "<", diff_l, diff_l.collidepoint(mouse))
        make_button(surface, fonts, ">", diff_r, diff_r.collidepoint(mouse))

        make_button(surface, fonts, "← Back", back_btn, back_btn.collidepoint(mouse))

        for event in pygame.event.get():
            if event.type == QUIT:
                save_settings(cfg)
                return "menu"
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                save_settings(cfg)
                return "menu"
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if sound_btn.collidepoint(mouse):
                    cfg["sound"] = not cfg["sound"]
                elif color_l.collidepoint(mouse):
                    cfg["car_color"] = idx_cycle(CAR_COLORS, cfg["car_color"], -1)
                elif color_r.collidepoint(mouse):
                    cfg["car_color"] = idx_cycle(CAR_COLORS, cfg["car_color"], 1)
                elif diff_l.collidepoint(mouse):
                    cfg["difficulty"] = idx_cycle(DIFFICULTIES, cfg["difficulty"], -1)
                elif diff_r.collidepoint(mouse):
                    cfg["difficulty"] = idx_cycle(DIFFICULTIES, cfg["difficulty"], 1)
                elif back_btn.collidepoint(mouse):
                    save_settings(cfg)
                    return "menu"

        pygame.display.flip()
        clock.tick(60)


# ─────── Game Over Screen ───────────────────────────────────────────────────────

def game_over_screen(surface, score, distance, coins) -> str:
    """Returns 'retry' or 'menu'."""
    fonts = _fonts()
    W     = surface.get_width()
    clock = pygame.time.Clock()

    retry_btn = pygame.Rect(W//2-110, 430, 200, 50)
    menu_btn  = pygame.Rect(W//2-110, 495, 200, 50)

    while True:
        mouse = pygame.mouse.get_pos()
        draw_bg(surface)

        # Title
        go = fonts["title"].render("GAME OVER", True, RED_SOFT)
        surface.blit(go, go.get_rect(centerx=W//2, top=70))

        # Stats
        stats = [
            ("Score",    str(score)),
            ("Distance", f"{distance} m"),
            ("Coins",    str(coins)),
        ]
        for i, (label, val) in enumerate(stats):
            y = 200 + i * 60
            lsurf = fonts["medium"].render(label + ":", True, GREY)
            vsurf = fonts["large"].render(val, True, ACCENT2)
            surface.blit(lsurf, (W//2-130, y))
            surface.blit(vsurf, vsurf.get_rect(right=W//2+130, top=y))

        make_button(surface, fonts, "▶  Retry",     retry_btn, retry_btn.collidepoint(mouse))
        make_button(surface, fonts, "⌂  Main Menu", menu_btn,  menu_btn.collidepoint(mouse))

        for event in pygame.event.get():
            if event.type == QUIT:
                return "menu"
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if retry_btn.collidepoint(mouse):
                    return "retry"
                if menu_btn.collidepoint(mouse):
                    return "menu"
            if event.type == KEYDOWN:
                if event.key == K_r:
                    return "retry"
                if event.key == K_ESCAPE:
                    return "menu"

        pygame.display.flip()
        clock.tick(60)


# ─────── Leaderboard Screen ─────────────────────────────────────────────────────

def leaderboard_screen(surface) -> str:
    """Returns 'menu'."""
    fonts   = _fonts()
    W       = surface.get_width()
    clock   = pygame.time.Clock()
    entries = load_leaderboard()

    back_btn = pygame.Rect(W//2-80, 545, 160, 44)

    while True:
        mouse = pygame.mouse.get_pos()
        draw_bg(surface)
        draw_title(surface, fonts, "LEADERBOARD", y=28)

        # Header
        hdr_y = 105
        cols = [(W//2-170, "Rank"), (W//2-110, "Name"), (W//2+20, "Score"), (W//2+100, "Dist")]
        for cx, txt in cols:
            h = fonts["small"].render(txt, True, ACCENT)
            surface.blit(h, (cx, hdr_y))
        pygame.draw.line(surface, ACCENT, (W//2-180, hdr_y+22), (W//2+160, hdr_y+22), 1)

        # Rows
        for i, entry in enumerate(entries[:10]):
            y = hdr_y + 35 + i * 38
            # Highlight top 3
            if i == 0:   row_col = ACCENT2
            elif i == 1: row_col = GREY
            elif i == 2: row_col = (180, 100, 50)
            else:        row_col = WHITE

            rank_s = fonts["medium"].render(f"#{i+1}", True, row_col)
            name_s = fonts["medium"].render(entry.get("name","?")[:10], True, row_col)
            scr_s  = fonts["medium"].render(str(entry.get("score",0)), True, row_col)
            dist_s = fonts["small"].render(f"{entry.get('distance',0)}m", True, GREY)

            surface.blit(rank_s, (W//2-170, y))
            surface.blit(name_s, (W//2-110, y))
            surface.blit(scr_s,  scr_s.get_rect(right=W//2+140, top=y))
            surface.blit(dist_s, dist_s.get_rect(right=W//2+175, top=y+4))

        if not entries:
            no = fonts["medium"].render("No scores yet — play first!", True, GREY)
            surface.blit(no, no.get_rect(centerx=W//2, top=250))

        make_button(surface, fonts, "← Back", back_btn, back_btn.collidepoint(mouse))

        for event in pygame.event.get():
            if event.type == QUIT:
                return "menu"
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.collidepoint(mouse):
                    return "menu"
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return "menu"

        pygame.display.flip()
        clock.tick(60)
