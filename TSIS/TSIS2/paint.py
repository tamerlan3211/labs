
import pygame
import sys
from datetime import datetime
from tools import (
    draw_object,
    flood_fill,
    render_text_preview,
    render_text_final,
)

# ─────────────────────────────────────────────
#  Константы
# ─────────────────────────────────────────────

WIDTH, HEIGHT = 1000, 700
TOOLBAR_W = 160          # ширина левой панели инструментов

# Цветовая палитра
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
RED     = (255, 0,   0)
GREEN   = (0,   200, 0)
BLUE    = (0,   100, 255)
YELLOW  = (255, 220, 0)
ORANGE  = (255, 140, 0)
PURPLE  = (160, 0,   200)
CYAN    = (0,   220, 220)
PINK    = (255, 100, 180)

# Доступные цвета в палитре
PALETTE = [BLACK, WHITE, RED, GREEN, BLUE,
           YELLOW, ORANGE, PURPLE, CYAN, PINK]

# Все режимы рисования
MODES = [
    'brush',               # Кисть
    'pencil',              # Карандаш (тонкий)
    'line',                # Прямая линия
    'rectangle',           # Прямоугольник
    'square',              # Квадрат
    'circle',              # Окружность
    'right_triangle',      # Прямоугольный треугольник
    'equilateral_triangle',# Равносторонний треугольник
    'rhombus',             # Ромб
    'eraser',              # Ластик
    'fill',                # Заливка
    'text',                # Текст
]

# Метки режимов для отображения в панели
MODE_LABELS = {
    'brush':               'Кисть',
    'pencil':              'Карандаш',
    'line':                'Линия',
    'rectangle':           'Прямоугольник',
    'square':              'Квадрат',
    'circle':              'Окружность',
    'right_triangle':      'Пр. треугольник',
    'equilateral_triangle':'Рав. треугольник',
    'rhombus':             'Ромб',
    'eraser':              'Ластик',
    'fill':                'Заливка',
    'text':                'Текст',
}

# Три уровня толщины кисти (радиус)
SIZE_SMALL  = 2
SIZE_MEDIUM = 5
SIZE_LARGE  = 10

# Цвет фона холста — меняй здесь: (255,255,255) = белый, (30,30,30) = тёмный
CANVAS_BG = (255, 255, 255)

# Цвет фона панели инструментов
TOOLBAR_BG = (45, 45, 55)


# ─────────────────────────────────────────────
#  Вспомогательные функции UI
# ─────────────────────────────────────────────

def draw_toolbar(surface, mode, color, radius, font_sm, font_tiny):
    # """
    # Рисует левую панель инструментов:
    # - кнопки режимов
    # - текущий цвет
    # - палитра
    # - размеры кисти
    # """
    pygame.draw.rect(surface, TOOLBAR_BG, (0, 0, TOOLBAR_W, HEIGHT))
    pygame.draw.line(surface, (80, 80, 100), (TOOLBAR_W, 0), (TOOLBAR_W, HEIGHT), 2)

    y = 10

    # ── Заголовок ──
    title = font_sm.render('PAINT', True, (200, 200, 255))
    surface.blit(title, (TOOLBAR_W // 2 - title.get_width() // 2, y))
    y += 28
    pygame.draw.line(surface, (80, 80, 100), (8, y), (TOOLBAR_W - 8, y), 1)
    y += 8

    # ── Кнопки инструментов ──
    btn_h = 26
    btn_margin = 3
    for m in MODES:
        active = (m == mode)
        color_btn = (70, 130, 200) if active else (60, 60, 75)
        btn_rect = pygame.Rect(6, y, TOOLBAR_W - 12, btn_h)
        pygame.draw.rect(surface, color_btn, btn_rect, border_radius=5)
        if active:
            pygame.draw.rect(surface, (120, 180, 255), btn_rect, 2, border_radius=5)
        label = font_tiny.render(MODE_LABELS[m], True, WHITE)
        surface.blit(label, (btn_rect.x + 6, btn_rect.y + (btn_h - label.get_height()) // 2))
        y += btn_h + btn_margin

    y += 6
    pygame.draw.line(surface, (80, 80, 100), (8, y), (TOOLBAR_W - 8, y), 1)
    y += 8

    # ── Текущий цвет ──
    lbl = font_tiny.render('Цвет:', True, (180, 180, 180))
    surface.blit(lbl, (8, y))
    y += 16
    pygame.draw.rect(surface, color, (8, y, TOOLBAR_W - 16, 22), border_radius=4)
    pygame.draw.rect(surface, WHITE, (8, y, TOOLBAR_W - 16, 22), 1, border_radius=4)
    y += 28

    # ── Палитра ──
    lbl2 = font_tiny.render('Палитра:', True, (180, 180, 180))
    surface.blit(lbl2, (8, y))
    y += 16
    swatch = 18
    gap = 4
    per_row = (TOOLBAR_W - 16) // (swatch + gap)
    for i, c in enumerate(PALETTE):
        col = i % per_row
        row = i // per_row
        rx = 8 + col * (swatch + gap)
        ry = y + row * (swatch + gap)
        pygame.draw.rect(surface, c, (rx, ry, swatch, swatch), border_radius=3)
        if c == color:
            pygame.draw.rect(surface, WHITE, (rx, ry, swatch, swatch), 2, border_radius=3)
    rows = (len(PALETTE) + per_row - 1) // per_row
    y += rows * (swatch + gap) + 4

    pygame.draw.line(surface, (80, 80, 100), (8, y), (TOOLBAR_W - 8, y), 1)
    y += 8

    # ── Размер кисти ──
    lbl3 = font_tiny.render('Размер (S/M/L):', True, (180, 180, 180))
    surface.blit(lbl3, (8, y))
    y += 16
    sizes = [('S', SIZE_SMALL), ('M', SIZE_MEDIUM), ('L', SIZE_LARGE)]
    sx = 8
    for label_s, sz in sizes:
        active_sz = (sz == radius)
        cbtn = (70, 130, 200) if active_sz else (60, 60, 75)
        bw = (TOOLBAR_W - 16 - 8) // 3
        srect = pygame.Rect(sx, y, bw, 26)
        pygame.draw.rect(surface, cbtn, srect, border_radius=5)
        if active_sz:
            pygame.draw.rect(surface, (120, 180, 255), srect, 2, border_radius=5)
        sl = font_tiny.render(label_s, True, WHITE)
        surface.blit(sl, (srect.centerx - sl.get_width() // 2,
                          srect.centery - sl.get_height() // 2))
        sx += bw + 4
    y += 30

    # ── Подсказки ──
    pygame.draw.line(surface, (80, 80, 100), (8, y), (TOOLBAR_W - 8, y), 1)
    y += 6
    hints = [
        'Ctrl+S — сохранить',
        'Ctrl+Z — отмена',
        'Del — очистить',
    ]
    for h in hints:
        hl = font_tiny.render(h, True, (140, 140, 160))
        surface.blit(hl, (8, y))
        y += 14

    return  # Возвращаем информацию о расположении кнопок для кликов


def get_toolbar_click(mx, my):
    """
    Определяет, на какой элемент тулбара кликнул пользователь.
    Возвращает ('mode', mode_name), ('color', color), ('size', radius) или None.
    y считается ТОЧНО так же как в draw_toolbar — строка в строку.
    """
    if mx >= TOOLBAR_W:
        return None

    # draw_toolbar: y = 10
    y = 10
    # y += 28  (заголовок)
    y += 28
    # pygame.draw.line(...)  ← не меняет y
    # y += 8
    y += 8

    btn_h = 26
    btn_margin = 3

    # for m in MODES: ... y += btn_h + btn_margin
    for m in MODES:
        btn_rect = pygame.Rect(6, y, TOOLBAR_W - 12, btn_h)
        if btn_rect.collidepoint(mx, my):
            return ('mode', m)
        y += btn_h + btn_margin

    # y += 6  (перед разделителем)
    y += 6
    # pygame.draw.line(...)  ← не меняет y
    # y += 8
    y += 8

    # «Цвет:» — y += 16
    y += 16
    # pygame.draw.rect(цветной блок)  ← не меняет y
    # pygame.draw.rect(рамка)         ← не меняет y
    # y += 28
    y += 28

    # «Палитра:» — y += 16
    y += 16
    swatch = 18
    gap = 4
    per_row = (TOOLBAR_W - 16) // (swatch + gap)
    for i, c in enumerate(PALETTE):
        col = i % per_row
        row = i // per_row
        rx = 8 + col * (swatch + gap)
        ry = y + row * (swatch + gap)
        if rx <= mx < rx + swatch and ry <= my < ry + swatch:
            return ('color', c)
    rows = (len(PALETTE) + per_row - 1) // per_row
    # y += rows * (swatch + gap) + 4
    y += rows * (swatch + gap) + 4

    # pygame.draw.line(разделитель)  ← не меняет y
    # y += 8
    y += 8

    # «Размер:» — y += 16
    y += 16
    bw = (TOOLBAR_W - 16 - 8) // 3
    sx = 8
    for _, sz in [('S', SIZE_SMALL), ('M', SIZE_MEDIUM), ('L', SIZE_LARGE)]:
        srect = pygame.Rect(sx, y, bw, 26)
        if srect.collidepoint(mx, my):
            return ('size', sz)
        sx += bw + 4

    return None


# ─────────────────────────────────────────────
#  Основной цикл
# ─────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Paint — Практика 12')
    clock = pygame.time.Clock()

    # ── Шрифты ──
    font_sm   = pygame.font.SysFont('Arial', 16, bold=True)
    font_tiny = pygame.font.SysFont('Arial', 13)
    font_text = pygame.font.SysFont('Arial', 24)  # для текстового инструмента

    # ── Холст — отдельный Surface, чтобы заливка работала на нём ──
    canvas = pygame.Surface((WIDTH - TOOLBAR_W, HEIGHT))
    canvas.fill(CANVAS_BG)

    # ── Состояние приложения ──
    mode    = 'brush'
    color   = BLUE
    radius  = SIZE_MEDIUM
    drawing = False

    # Список завершённых объектов для перерисовки
    objects = []
    # Стек для Ctrl+Z
    undo_stack = []

    current_object = None  # Объект, рисуемый в данный момент
    start_pos      = None

    # ── Текстовый инструмент ──
    text_active = False   # Режим набора текста включён?
    text_obj    = None    # Текущий объект текста

    # ─────────────────────────────────────────
    #  Главный цикл
    # ─────────────────────────────────────────
    running = True
    while running:
        # ── Обработка событий ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ────────────────────────
            #  Клавиатура
            # ────────────────────────
            if event.type == pygame.KEYDOWN:

                # Если активен текстовый инструмент — перехватываем ввод
                if text_active and text_obj is not None:
                    if event.key == pygame.K_RETURN:
                        # Подтверждаем текст: рисуем на холсте навсегда
                        render_text_final(canvas, text_obj, font_text)
                        text_active = False
                        text_obj    = None
                    elif event.key == pygame.K_ESCAPE:
                        # Отмена ввода
                        text_active = False
                        text_obj    = None
                    elif event.key == pygame.K_BACKSPACE:
                        text_obj['text'] = text_obj['text'][:-1]
                    else:
                        # Добавляем введённый символ
                        if event.unicode:
                            text_obj['text'] += event.unicode
                    continue  # Остальные хоткеи не обрабатываем в режиме текста

                # ── Ctrl+S — сохранить ──
                mods = pygame.key.get_mods()
                if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename  = f'canvas_{timestamp}.png'
                    pygame.image.save(canvas, filename)
                    print(f'[Сохранено] {filename}')

                # ── Ctrl+Z — отмена последнего действия ──
                elif event.key == pygame.K_z and (mods & pygame.KMOD_CTRL):
                    if undo_stack:
                        # Восстанавливаем холст из снимка
                        canvas.blit(undo_stack.pop(), (0, 0))
                        if objects:
                            objects.pop()

                # ── Del — очистить холст ──
                elif event.key == pygame.K_DELETE:
                    undo_stack.append(canvas.copy())
                    canvas.fill(CANVAS_BG)
                    objects.clear()

                # ── Переключение размера кисти: S / M / L ──
                elif event.key == pygame.K_s and not (mods & pygame.KMOD_CTRL):
                    radius = SIZE_SMALL
                elif event.key == pygame.K_m:
                    radius = SIZE_MEDIUM
                elif event.key == pygame.K_l:
                    radius = SIZE_LARGE

            # ────────────────────────
            #  Клик мышью
            # ────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Клик по тулбару
                if mx < TOOLBAR_W:
                    result = get_toolbar_click(mx, my)
                    if result:
                        kind, val = result
                        if kind == 'mode':
                            mode = val
                            # Завершаем текстовый режим при смене инструмента
                            text_active = False
                            text_obj    = None
                        elif kind == 'color':
                            color = val
                        elif kind == 'size':
                            radius = val
                    continue  # Больше ничего не обрабатываем

                # Клик по холсту — пересчитываем координаты относительно холста
                cx = mx - TOOLBAR_W
                cy = my

                # ── Заливка ──
                if mode == 'fill':
                    undo_stack.append(canvas.copy())
                    flood_fill(canvas, (cx, cy), color)

                # ── Текстовый инструмент ──
                elif mode == 'text':
                    if not text_active:
                        text_active = True
                        text_obj    = {'pos': (cx, cy), 'text': '', 'color': color}
                    else:
                        # Второй клик подтверждает и начинает новый текст
                        render_text_final(canvas, text_obj, font_text)
                        text_active = True
                        text_obj    = {'pos': (cx, cy), 'text': '', 'color': color}

                # ── Начало рисования фигуры ──
                else:
                    drawing   = True
                    start_pos = (cx, cy)

                    if mode in ('brush', 'pencil'):
                        draw_radius = radius if mode == 'brush' else 1
                        current_object = {
                            'type':   'brush',
                            'points': [start_pos],
                            'color':  color,
                            'radius': draw_radius,
                        }
                    elif mode == 'eraser':
                        current_object = {
                            'type':   'brush',
                            'points': [start_pos],
                            'color':  CANVAS_BG,
                            'radius': radius * 2,  # Ластик шире кисти
                        }
                    else:
                        # Все фигуры с двумя точками (start/end)
                        current_object = {
                            'type':  mode,
                            'start': start_pos,
                            'end':   start_pos,
                            'color': color,
                            'radius': radius,
                        }

            # ────────────────────────
            #  Движение мыши
            # ────────────────────────
            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my = event.pos
                cx = mx - TOOLBAR_W
                cy = my
                if current_object:
                    if current_object['type'] == 'brush':
                        current_object['points'].append((cx, cy))
                    else:
                        current_object['end'] = (cx, cy)

            # ────────────────────────
            #  Отпускание кнопки мыши
            # ────────────────────────
            if event.type == pygame.MOUSEBUTTONUP and drawing:
                if current_object:
                    # Сохраняем снимок перед добавлением объекта
                    undo_stack.append(canvas.copy())
                    # Рисуем объект на холсте (постоянно)
                    draw_object(canvas, current_object)
                    objects.append(current_object)
                drawing        = False
                current_object = None

        # ─────────────────────────────────────
        #  Отрисовка кадра
        # ─────────────────────────────────────

        # Копируем холст на экран
        screen.blit(canvas, (TOOLBAR_W, 0))

        # Превью текущего объекта (пока рисуем)
        if drawing and current_object:
            # Рисуем превью поверх холста прямо на screen
            temp = canvas.copy()
            draw_object(temp, current_object)
            screen.blit(temp, (TOOLBAR_W, 0))

        # Превью текста в режиме набора
        if text_active and text_obj:
            temp_pos = (text_obj['pos'][0] + TOOLBAR_W, text_obj['pos'][1])
            tmp_obj  = dict(text_obj, pos=temp_pos)
            render_text_preview(screen, tmp_obj, font_text)

        # Рисуем тулбар поверх всего
        draw_toolbar(screen, mode, color, radius, font_sm, font_tiny)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()