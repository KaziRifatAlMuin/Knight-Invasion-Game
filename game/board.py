# game/board.py

import random

class Board:
    def __init__(self, size=9):
        self.size = size
        self.grid = [['.' for _ in range(size)] for _ in range(size)]

        # Correct positions
        self.blue_pos = (0, size // 2)        # Top middle
        self.red_pos = (size - 1, size // 2)  # Bottom middle

        self.place_knights()
        self.place_fire()

    def place_knights(self):
        br, bc = self.blue_pos
        rr, rc = self.red_pos

        self.grid[br][bc] = 'B'
        self.grid[rr][rc] = 'R'

    def place_fire(self, fire_pairs=4):
        """
        Place fire in vertical symmetry:
        (r, c) ↔ (size-1-r, c)
        """

        placed = 0

        while placed < fire_pairs:
            r = random.randint(1, self.size // 2 - 1)  # avoid first row (blue)
            c = random.randint(0, self.size - 1)

            r_sym = self.size - 1 - r

            if self.is_empty(r, c) and self.is_empty(r_sym, c):
                self.grid[r][c] = 'F'
                self.grid[r_sym][c] = 'F'
                placed += 1

    def is_empty(self, r, c):
        return self.grid[r][c] == '.'

    def print_board(self):
        print("\n   " + " ".join(str(i+1) for i in range(self.size)))
        print("  +" + "--"*self.size + "+")

        for i in range(self.size):
            row = self.grid[i]
            print(f"{i+1:2}| " + " ".join(row) + " |")

        print("  +" + "--"*self.size + "+\n")

    def reset(self):
        self.grid = [['.' for _ in range(self.size)] for _ in range(self.size)]
        self.place_knights()
        self.place_fire()