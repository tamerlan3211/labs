"""
config.py — Глобальные константы игры.
Здесь хранятся размеры окна, цвета, параметры игрового поля.
"""

# ── Размеры окна и сетки ──────────────────────────────────────────
WIDTH, HEIGHT   = 800, 600       # Размер окна в пикселях
BLOCK_SIZE      = 20             # Размер одной клетки сетки
PANEL_HEIGHT    = 50             # Высота верхней панели HUD (счёт, уровень)

# Игровое поле начинается ниже панели
FIELD_TOP    = PANEL_HEIGHT
FIELD_BOTTOM = HEIGHT
FIELD_LEFT   = 0
FIELD_RIGHT  = WIDTH

# Количество клеток по осям (для генерации позиций)
COLS = WIDTH  // BLOCK_SIZE
ROWS = (HEIGHT - PANEL_HEIGHT) // BLOCK_SIZE

# ── Частота кадров ────────────────────────────────────────────────
FPS = 60          # Максимальный FPS (логика игры управляется отдельным таймером)

# ── Начальные параметры змейки ────────────────────────────────────
INIT_SPEED   = 10   # Тиков в секунду (обновлений игровой логики)
SPEED_STEP   =  2   # Прибавка скорости за каждый новый уровень
LEVEL_STEP   =  3   # Сколько очков нужно для перехода на следующий уровень

# ── Цвета ─────────────────────────────────────────────────────────
BLACK       = (  0,   0,   0)
WHITE       = (255, 255, 255)
GRAY        = (100, 100, 100)
DARK_GRAY   = ( 30,  30,  40)
PANEL_COLOR = ( 15,  15,  25)

# Еда
COLOR_FOOD_NORMAL  = (  0, 255,   0)   # Зелёная — 1 очко
COLOR_FOOD_BONUS   = (255, 215,   0)   # Золотая — 3 очка, исчезает быстро
COLOR_FOOD_SUPER   = (  0, 200, 255)   # Синяя   — 5 очков, исчезает очень быстро
COLOR_FOOD_POISON  = (180,   0,  50)   # Тёмно-красная — яд, укорачивает змейку

# Препятствия
COLOR_OBSTACLE = ( 80,  80, 120)

# Пауэрапы
COLOR_POWERUP_SPEED  = (255, 140,   0)  # Оранжевый — ускорение
COLOR_POWERUP_SLOW   = ( 50, 100, 255)  # Синий     — замедление
COLOR_POWERUP_SHIELD = (180, 255, 180)  # Светло-зелёный — щит

# UI
COLOR_BTN        = ( 40,  40,  60)
COLOR_BTN_HOVER  = ( 70,  70, 110)
COLOR_BTN_BORDER = ( 80, 130, 220)
COLOR_ACCENT     = ( 80, 200, 120)
COLOR_DANGER     = (220,  60,  60)
COLOR_TITLE      = (100, 220, 150)

# ── Параметры еды ─────────────────────────────────────────────────
FOOD_TYPES = {
    # name       : (очки, цвет,                  время жизни мс, вес появления)
    'normal' : (1, COLOR_FOOD_NORMAL,  None,  60),   # не исчезает, часто
    'bonus'  : (3, COLOR_FOOD_BONUS,   6000,  25),   # 6 сек
    'super'  : (5, COLOR_FOOD_SUPER,   3000,  10),   # 3 сек
    'poison' : (0, COLOR_FOOD_POISON,  8000,   5),   # яд, 8 сек
}

# ── Параметры пауэрапов ───────────────────────────────────────────
POWERUP_FIELD_DURATION = 8000    # Пауэрап исчезает с поля через 8 сек
POWERUP_EFFECT_DURATION = 5000   # Эффект длится 5 сек

POWERUP_TYPES = {
    'speed'  : (COLOR_POWERUP_SPEED,  'SPEED BOOST',  '⚡'),
    'slow'   : (COLOR_POWERUP_SLOW,   'SLOW MOTION',  '🐢'),
    'shield' : (COLOR_POWERUP_SHIELD, 'SHIELD',       '🛡'),
}

# ── База данных ───────────────────────────────────────────────────
DB_CONFIG = {
    'host'    : 'localhost',
    'port'    : 5432,
    'dbname'  : 'snake_db',
    'user'    : 'postgres',
    'password': '12345',   
}

# SQL для создания таблиц (выполняется при первом запуске)
SQL_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""
