# game/board.py

from game.rules import GameState


class Board:
    def __init__(self):
        self.state = GameState()

    # ---------------------------
    # Display Only (NO LOGIC)
    # ---------------------------

    def display(self):
        size = 9
        grid = [['.' for _ in range(size)] for _ in range(size)]

        # Fires
        for r, c in self.state.fires:
            grid[r][c] = 'F'

        # Blocks
        for r, c in self.state.blocks:
            grid[r][c] = 'X'

        # Players
        r1, c1 = self.state.p1
        r2, c2 = self.state.p2

        grid[r1][c1] = 'B'  # Player 1
        grid[r2][c2] = 'R'  # Player 2

        # Print nicely
        print("\n   " + " ".join(str(i+1) for i in range(size)))
        print("  +" + "--"*size + "+")

        for i in range(size):
            print(f"{i+1:2}| " + " ".join(grid[i]) + " |")

        print("  +" + "--"*size + "+\n")