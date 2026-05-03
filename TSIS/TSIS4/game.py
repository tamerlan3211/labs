"""
game.py — Вся игровая логика змейки:
движение, еда, яд, пауэрапы, препятствия, коллизии.
"""

import pygame
import random
import math

from config import (
    WIDTH, HEIGHT, BLOCK_SIZE, PANEL_HEIGHT,
    COLS, ROWS, FIELD_TOP,
    INIT_SPEED, SPEED_STEP, LEVEL_STEP,
    BLACK, WHITE, GRAY, DARK_GRAY, PANEL_COLOR,
    COLOR_OBSTACLE,
    FOOD_TYPES, POWERUP_TYPES,
    POWERUP_FIELD_DURATION, POWERUP_EFFECT_DURATION,
    COLOR_BTN, COLOR_BTN_BORDER, COLOR_ACCENT, COLOR_DANGER,
)


# ─────────────────────────────────────────────────────────────────
#  Вспомогательные функции позиционирования
# ─────────────────────────────────────────────────────────────────

def random_cell(exclude: list[tuple]) -> tuple[int, int]:
    """
    Возвращает случайную свободную клетку на игровом поле.
    Исключает все клетки из списка exclude (координаты в пикселях).
    """
    while True:
        col = random.randint(0, COLS - 1)
        row = random.randint(0, ROWS - 1)
        px = col * BLOCK_SIZE
        py = FIELD_TOP + row * BLOCK_SIZE
        if (px, py) not in exclude:
            return (px, py)


def obstacles_for_level(level: int, snake_head: tuple, exclude: list) -> list[tuple]:
    """
    Генерирует список препятствий для уровня >= 3.
    Количество препятствий растёт с уровнем.
    Гарантирует, что голова змейки не будет заблокирована.

    :param level:      текущий уровень
    :param snake_head: позиция головы (px, py)
    :param exclude:    занятые клетки (тело, еда, пауэрапы)
    :return: список позиций препятствий
    """
    if level < 3:
        return []

    count = min(4 + (level - 3) * 2, 20)  # максимум 20 блоков
    obstacles = []
    # Зона безопасности вокруг головы: 3 клетки
    safe_zone = {
        (snake_head[0] + dx * BLOCK_SIZE, snake_head[1] + dy * BLOCK_SIZE)
        for dx in range(-3, 4)
        for dy in range(-3, 4)
    }

    attempts = 0
    while len(obstacles) < count and attempts < 500:
        attempts += 1
        pos = random_cell(exclude + obstacles)
        if pos not in safe_zone:
            obstacles.append(pos)

    return obstacles


# ─────────────────────────────────────────────────────────────────
#  Класс еды
# ─────────────────────────────────────────────────────────────────

class FoodItem:
    """
    Один элемент еды на поле.
    Хранит тип, позицию, очки, цвет и время исчезновения.
    """

    def __init__(self, pos: tuple, food_type: str):
        self.pos       = pos                           # (px, py)
        self.food_type = food_type
        points, color, lifetime_ms, _ = FOOD_TYPES[food_type]
        self.points    = points
        self.color     = color
        # Время появления (мс) — для отсчёта таймера
        self.spawn_time   = pygame.time.get_ticks()
        self.lifetime_ms  = lifetime_ms                # None = не исчезает

    def is_expired(self) -> bool:
        """Возвращает True если еда должна исчезнуть."""
        if self.lifetime_ms is None:
            return False
        return pygame.time.get_ticks() - self.spawn_time > self.lifetime_ms

    def remaining_fraction(self) -> float:
        """
        Возвращает долю оставшегося времени жизни [0..1].
        1.0 = только что появилась, 0.0 = сейчас исчезнет.
        """
        if self.lifetime_ms is None:
            return 1.0
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return max(0.0, 1.0 - elapsed / self.lifetime_ms)

    def draw(self, surface: pygame.Surface):
        """Рисует еду. Мигает когда время почти вышло."""
        frac = self.remaining_fraction()
        # Мигание: последние 30% времени жизни
        if frac < 0.3:
            # Мигаем с частотой ~4 Гц
            if (pygame.time.get_ticks() // 125) % 2 == 0:
                return  # Пропускаем кадр — эффект мигания

        r = pygame.Rect(self.pos[0] + 2, self.pos[1] + 2,
                        BLOCK_SIZE - 4, BLOCK_SIZE - 4)
        pygame.draw.rect(surface, self.color, r, border_radius=4)

        # Яд — рисуем крестик поверх
        if self.food_type == 'poison':
            cx, cy = self.pos[0] + BLOCK_SIZE // 2, self.pos[1] + BLOCK_SIZE // 2
            pygame.draw.line(surface, WHITE, (cx - 4, cy - 4), (cx + 4, cy + 4), 2)
            pygame.draw.line(surface, WHITE, (cx + 4, cy - 4), (cx - 4, cy + 4), 2)


# ─────────────────────────────────────────────────────────────────
#  Класс пауэрапа
# ─────────────────────────────────────────────────────────────────

class PowerUp:
    """
    Временный пауэрап на поле.
    Исчезает через POWERUP_FIELD_DURATION мс если не собран.
    """

    def __init__(self, pos: tuple, pu_type: str):
        self.pos        = pos
        self.pu_type    = pu_type
        color, label, icon = POWERUP_TYPES[pu_type]
        self.color      = color
        self.label      = label
        self.icon       = icon
        self.spawn_time = pygame.time.get_ticks()

    def is_expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_time > POWERUP_FIELD_DURATION

    def remaining_fraction(self) -> float:
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return max(0.0, 1.0 - elapsed / POWERUP_FIELD_DURATION)

    def draw(self, surface: pygame.Surface, font_tiny: pygame.font.Font):
        """Рисует пауэрап с пульсирующей рамкой."""
        frac = self.remaining_fraction()
        # Мигание в последние 20%
        if frac < 0.2 and (pygame.time.get_ticks() // 100) % 2 == 0:
            return

        # Пульсирующий размер рамки через синус времени
        t = pygame.time.get_ticks() / 300
        border = int(2 + 1.5 * abs(math.sin(t)))

        r = pygame.Rect(self.pos[0], self.pos[1], BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(surface, self.color, r, border_radius=5)
        pygame.draw.rect(surface, WHITE, r, border, border_radius=5)

        # Первая буква типа поверх
        lbl = font_tiny.render(self.icon if len(self.icon) == 1 else self.label[0],
                               True, BLACK)
        surface.blit(lbl, (r.centerx - lbl.get_width() // 2,
                            r.centery - lbl.get_height() // 2))


# ─────────────────────────────────────────────────────────────────
#  Основное состояние игры
# ─────────────────────────────────────────────────────────────────

class GameState:
    """
    Хранит всё состояние одной игровой сессии:
    змейку, еду, пауэрапы, препятствия, счёт, уровень.
    """

    def __init__(self, snake_color: tuple):
        self.snake_color = snake_color

        # ── Змейка ──────────────────────────────────────
        # Начальная позиция — центр поля
        start_x = (COLS // 2) * BLOCK_SIZE
        start_y = FIELD_TOP + (ROWS // 2) * BLOCK_SIZE
        self.snake = [(start_x, start_y)]   # список (px, py), голова = snake[0]
        self.direction  = (BLOCK_SIZE, 0)   # (dx, dy) в пикселях
        self.next_dir   = (BLOCK_SIZE, 0)   # Следующее направление (буферизуем)

        # ── Счёт и уровень ──────────────────────────────
        self.score         = 0
        self.level         = 1
        self.speed         = INIT_SPEED    # тиков в секунду

        # ── Таймер логического обновления ───────────────
        # Используем pygame.time.get_ticks() вместо clock.tick(speed),
        # чтобы скорость отвязать от FPS.
        self.last_move_time = pygame.time.get_ticks()

        # ── Препятствия (ДО еды — _occupied() их использует) ────────────────────
        self.obstacles: list[tuple] = []

        # ── Пауэрап (максимум 1 на поле) ────────────────
        self.powerup: PowerUp | None = None
        self.powerup_spawn_timer = pygame.time.get_ticks()
        self.powerup_spawn_interval = 10000   # каждые 10 сек пытаемся заспawnить

        # ── Активный эффект пауэрапа ─────────────────────
        self.active_effect: str | None = None   # 'speed' | 'slow' | 'shield'
        self.effect_end_time: int = 0

        # ── Щит ─────────────────────────────────────────
        self.shield_active = False   # True = следующий смертельный удар игнорируется

        # ── Флаги состояния ──────────────────────────────
        self.alive = True

        # ── Еда (в конце, после всех полей которые нужны _occupied()) ──────────
        self.foods: list[FoodItem] = []
        self._spawn_food()     # Сразу создаём первую нормальную еду

    # ── Вспомогательные методы ──────────────────────────────────

    def _occupied(self) -> list[tuple]:
        """Возвращает список всех занятых клеток (тело + препятствия + еда + пауэрап)."""
        cells = list(self.snake)
        cells += self.obstacles
        cells += [f.pos for f in self.foods]
        if self.powerup:
            cells.append(self.powerup.pos)
        return cells

    def _spawn_food(self):
        """
        Добавляет одну единицу еды на поле.
        Тип выбирается случайно с весами из FOOD_TYPES.
        """
        types  = list(FOOD_TYPES.keys())
        weights = [FOOD_TYPES[t][3] for t in types]
        chosen = random.choices(types, weights=weights, k=1)[0]
        pos = random_cell(self._occupied())
        self.foods.append(FoodItem(pos, chosen))

    def _try_spawn_powerup(self):
        """
        Спаwnит пауэрап если прошло достаточно времени и поле пустое.
        """
        now = pygame.time.get_ticks()
        if self.powerup is not None:
            return
        if now - self.powerup_spawn_timer < self.powerup_spawn_interval:
            return
        self.powerup_spawn_timer = now
        pu_type = random.choice(list(POWERUP_TYPES.keys()))
        pos = random_cell(self._occupied())
        self.powerup = PowerUp(pos, pu_type)

    def _apply_level(self):
        """
        Проверяет нужно ли повысить уровень и обновляет скорость.
        При переходе с уровня 2 на 3 — генерирует препятствия.
        """
        new_level = 1 + self.score // LEVEL_STEP
        if new_level > self.level:
            self.level = new_level
            self.speed = INIT_SPEED + (self.level - 1) * SPEED_STEP
            # Препятствия появляются начиная с уровня 3
            if self.level >= 3:
                head = self.snake[0]
                self.obstacles = obstacles_for_level(
                    self.level, head, self._occupied()
                )

    # ── Основной метод обновления ────────────────────────────────

    def update(self) -> bool:
        """
        Вызывается каждый игровой тик (не каждый кадр!).
        Обновляет позицию змейки, проверяет коллизии.
        Возвращает False если игра окончена.
        """
        now = pygame.time.get_ticks()

        # Применяем буферизованное направление
        self.direction = self.next_dir

        # Вычисляем новую позицию головы
        hx, hy = self.snake[0]
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)

        # ── Проверка: столкновение со стенами ──
        nx, ny = new_head
        if nx < 0 or nx >= WIDTH or ny < FIELD_TOP or ny >= HEIGHT:
            if self.shield_active:
                # Щит поглощает удар — телепортируемся на противоположную сторону
                nx = nx % WIDTH
                ny = FIELD_TOP + (ny - FIELD_TOP) % (HEIGHT - FIELD_TOP)
                new_head = (nx, ny)
                self.shield_active = False
                self.active_effect = None
            else:
                self.alive = False
                return False

        # ── Проверка: столкновение с препятствиями ──
        if new_head in self.obstacles:
            if self.shield_active:
                self.shield_active = False
                self.active_effect = None
            else:
                self.alive = False
                return False

        # ── Проверка: столкновение с собой ──
        if new_head in self.snake[:-1]:
            if self.shield_active:
                self.shield_active = False
                self.active_effect = None
            else:
                self.alive = False
                return False

        # Двигаем змейку: добавляем голову
        self.snake.insert(0, new_head)

        # ── Проверка еды ──
        eaten_food = None
        for food in self.foods:
            if food.pos == new_head:
                eaten_food = food
                break

        if eaten_food:
            self.foods.remove(eaten_food)
            if eaten_food.food_type == 'poison':
                # ── Яд: укорачиваем змейку на 2 ──
                self.snake = self.snake[:-2] if len(self.snake) > 3 else self.snake[:1]
                if len(self.snake) <= 1:
                    self.alive = False
                    return False
            else:
                # Обычная еда: начисляем очки, змейка не укорачивается
                self.score += eaten_food.points
                self._apply_level()
            self._spawn_food()   # Новая еда взамен съеденной
        else:
            # Еда не съедена — убираем хвост (змейка не растёт)
            self.snake.pop()

        # ── Проверка пауэрапа ──
        if self.powerup and self.powerup.pos == new_head:
            self._activate_powerup(self.powerup.pu_type)
            self.powerup = None

        # ── Удаляем просроченную еду ──
        self.foods = [f for f in self.foods if not f.is_expired()]
        # Если на поле нет еды — добавляем
        if not self.foods:
            self._spawn_food()

        # ── Проверяем просроченный пауэрап на поле ──
        if self.powerup and self.powerup.is_expired():
            self.powerup = None

        # ── Пробуем заспawnить новый пауэрап ──
        self._try_spawn_powerup()

        # ── Проверяем истечение активного эффекта ──
        if self.active_effect and now > self.effect_end_time:
            self._deactivate_effect()

        return True

    def _activate_powerup(self, pu_type: str):
        """
        Применяет эффект пауэрапа к змейке.
        """
        now = pygame.time.get_ticks()
        self.active_effect  = pu_type
        self.effect_end_time = now + POWERUP_EFFECT_DURATION

        if pu_type == 'speed':
            self.speed = min(self.speed + 5, 30)   # Ускоряем, но не более 30 т/с
        elif pu_type == 'slow':
            self.speed = max(self.speed - 4, 3)    # Замедляем, но не менее 3 т/с
        elif pu_type == 'shield':
            self.shield_active = True

    def _deactivate_effect(self):
        """Сбрасывает временный эффект, восстанавливает базовую скорость."""
        if self.active_effect in ('speed', 'slow'):
            self.speed = INIT_SPEED + (self.level - 1) * SPEED_STEP
        self.active_effect = None

    def turn(self, new_dir: tuple):
        """
        Буферизует смену направления.
        Запрещает разворот на 180°.
        """
        dx, dy = new_dir
        cdx, cdy = self.direction
        # Разворот на 180° = сумма координат равна 0 при противоположных знаках
        if (dx, dy) != (-cdx, -cdy):
            self.next_dir = new_dir

    def tick_due(self) -> bool:
        """
        Возвращает True если пришло время следующего логического тика.
        Основано на self.speed (тиков в секунду).
        """
        now = pygame.time.get_ticks()
        interval = 1000 // self.speed
        if now - self.last_move_time >= interval:
            self.last_move_time = now
            return True
        return False


# ─────────────────────────────────────────────────────────────────
#  Функции отрисовки игрового поля
# ─────────────────────────────────────────────────────────────────

def draw_grid(surface: pygame.Surface):
    """Рисует серую сетку на игровом поле (включается в настройках)."""
    for col in range(COLS):
        x = col * BLOCK_SIZE
        pygame.draw.line(surface, (40, 40, 50), (x, FIELD_TOP), (x, HEIGHT))
    for row in range(ROWS):
        y = FIELD_TOP + row * BLOCK_SIZE
        pygame.draw.line(surface, (40, 40, 50), (0, y), (WIDTH, y))


def draw_snake(surface: pygame.Surface, snake: list, color: tuple,
               shield_active: bool):
    """
    Рисует тело змейки. Голова — немного светлее.
    При активном щите добавляет свечение вокруг головы.
    """
    for i, (px, py) in enumerate(snake):
        r = pygame.Rect(px + 1, py + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2)
        if i == 0:
            # Голова светлее
            bright = tuple(min(255, c + 60) for c in color)
            pygame.draw.rect(surface, bright, r, border_radius=5)
            # Глаза
            ex = px + BLOCK_SIZE - 6
            ey = py + 5
            pygame.draw.circle(surface, (20, 20, 20), (ex, ey), 3)
            # Щит — рисуем кольцо вокруг головы
            if shield_active:
                t = pygame.time.get_ticks() / 200
                glow = (180, 255, 180)
                border = int(2 + abs(math.sin(t)) * 2)
                pygame.draw.rect(surface, glow,
                                 pygame.Rect(px, py, BLOCK_SIZE, BLOCK_SIZE),
                                 border, border_radius=6)
        else:
            # Хвост — темнее к концу
            fade = max(0.4, 1.0 - i / len(snake) * 0.5)
            faded = tuple(int(c * fade) for c in color)
            pygame.draw.rect(surface, faded, r, border_radius=3)


def draw_obstacles(surface: pygame.Surface, obstacles: list):
    """Рисует препятствия — каменные блоки."""
    for (px, py) in obstacles:
        r = pygame.Rect(px, py, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(surface, COLOR_OBSTACLE, r)
        # Светлые рёбра для объёмного вида
        pygame.draw.line(surface, (120, 120, 160), (px, py), (px + BLOCK_SIZE, py), 2)
        pygame.draw.line(surface, (120, 120, 160), (px, py), (px, py + BLOCK_SIZE), 2)


def draw_hud(surface: pygame.Surface, gs: 'GameState',
             personal_best: int, font: pygame.font.Font,
             font_small: pygame.font.Font):
    """
    Рисует верхнюю панель HUD: счёт, уровень, рекорд, активный эффект.
    """
    pygame.draw.rect(surface, PANEL_COLOR, (0, 0, WIDTH, PANEL_HEIGHT))
    pygame.draw.line(surface, COLOR_BTN_BORDER, (0, PANEL_HEIGHT), (WIDTH, PANEL_HEIGHT), 1)

    # Счёт
    sc = font.render(f"Score: {gs.score}", True, WHITE)
    surface.blit(sc, (10, 12))

    # Уровень
    lv = font.render(f"Level: {gs.level}", True, COLOR_ACCENT)
    surface.blit(lv, (WIDTH // 2 - lv.get_width() // 2, 12))

    # Личный рекорд
    pb = font_small.render(f"Best: {personal_best}", True, GRAY)
    surface.blit(pb, (WIDTH - pb.get_width() - 10, 5))

    # Длина змейки
    ln = font_small.render(f"Len: {len(gs.snake)}", True, GRAY)
    surface.blit(ln, (WIDTH - ln.get_width() - 10, 22))

    # Активный эффект пауэрапа
    if gs.active_effect:
        color, label, icon = POWERUP_TYPES[gs.active_effect]
        now = pygame.time.get_ticks()
        remaining = max(0, gs.effect_end_time - now) // 1000
        eff_text = font_small.render(f"{label} {remaining}s", True, color)
        surface.blit(eff_text, (WIDTH // 2 - eff_text.get_width() // 2, 32))