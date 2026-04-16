import pygame
import sys
import datetime
import os

def rotate(image, angle, center):
    rotated = pygame.transform.rotate(image, angle)
    rect = rotated.get_rect(center=center)
    return rotated, rect

def main():
    pygame.init()
    WIDTH, HEIGHT = 700, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mickey Clock")
    clock = pygame.time.Clock()
    center = (WIDTH // 2, HEIGHT // 2)

    # Умный путь: ищем папку, где лежит ЭТОТ файл
    base_path = os.path.dirname(__file__)
    
    # Функция для загрузки, которая проверяет и .jpg и .jpeg
    def load_resource(filenames):
        for name in filenames:
            path = os.path.join(base_path, name)
            if os.path.exists(path):
                return pygame.image.load(path)
        # Если ничего не нашли, попробуем поискать на уровень выше (в Practice9)
        for name in filenames:
            path = os.path.join(os.path.dirname(base_path), name)
            if os.path.exists(path):
                return pygame.image.load(path)
        return None

    # Загружаем (проверяем оба варианта расширения)
    mick_img = load_resource(["mickeyclock.jpeg", "mickeyclock.jpg"])
    hand_raw = load_resource(["стрелкапнг.png", "arrow.png"])

    if mick_img is None or hand_raw is None:
        print("Ошибка: Картинки не найдены! Проверь, что они лежат в папке с часами.")
        return # Возвращаемся в меню

    mick = pygame.transform.scale(mick_img, (700, 700))
    # Масштабируем разные стрелки из одной картинки
    hand_img = pygame.transform.scale(hand_raw, (100, 550)) # секундная
    strelka = pygame.transform.scale(hand_raw, (100, 450))  # минутная
    strelka2 = pygame.transform.scale(hand_raw, (100, 300)) # часовая

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return # Возврат в меню вместо полного выхода sys.exit()

        screen.blit(mick, (0, 0))  

        now = datetime.datetime.now()
        minute_angle = -(now.minute * 6)
        second_angle = -(now.second * 6)
        hour_angle = -(now.hour % 12 * 30 + now.minute * 0.5)

        # 🔹 ТУТ ИСПРАВЛЕНО: добавил center
        minute_hand, minute_rect = rotate(strelka, minute_angle, center)
        second_hand, second_rect = rotate(hand_img, second_angle, center)
        hour_hand, hour_rect = rotate(strelka2, hour_angle, center)

        screen.blit(minute_hand, minute_rect)
        screen.blit(second_hand, second_rect)
        screen.blit(hour_hand, hour_rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()

# def rotate(image, angle):
#     rotated = pygame.transform.rotate(image, angle)
#     rect = rotated.get_rect(center=center)
#     return rotated, rect
