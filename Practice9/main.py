import sys

from mickeys_clock.clock import main as clock_main
from music_player.player import main as player_main
from moving_ball.ball import main as ball_main


def menu():
    i = 0
    for i in range(1):
        print("\n===== MAIN MENU =====")
        print("1. Mickey Clock")
        print("2. Music Player")
        print("3. Moving Ball")
        print("0. Exit")

        choice = input("Choose: ")

        if choice == "1":
            clock_main()

        elif choice == "2":
            player_main()

        elif choice == "3":
            ball_main()

        elif choice == "0":
            print("Bye!")
            sys.exit()

        else:
            print("Invalid choice")


if __name__ == "__main__":
    menu()