import pygame
import sys

def main():
    
    pygame.init()

    WIDTH, HEIGHT = 700, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ball")

    WHITE = (255, 255, 255)
    RED = (255, 0, 0)

    radius = 25
    x = WIDTH // 2
    y = HEIGHT // 2
    speed = 10 # Можно сделать чуть быстрее :)

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                
                return 

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            if x - speed - radius >= 0:
                x -= speed

        if keys[pygame.K_RIGHT]:
            if x + speed + radius <= WIDTH:
                x += speed

        if keys[pygame.K_UP]:
            if y - speed - radius >= 0:
                y -= speed

        if keys[pygame.K_DOWN]:
            if y + speed + radius <= HEIGHT:
                y += speed

        screen.fill(WHITE)
        pygame.draw.circle(screen, RED, (x, y), radius)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()