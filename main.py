# main.py

from game.board import Board

def main():
    print("🧠 Knight Invasion Game Started!\n")

    board = Board()

    print("Initial Board:")
    board.print_board()

    while True:
        choice = input("Press ENTER to regenerate board or 'q' to quit: ")

        if choice.lower() == 'q':
            print("Game exited.")
            break

        board.reset()
        board.print_board()


if __name__ == "__main__":
    main()