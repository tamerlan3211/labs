import pygame
import os


def main():
    pygame.init()
    pygame.mixer.init()

    WIDTH, HEIGHT = 700, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Music Player")

    font = pygame.font.SysFont(None, 30)

    # Папка с музыкой
    music_folder = os.path.join(os.path.dirname(__file__), "music")

    # Плейлист
    playlist = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]

    if not playlist:
        print("No music files found")
        return

    current = 0
    playing = False
    paused = False

    def load_track(index):
        path = os.path.join(music_folder, playlist[index])
        pygame.mixer.music.load(path)

    load_track(current)

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if not playing:
                        pygame.mixer.music.play()
                        playing = True
                        paused = False
                    else:
                        if paused:
                            pygame.mixer.music.unpause()
                            paused = False
                        else:
                            pygame.mixer.music.pause()
                            paused = True
            
            

                elif event.key == pygame.K_s:
                    pygame.mixer.music.stop()
                    playing = False
                    paused = False

                elif event.key == pygame.K_n:
                    current = (current + 1) % len(playlist)
                    load_track(current)
                    pygame.mixer.music.play()
                    playing = True
                    paused = False

                elif event.key == pygame.K_b:
                    current = (current - 1) % len(playlist)
                    load_track(current)
                    pygame.mixer.music.play()
                    playing = True
                    paused = False

                elif event.key == pygame.K_q:
                    pygame.mixer.music.stop()
                    pygame.quit()
                    return
                

        # --- позиция трека
        pos = pygame.mixer.music.get_pos() // 1000

        # --- отрисовка
        screen.fill((105, 105, 105))

        track_name = playlist[current]

        if not playing:
            status = "Stopped"
        elif paused:
            status = "Paused"
        else:
            status = "Playing"

        text1 = font.render(f"Track: {track_name}", True, (0, 0, 0))
        text2 = font.render(f"Status: {status}", True, (0, 0, 0))
        text3 = font.render(f"Time: {pos} sec", True, (0, 0, 0))

        controls = font.render("P=Play/Pause N=Next B=Back S=Stop Q=Quit", True, (255, 255, 255))

        screen.blit(text1, (20, 50))
        screen.blit(text2, (20, 100))
        screen.blit(text3, (20, 150))
        screen.blit(controls, (20, 220))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()