# game/board.py

import random

class Board:
    def __init__(self, size=9):
        self.size = size
        self.grid = [['.' for _ in range(size)] for _ in range(size)]

        # Initial knight positions
        self.red_pos = (0, 4)   # (1,5) in 1-based indexing
        self.blue_pos = (8, 4)  # (9,5)

        self.place_knights()
        self.place_fire()

    def place_knights(self):
        r, c = self.red_pos
        self.grid[r][c] = 'R'

        r, c = self.blue_pos
        self.grid[r][c] = 'B'

    def place_fire(self, fire_count=6):
        """Place symmetric fire cells"""
        placed = 0

        while placed < fire_count:
            r = random.randint(0, self.size//2 - 1)
            c = random.randint(0, self.size - 1)

            r_sym = self.size - 1 - r
            c_sym = self.size - 1 - c

            if self.is_empty(r, c) and self.is_empty(r_sym, c_sym):
                self.grid[r][c] = 'F'
                self.grid[r_sym][c_sym] = 'F'
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