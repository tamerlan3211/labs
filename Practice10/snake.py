import pygame
import random

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 600, 400
BLOCK_SIZE = 20
WHITE = (255, 255, 255)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

display = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def game_loop():
    game_over = False
    
    # Начальные координаты змейки
    x, y = WIDTH // 2, HEIGHT // 2
    x_speed, y_speed = 0, 0
    
    snake_pixels = []
    snake_length = 1
    
    # Состояние игры
    score = 0
    level = 1
    speed = 10
    
    # Функция для генерации еды, чтобы она не попадала на змейку
    def generate_food(snake_body):
        while True:
            food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            food_y = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            # Проверка: не пересекается ли еда с телом змейки
            if [food_x, food_y] not in snake_body:
                return food_x, food_y

    food_x, food_y = generate_food(snake_pixels)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x_speed == 0:
                    x_speed = -BLOCK_SIZE
                    y_speed = 0
                elif event.key == pygame.K_RIGHT and x_speed == 0:
                    x_speed = BLOCK_SIZE
                    y_speed = 0
                elif event.key == pygame.K_UP and y_speed == 0:
                    y_speed = -BLOCK_SIZE
                    x_speed = 0
                elif event.key == pygame.K_DOWN and y_speed == 0:
                    y_speed = BLOCK_SIZE
                    x_speed = 0

        # --- ЛОГИКА ДВИЖЕНИЯ ---
        x += x_speed
        y += y_speed

        # --- 1. ПРОВЕРКА СТОЛКНОВЕНИЯ С ГРАНИЦАМИ (WALL COLLISION) ---
        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_over = True

        display.fill(BLACK)
        
        # Отрисовка еды
        pygame.draw.rect(display, RED, [food_x, food_y, BLOCK_SIZE, BLOCK_SIZE])

        # Логика роста змейки
        snake_pixels.append([x, y])
        if len(snake_pixels) > snake_length:
            del snake_pixels[0]

        # ПРОВЕРКА СТОЛКНОВЕНИЯ С СОБОЙ
        for pixel in snake_pixels[:-1]:
            if pixel == [x, y]:
                game_over = True

        # Отрисовка змейки
        for pixel in snake_pixels:
            pygame.draw.rect(display, GREEN, [pixel[0], pixel[1], BLOCK_SIZE, BLOCK_SIZE])

        # --- 2. ПРОВЕРКА ПОЕДАНИЯ ЕДЫ ---
        if x == food_x and y == food_y:
            food_x, food_y = generate_food(snake_pixels) # Генерируем новую еду
            snake_length += 1
            score += 1
            
            # --- 3. СИСТЕМА УРОВНЕЙ ---
            # Повышаем уровень каждые 3 съеденные еды
            if score % 3 == 0:
                level += 1
                speed += 2 # --- 4. УВЕЛИЧЕНИЕ СКОРОСТИ ---

        # --- 5. ОТОБРАЖЕНИЕ СЧЕТА И УРОВНЯ ---
        font = pygame.font.SysFont("comicsansms", 25)
        score_text = font.render(f"Score: {score}  Level: {level}", True, WHITE)
        display.blit(score_text, [10, 10])

        pygame.display.update()
        clock.tick(speed)

    pygame.quit()

game_loop()