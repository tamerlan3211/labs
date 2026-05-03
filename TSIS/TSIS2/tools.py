"""
tools.py — Вспомогательные инструменты для Paint-приложения.
Содержит функции отрисовки фигур, заливки и работы с текстом.
"""

import pygame
import math
from collections import deque


# ─────────────────────────────────────────────
#  Кисть / карандаш / ластик
# ─────────────────────────────────────────────

def draw_brush(surface, obj):
    """
    Рисует плавную линию по набору точек.
    Используется для кисти, карандаша и ластика.
    """
    pts = obj['points']
    if len(pts) == 1:
        # Одиночная точка — просто кружок
        pygame.draw.circle(surface, obj['color'], pts[0], obj['radius'])
        return
    for i in range(len(pts) - 1):
        p1, p2 = pts[i], pts[i + 1]
        pygame.draw.line(surface, obj['color'], p1, p2, obj['radius'] * 2)
        pygame.draw.circle(surface, obj['color'], p1, obj['radius'])
    # Закрываем последнюю точку
    pygame.draw.circle(surface, obj['color'], pts[-1], obj['radius'])


# ─────────────────────────────────────────────
#  Прямая линия
# ─────────────────────────────────────────────

def draw_line(surface, obj):
    """Рисует прямую линию от start до end с заданной толщиной."""
    thickness = max(1, obj['radius'] * 2)
    pygame.draw.line(surface, obj['color'], obj['start'], obj['end'], thickness)


# ─────────────────────────────────────────────
#  Прямоугольник
# ─────────────────────────────────────────────

def draw_rect(surface, obj):
    """
    Рисует прямоугольник по двум угловым точкам.
    Толщина рамки вычисляется из obj['radius'].
    """
    x1, y1 = obj['start']
    x2, y2 = obj['end']
    rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))
    if rect.width > 0 and rect.height > 0:
        thickness = max(1, obj['radius'] // 3 + 1)
        pygame.draw.rect(surface, obj['color'], rect, thickness)


# ─────────────────────────────────────────────
#  Квадрат
# ─────────────────────────────────────────────

def draw_square(surface, obj):
    """
    Рисует квадрат: сторона = минимум из ширины и высоты выделения,
    отсчитывается от start по направлению к end.
    """
    x1, y1 = obj['start']
    x2, y2 = obj['end']
    side = min(abs(x1 - x2), abs(y1 - y2))
    # Определяем направление по осям
    dx = 1 if x2 >= x1 else -1
    dy = 1 if y2 >= y1 else -1
    rect = pygame.Rect(min(x1, x1 + dx * side),
                       min(y1, y1 + dy * side),
                       side, side)
    if side > 0:
        thickness = max(1, obj['radius'] // 3 + 1)
        pygame.draw.rect(surface, obj['color'], rect, thickness)


# ─────────────────────────────────────────────
#  Окружность
# ─────────────────────────────────────────────

def draw_circle(surface, obj):
    """
    Рисует окружность: центр = start, радиус = расстояние до end.
    """
    x1, y1 = obj['start']
    x2, y2 = obj['end']
    r = int(math.hypot(x1 - x2, y1 - y2))
    if r > 0:
        thickness = max(1, obj['radius'] // 3 + 1)
        pygame.draw.circle(surface, obj['color'], (x1, y1), r, thickness)


# ─────────────────────────────────────────────
#  Прямоугольный треугольник
# ─────────────────────────────────────────────

def draw_right_triangle(surface, obj):
    """
    Рисует прямоугольный треугольник.
    Прямой угол — в точке start.
    Вершины: start, (end.x, start.y), end.
    """
    x1, y1 = obj['start']
    x2, y2 = obj['end']
    thickness = max(1, obj['radius'] // 3 + 1)
    points = [
        (x1, y1),        # прямой угол
        (x2, y1),        # по горизонтали
        (x2, y2),        # конечная точка
    ]
    pygame.draw.polygon(surface, obj['color'], points, thickness)


# ─────────────────────────────────────────────
#  Равносторонний треугольник
# ─────────────────────────────────────────────

def draw_equilateral_triangle(surface, obj):
    """
    Рисует равносторонний треугольник.
    Основание: горизонтальный отрезок от start до (end.x, start.y).
    Вершина: посередине основания, смещена вверх на высоту треугольника.
    """
    x1, y1 = obj['start']
    x2, y2 = obj['end']
    side = abs(x2 - x1)
    if side == 0:
        return
    # Высота равностороннего треугольника: h = side * sqrt(3) / 2
    height = int(side * math.sqrt(3) / 2)
    # Направление вершины — вверх или вниз в зависимости от drag-направления
    direction = -1 if y2 <= y1 else 1
    mid_x = (x1 + x2) // 2
    points = [
        (x1, y1),
        (x2, y1),
        (mid_x, y1 + direction * height),
    ]
    thickness = max(1, obj['radius'] // 3 + 1)
    pygame.draw.polygon(surface, obj['color'], points, thickness)


# ─────────────────────────────────────────────
#  Ромб
# ─────────────────────────────────────────────

def draw_rhombus(surface, obj):
    """
    Рисует ромб по диагонали start→end.
    Центр — середина диагонали, диагонали равны по длине.
    """
    x1, y1 = obj['start']
    x2, y2 = obj['end']
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    dx = abs(x2 - x1) // 2
    dy = abs(y2 - y1) // 2
    if dx == 0 and dy == 0:
        return
    # Четыре вершины ромба: верх, право, низ, лево
    points = [
        (cx,      cy - dy),  # верхняя
        (cx + dx, cy),       # правая
        (cx,      cy + dy),  # нижняя
        (cx - dx, cy),       # левая
    ]
    thickness = max(1, obj['radius'] // 3 + 1)
    pygame.draw.polygon(surface, obj['color'], points, thickness)


# ─────────────────────────────────────────────
#  Универсальная функция отрисовки объекта
# ─────────────────────────────────────────────

# Карта: тип объекта → функция рисования
DRAW_FUNCS = {
    'brush':               draw_brush,
    'line':                draw_line,
    'rectangle':           draw_rect,
    'square':              draw_square,
    'circle':              draw_circle,
    'right_triangle':      draw_right_triangle,
    'equilateral_triangle': draw_equilateral_triangle,
    'rhombus':             draw_rhombus,
}


def draw_object(surface, obj):
    """Отрисовывает любой объект через таблицу DRAW_FUNCS."""
    func = DRAW_FUNCS.get(obj['type'])
    if func:
        func(surface, obj)


# ─────────────────────────────────────────────
#  Заливка (Flood Fill)
# ─────────────────────────────────────────────

def flood_fill(surface, pos, fill_color):
    """
    Заливка замкнутой области методом BFS (обход в ширину).
    Заменяет все пиксели целевого цвета на fill_color,
    начиная с точки pos.

    :param surface:    pygame.Surface — холст
    :param pos:        (x, y) — начальная точка
    :param fill_color: (R, G, B) — цвет заливки
    """
    x, y = pos
    w, h = surface.get_size()

    # Цвет, который заменяем
    target_color = surface.get_at((x, y))[:3]  # без альфа-канала

    # Если кликнули на тот же цвет — ничего не делаем
    if target_color == fill_color[:3]:
        return

    # BFS по пикселям
    queue = deque()
    queue.append((x, y))
    visited = set()
    visited.add((x, y))

    while queue:
        cx, cy = queue.popleft()
        # Проверяем, что пиксель нужного цвета
        if surface.get_at((cx, cy))[:3] != target_color:
            continue
        surface.set_at((cx, cy), fill_color)

        # Добавляем соседей (4-связность)
        for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))


# ─────────────────────────────────────────────
#  Отрисовка текста
# ─────────────────────────────────────────────

def render_text_preview(surface, text_obj, font):
    """
    Отрисовывает мигающий курсор и набираемый текст в режиме редактирования.
    text_obj — словарь {'pos': (x,y), 'text': str, 'color': ...}
    """
    # Рендерим набранный текст
    rendered = font.render(text_obj['text'] + '|', True, text_obj['color'])
    surface.blit(rendered, text_obj['pos'])


def render_text_final(surface, text_obj, font):
    """
    Окончательно рисует текст на холсте (без курсора).
    """
    if text_obj['text']:
        rendered = font.render(text_obj['text'], True, text_obj['color'])
        surface.blit(rendered, text_obj['pos'])
