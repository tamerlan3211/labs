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

    
    base_path = os.path.dirname(__file__)
    
    
    def load_resource(filenames):
        for name in filenames:
            path = os.path.join(base_path, name)
            if os.path.exists(path):
                return pygame.image.load(path)
        
        for name in filenames:
            path = os.path.join(os.path.dirname(base_path), name)
            if os.path.exists(path):
                return pygame.image.load(path)
        return None


    mick_img = load_resource(["mickeyclock.jpeg", "mickeyclock.jpg"])
    hand_raw = load_resource(["стрелкапнг.png", "arrow.png"])

    if mick_img is None or hand_raw is None:
        print("Ошибка: Картинки не найдены! Проверь, что они лежат в папке с часами.")
        return 

    mick = pygame.transform.scale(mick_img, (700, 700))
   
    hand_img = pygame.transform.scale(hand_raw, (100, 550)) # секундная
    strelka = pygame.transform.scale(hand_raw, (100, 450))  # минутная
    strelka2 = pygame.transform.scale(hand_raw, (100, 300)) # часовая

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 

        screen.blit(mick, (0, 0))  

        now = datetime.datetime.now()
        minute_angle = -(now.minute * 6)
        second_angle = -(now.second * 6)
        hour_angle = -(now.hour % 12 * 30 + now.minute * 0.5)

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
