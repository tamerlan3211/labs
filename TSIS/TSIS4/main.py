"""
main.py — Точка входа. Управляет экранами:
главное меню, игра, game over, таблица лидеров, настройки.
"""

import pygame
import sys
import json
import os

from config import (
    WIDTH, HEIGHT, FPS, PANEL_HEIGHT,
    BLACK, WHITE, GRAY, DARK_GRAY, PANEL_COLOR,
    COLOR_BTN, COLOR_BTN_HOVER, COLOR_BTN_BORDER,
    COLOR_ACCENT, COLOR_DANGER, COLOR_TITLE,
    POWERUP_TYPES,
)
from game import (
    GameState,
    draw_grid, draw_snake, draw_obstacles, draw_hud,
)
from db import init_db, get_or_create_player, save_session, get_leaderboard, get_personal_best

# ── Путь к settings.json ──────────────────────────────────────────
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'settings.json')

# ── Дефолтные настройки ───────────────────────────────────────────
DEFAULT_SETTINGS = {
    'snake_color': [0, 200, 80],
    'grid_overlay': True,
    'sound': False,
}


# ─────────────────────────────────────────────────────────────────
#  Работа с настройками (JSON)
# ─────────────────────────────────────────────────────────────────

def load_settings() -> dict:
    """Загружает настройки из settings.json. При ошибке возвращает дефолтные."""
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Дополняем отсутствующие ключи дефолтами
        for k, v in DEFAULT_SETTINGS.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    """Сохраняет настройки в settings.json."""
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"[Settings] Ошибка сохранения: {e}")


# ─────────────────────────────────────────────────────────────────
#  UI-утилиты
# ─────────────────────────────────────────────────────────────────

class Button:
    """Простая кнопка с hover-эффектом."""

    def __init__(self, rect: pygame.Rect, text: str,
                 font: pygame.font.Font,
                 color_normal=COLOR_BTN,
                 color_hover=COLOR_BTN_HOVER,
                 color_border=COLOR_BTN_BORDER,
                 color_text=WHITE):
        self.rect         = rect
        self.text         = text
        self.font         = font
        self.c_normal     = color_normal
        self.c_hover      = color_hover
        self.c_border     = color_border
        self.c_text       = color_text

    def draw(self, surface: pygame.Surface) -> bool:
        """Рисует кнопку. Возвращает True если мышь наведена."""
        mx, my = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mx, my)
        bg = self.c_hover if hovered else self.c_normal
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.c_border, self.rect, 2, border_radius=8)
        lbl = self.font.render(self.text, True, self.c_text)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width() // 2,
                           self.rect.centery - lbl.get_height() // 2))
        return hovered

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """Возвращает True если на кнопку кликнули."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False


def draw_background(surface: pygame.Surface):
    """Красивый тёмный фон с точечным узором для меню."""
    surface.fill((10, 12, 20))
    # Рисуем сетку точек
    for x in range(0, WIDTH, 30):
        for y in range(0, HEIGHT, 30):
            pygame.draw.circle(surface, (25, 28, 45), (x, y), 1)


def draw_title(surface: pygame.Surface, font_big: pygame.font.Font, subtitle=''):
    """Рисует заголовок игры с тенью."""
    # Тень
    shadow = font_big.render('SNAKE', True, (0, 80, 30))
    surface.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + 3, 53))
    # Основной текст
    title = font_big.render('SNAKE', True, COLOR_TITLE)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    if subtitle:
        font_sub = pygame.font.SysFont('Consolas', 18)
        sub = font_sub.render(subtitle, True, GRAY)
        surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 115))


# ─────────────────────────────────────────────────────────────────
#  Экран ввода имени
# ─────────────────────────────────────────────────────────────────

def screen_username(surface: pygame.Surface, clock: pygame.time.Clock,
                    font: pygame.font.Font, font_big: pygame.font.Font) -> str:
    """
    Экран ввода имени пользователя.
    Возвращает введённое имя (не пустое).
    """
    username = ''
    font_hint = pygame.font.SysFont('Consolas', 18)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 20 and event.unicode.isprintable():
                    username += event.unicode

        draw_background(surface)
        draw_title(surface, font_big, 'Enter your name')

        # Поле ввода
        box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 25, 300, 50)
        pygame.draw.rect(surface, (30, 35, 55), box, border_radius=8)
        pygame.draw.rect(surface, COLOR_BTN_BORDER, box, 2, border_radius=8)

        # Мигающий курсор
        cursor = '|' if (pygame.time.get_ticks() // 500) % 2 == 0 else ' '
        name_surf = font.render(username + cursor, True, WHITE)
        surface.blit(name_surf, (box.centerx - name_surf.get_width() // 2,
                                 box.centery - name_surf.get_height() // 2))

        hint = font_hint.render('Press ENTER to continue', True, GRAY)
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 40))

        pygame.display.flip()
        clock.tick(FPS)


# ─────────────────────────────────────────────────────────────────
#  Главное меню
# ─────────────────────────────────────────────────────────────────

def screen_main_menu(surface: pygame.Surface, clock: pygame.time.Clock,
                     font: pygame.font.Font, font_big: pygame.font.Font) -> str:
    """
    Главное меню. Возвращает: 'play' | 'leaderboard' | 'settings' | 'quit'.
    """
    btn_w, btn_h = 220, 48
    cx = WIDTH // 2 - btn_w // 2
    buttons = {
        'play'       : Button(pygame.Rect(cx, 170, btn_w, btn_h), '▶  PLAY',        font),
        'leaderboard': Button(pygame.Rect(cx, 230, btn_w, btn_h), '🏆  LEADERBOARD', font),
        'settings'   : Button(pygame.Rect(cx, 290, btn_w, btn_h), '⚙  SETTINGS',    font),
        'quit'       : Button(pygame.Rect(cx, 350, btn_w, btn_h), '✕  QUIT',         font,
                              color_border=COLOR_DANGER),
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            for action, btn in buttons.items():
                if btn.is_clicked(event):
                    return action

        draw_background(surface)
        draw_title(surface, font_big)
        for btn in buttons.values():
            btn.draw(surface)

        # Версия
        ver = pygame.font.SysFont('Consolas', 14).render('Practice 12 — Snake', True, (50, 55, 80))
        surface.blit(ver, (WIDTH - ver.get_width() - 8, HEIGHT - 20))

        pygame.display.flip()
        clock.tick(FPS)


# ─────────────────────────────────────────────────────────────────
#  Экран игры
# ─────────────────────────────────────────────────────────────────

def screen_game(surface: pygame.Surface, clock: pygame.time.Clock,
                font: pygame.font.Font, font_big: pygame.font.Font,
                font_small: pygame.font.Font,
                settings: dict, player_id: int, personal_best: int) -> tuple[int, int]:
    """
    Основной игровой экран.
    Возвращает (итоговый_score, итоговый_level).
    """
    snake_color = tuple(settings['snake_color'])
    grid_on     = settings['grid_overlay']

    gs = GameState(snake_color)
    font_tiny = pygame.font.SysFont('Consolas', 14)

    # Направления
    DIR_MAP = {
        pygame.K_LEFT : (-20,   0),
        pygame.K_RIGHT: ( 20,   0),
        pygame.K_UP   : (  0, -20),
        pygame.K_DOWN : (  0,  20),
        pygame.K_a    : (-20,   0),
        pygame.K_d    : ( 20,   0),
        pygame.K_w    : (  0, -20),
        pygame.K_s    : (  0,  20),
    }

    while gs.alive:
        # ── Обработка событий ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return gs.score, gs.level
                if event.key in DIR_MAP:
                    gs.turn(DIR_MAP[event.key])

        # ── Логический тик ──
        if gs.tick_due():
            gs.update()

        # ── Отрисовка ──
        surface.fill(DARK_GRAY)

        if grid_on:
            draw_grid(surface)

        # Еда
        for food in gs.foods:
            food.draw(surface)

        # Пауэрап на поле
        if gs.powerup:
            gs.powerup.draw(surface, font_tiny)

        # Препятствия
        draw_obstacles(surface, gs.obstacles)

        # Змейка
        draw_snake(surface, gs.snake, snake_color, gs.shield_active)

        # HUD
        draw_hud(surface, gs, personal_best, font, font_small)

        pygame.display.flip()
        clock.tick(FPS)

    return gs.score, gs.level


# ─────────────────────────────────────────────────────────────────
#  Экран Game Over
# ─────────────────────────────────────────────────────────────────

def screen_game_over(surface: pygame.Surface, clock: pygame.time.Clock,
                     font: pygame.font.Font, font_big: pygame.font.Font,
                     score: int, level: int, personal_best: int) -> str:
    """
    Экран конца игры.
    Возвращает: 'retry' | 'menu'.
    """
    btn_w, btn_h = 200, 46
    cx = WIDTH // 2
    btn_retry = Button(pygame.Rect(cx - btn_w - 10, 380, btn_w, btn_h), '↺  RETRY',    font)
    btn_menu  = Button(pygame.Rect(cx + 10,         380, btn_w, btn_h), '⌂  MAIN MENU', font)
    font_sub  = pygame.font.SysFont('Consolas', 22)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_retry.is_clicked(event):
                return 'retry'
            if btn_menu.is_clicked(event):
                return 'menu'

        draw_background(surface)

        # Заголовок GAME OVER
        go = font_big.render('GAME OVER', True, COLOR_DANGER)
        surface.blit(go, (WIDTH // 2 - go.get_width() // 2, 80))

        # Результаты
        lines = [
            (f"Score:  {score}",         WHITE),
            (f"Level:  {level}",         COLOR_ACCENT),
            (f"Best:   {max(score, personal_best)}", (255, 215, 0)),
        ]
        y = 200
        for text, color in lines:
            s = font_sub.render(text, True, color)
            surface.blit(s, (WIDTH // 2 - s.get_width() // 2, y))
            y += 45

        btn_retry.draw(surface)
        btn_menu.draw(surface)

        pygame.display.flip()
        clock.tick(FPS)


# ─────────────────────────────────────────────────────────────────
#  Экран таблицы лидеров
# ─────────────────────────────────────────────────────────────────

def screen_leaderboard(surface: pygame.Surface, clock: pygame.time.Clock,
                       font: pygame.font.Font, font_big: pygame.font.Font):
    """Показывает топ-10 лидеров из базы данных."""
    btn_back = Button(pygame.Rect(WIDTH // 2 - 90, HEIGHT - 65, 180, 44), '← BACK', font)
    font_row  = pygame.font.SysFont('Consolas', 18)
    font_hdr  = pygame.font.SysFont('Consolas', 18, bold=True)

    # Загружаем данные один раз
    rows = get_leaderboard(10)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_back.is_clicked(event) or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                return

        draw_background(surface)
        draw_title(surface, font_big, 'TOP 10 LEADERBOARD')

        # Шапка таблицы
        headers = ['#', 'Player', 'Score', 'Lvl', 'Date']
        cols_x  = [40, 90, 370, 480, 570]
        y = 140
        for hdr, x in zip(headers, cols_x):
            h = font_hdr.render(hdr, True, COLOR_ACCENT)
            surface.blit(h, (x, y))
        pygame.draw.line(surface, COLOR_BTN_BORDER, (30, y + 26), (WIDTH - 30, y + 26), 1)
        y += 35

        if not rows:
            no_data = font_row.render('No records yet. Play to get on the board!', True, GRAY)
            surface.blit(no_data, (WIDTH // 2 - no_data.get_width() // 2, y + 20))
        else:
            for row in rows:
                # Чередующийся фон строк
                if row['rank'] % 2 == 0:
                    pygame.draw.rect(surface, (20, 22, 38),
                                     (30, y - 2, WIDTH - 60, 26), border_radius=4)
                rank_color = (255, 215, 0) if row['rank'] == 1 else (
                             (192, 192, 192) if row['rank'] == 2 else (
                             (205, 127, 50) if row['rank'] == 3 else WHITE))
                values = [
                    str(row['rank']),
                    row['username'][:18],
                    str(row['score']),
                    str(row['level']),
                    row['played_at'],
                ]
                for val, x, in zip(values, cols_x):
                    c = rank_color if val == str(row['rank']) else WHITE
                    s = font_row.render(val, True, c)
                    surface.blit(s, (x, y))
                y += 28

        btn_back.draw(surface)
        pygame.display.flip()
        clock.tick(FPS)


# ─────────────────────────────────────────────────────────────────
#  Экран настроек
# ─────────────────────────────────────────────────────────────────

def screen_settings(surface: pygame.Surface, clock: pygame.time.Clock,
                    font: pygame.font.Font, font_big: pygame.font.Font,
                    settings: dict) -> dict:
    """
    Экран настроек. Возвращает обновлённый словарь настроек.
    """
    font_lbl  = pygame.font.SysFont('Consolas', 20)
    btn_back  = Button(pygame.Rect(WIDTH // 2 - 110, HEIGHT - 75, 220, 46),
                       '💾  SAVE & BACK', font)

    # Локальная копия настроек для редактирования
    local = dict(settings)
    local['snake_color'] = list(local['snake_color'])

    # Кнопки переключения сетки и звука
    btn_grid  = Button(pygame.Rect(WIDTH // 2 + 20, 200, 100, 36), '', font)
    btn_sound = Button(pygame.Rect(WIDTH // 2 + 20, 255, 100, 36), '', font)

    # Цветовые пресеты
    color_presets = [
        (0, 200, 80), (0, 180, 255), (255, 80, 80),
        (255, 200, 0), (200, 100, 255), (255, 140, 0),
    ]
    preset_size = 36
    preset_gap  = 12
    total_w = len(color_presets) * (preset_size + preset_gap) - preset_gap
    preset_start_x = WIDTH // 2 - total_w // 2
    preset_y = 340

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return settings   # Отмена — не сохраняем

            if btn_back.is_clicked(event):
                save_settings(local)
                return local

            if btn_grid.is_clicked(event):
                local['grid_overlay'] = not local['grid_overlay']

            if btn_sound.is_clicked(event):
                local['sound'] = not local['sound']

            # Клик по цветовому пресету
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, color in enumerate(color_presets):
                    px = preset_start_x + i * (preset_size + preset_gap)
                    r = pygame.Rect(px, preset_y, preset_size, preset_size)
                    if r.collidepoint(event.pos):
                        local['snake_color'] = list(color)

        draw_background(surface)
        draw_title(surface, font_big, 'SETTINGS')

        # ── Сетка ──
        gl = font_lbl.render('Grid Overlay:', True, WHITE)
        surface.blit(gl, (WIDTH // 2 - 200, 208))
        gv_text = 'ON' if local['grid_overlay'] else 'OFF'
        gv_col  = COLOR_ACCENT if local['grid_overlay'] else COLOR_DANGER
        btn_grid.text = gv_text
        btn_grid.c_text = gv_col
        btn_grid.draw(surface)

        # ── Звук ──
        sl = font_lbl.render('Sound:', True, WHITE)
        surface.blit(sl, (WIDTH // 2 - 200, 263))
        sv_text = 'ON' if local['sound'] else 'OFF'
        sv_col  = COLOR_ACCENT if local['sound'] else COLOR_DANGER
        btn_sound.text = sv_text
        btn_sound.c_text = sv_col
        btn_sound.draw(surface)

        # ── Цвет змейки ──
        cl = font_lbl.render('Snake Color:', True, WHITE)
        surface.blit(cl, (WIDTH // 2 - cl.get_width() // 2, 305))

        for i, color in enumerate(color_presets):
            px = preset_start_x + i * (preset_size + preset_gap)
            r = pygame.Rect(px, preset_y, preset_size, preset_size)
            pygame.draw.rect(surface, color, r, border_radius=6)
            if list(color) == local['snake_color']:
                pygame.draw.rect(surface, WHITE, r, 3, border_radius=6)

        # Превью выбранного цвета
        preview_color = tuple(local['snake_color'])
        pygame.draw.rect(surface, preview_color,
                         (WIDTH // 2 - 30, preset_y + 50, 60, 20), border_radius=4)

        btn_back.draw(surface)
        pygame.display.flip()
        clock.tick(FPS)


# ─────────────────────────────────────────────────────────────────
#  Точка входа
# ─────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Snake — Practice 12')
    clock = pygame.time.Clock()

    # ── Шрифты ──
    font_big   = pygame.font.SysFont('Consolas', 60, bold=True)
    font       = pygame.font.SysFont('Consolas', 22)
    font_small = pygame.font.SysFont('Consolas', 16)

    # ── Инициализация БД ──
    init_db()

    # ── Загрузка настроек ──
    settings = load_settings()

    # ── Ввод имени и получение player_id ──
    username  = screen_username(surface, clock, font, font_big)
    player_id = get_or_create_player(username)

    screen = 'menu'   # Текущий экран

    while True:
        if screen == 'menu':
            action = screen_main_menu(surface, clock, font, font_big)
            if action == 'quit':
                break
            elif action == 'play':
                screen = 'game'
            elif action == 'leaderboard':
                screen = 'leaderboard'
            elif action == 'settings':
                screen = 'settings'

        elif screen == 'game':
            personal_best = get_personal_best(player_id)
            score, level  = screen_game(
                surface, clock, font, font_big, font_small,
                settings, player_id, personal_best
            )
            # Сохраняем результат в БД
            save_session(player_id, score, level)
            screen = 'game_over'

        elif screen == 'game_over':
            personal_best = get_personal_best(player_id)
            action = screen_game_over(
                surface, clock, font, font_big, score, level, personal_best
            )
            screen = 'game' if action == 'retry' else 'menu'

        elif screen == 'leaderboard':
            screen_leaderboard(surface, clock, font, font_big)
            screen = 'menu'

        elif screen == 'settings':
            settings = screen_settings(surface, clock, font, font_big, settings)
            screen = 'menu'

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
