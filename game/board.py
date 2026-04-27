# game/board.py

from game.rules import GameState


class Board:
    def __init__(self, fire_pairs):
        """
        Initialize board with given fire_pairs.
        fire_pairs = number of symmetric fire pairs (each pair = 2 cells)
        """
        self.size = 9
        self.state = GameState(fire_pairs)

    # ----------------------------------
    # DISPLAY BOARD
    # ----------------------------------

    def display(self):
        """
        Prints the current board state.
        B = Player 1 (Blue)
        R = Player 2 (Red)
        F = Fire
        X = Block
        . = Empty
        """

        grid = [['.' for _ in range(self.size)] for _ in range(self.size)]

        # Fires
        for r, c in self.state.fires:
            grid[r][c] = 'F'

        # Blocks
        for r, c in self.state.blocks:
            grid[r][c] = 'X'

        # Players
        br, bc = self.state.p1
        rr, rc = self.state.p2

        grid[br][bc] = 'B'
        grid[rr][rc] = 'R'

        # Header
        print("\n   " + " ".join(str(i + 1) for i in range(self.size)))
        print("  +" + "--" * self.size + "+")

        # Rows
        for i in range(self.size):
            print(f"{i + 1:2}| " + " ".join(grid[i]) + " |")

        print("  +" + "--" * self.size + "+\n")

    # ----------------------------------
    # OPTIONAL: RESET BOARD
    # ----------------------------------

    def reset(self, fire_pairs):
        """
        Reset board with new fire configuration.
        """
        self.state = GameState(fire_pairs)

    # ----------------------------------
    # OPTIONAL: GET RAW GRID (for future GUI/AI)
    # ----------------------------------

    def get_grid(self):
        """
        Returns a 2D grid representation (useful for AI/debugging).
        """
        grid = [['.' for _ in range(self.size)] for _ in range(self.size)]

        for r, c in self.state.fires:
            grid[r][c] = 'F'

        for r, c in self.state.blocks:
            grid[r][c] = 'X'

        br, bc = self.state.p1
        rr, rc = self.state.p2

        grid[br][bc] = 'B'
        grid[rr][rc] = 'R'

        return grid