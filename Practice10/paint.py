import pygame

# Инициализация
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def main():
    radius = 5
    drawing = False
    mode = 'brush'  # Режимы: brush, rectangle, circle, eraser
    color = BLUE
    
    # Список всех нарисованных объектов
    # Формат: {'type': 'line', 'points': [...], 'color': (R,G,B), 'radius': 15}
    objects = []
    
    # Текущий объект, который мы рисуем прямо сейчас
    current_object = None
    start_pos = None

    while True:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                # Переключение режимов (Инструменты)
                if event.key == pygame.K_1: mode = 'brush'
                if event.key == pygame.K_2: mode = 'rectangle'
                if event.key == pygame.K_3: mode = 'circle'
                if event.key == pygame.K_4: mode = 'eraser'
                
                # Выбор цвета
                if event.key == pygame.K_r: color = RED
                if event.key == pygame.K_g: color = GREEN
                if event.key == pygame.K_b: color = BLUE
                if event.key == pygame.K_w: color = WHITE

            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                start_pos = event.pos
                
                if mode == 'brush':
                    current_object = {'type': 'brush', 'points': [start_pos], 'color': color, 'radius': radius}
                elif mode == 'eraser':
                    current_object = {'type': 'brush', 'points': [start_pos], 'color': BLACK, 'radius': radius}
                elif mode in ['rectangle', 'circle']:
                    current_object = {'type': mode, 'start': start_pos, 'end': start_pos, 'color': color, 'radius': radius}

            if event.type == pygame.MOUSEMOTION and drawing:
                if mode in ['brush', 'eraser']:
                    current_object['points'].append(event.pos)
                elif mode in ['rectangle', 'circle']:
                    current_object['end'] = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if drawing:
                    objects.append(current_object)
                    drawing = False
                    current_object = None

        # --- ОТРИСОВКА ---
        
        # Рисуем все сохраненные объекты
        for obj in objects + ([current_object] if current_object else []):
            if obj['type'] == 'brush':
                draw_brush(screen, obj)
            elif obj['type'] == 'rectangle':
                draw_rect(screen, obj)
            elif obj['type'] == 'circle':
                draw_circle(screen, obj)

        # Инструкция на экране
        font = pygame.font.SysFont("Arial", 18)
        help_text = "1: Brush | 2: Rect | 3: Circle | 4: Eraser | R/G/B/W: Colors"
        img = font.render(help_text, True, WHITE)
        screen.blit(img, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)

def draw_brush(screen, obj):
    """Отрисовка плавной линии для кисти и ластика"""
    for i in range(len(obj['points']) - 1):
        p1, p2 = obj['points'][i], obj['points'][i+1]
        pygame.draw.line(screen, obj['color'], p1, p2, obj['radius'] * 2)
        pygame.draw.circle(screen, obj['color'], p1, obj['radius'])
        pygame.draw.circle(screen, obj['color'], p2, obj['radius'])

def draw_rect(screen, obj):
    """Отрисовка прямоугольника по двум точкам"""
    x1, y1 = obj['start']
    x2, y2 = obj['end']
    rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))
    if rect.width > 0 and rect.height > 0:
        pygame.draw.rect(screen, obj['color'], rect, obj['radius'] // 5 + 1)

def draw_circle(screen, obj):
    """Отрисовка круга (радиус — расстояние от центра до мышки)"""
    x1, y1 = obj['start']
    x2, y2 = obj['end']
    # Считаем расстояние между точками как радиус
    r = int(((x1 - x2)**2 + (y1 - y2)**2)**0.5)
    if r > 0:
        pygame.draw.circle(screen, obj['color'], (x1, y1), r, obj['radius'] // 5 + 1)

if __name__ == "__main__":
    main()