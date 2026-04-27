# game/rules.py

from collections import deque
import random
import copy

BOARD_SIZE = 9

KNIGHT_DIRS = [
    (2, 1), (2, -1), (-2, 1), (-2, -1),
    (1, 2), (1, -2), (-1, 2), (-1, -2)
]

# ----------------------------------
# BASIC HELPERS
# ----------------------------------

def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def is_valid_cell(r, c, blocks, fires, opponent):
    return (
        in_bounds(r, c)
        and (r, c) not in blocks
        and (r, c) not in fires
        and (r, c) != opponent
    )


def is_adjacent_to_fire(pos, fires):
    r, c = pos
    for fr, fc in fires:
        if max(abs(r - fr), abs(c - fc)) == 1:
            return True
    return False


# ----------------------------------
# KNIGHT MOVEMENT
# ----------------------------------

def get_knight_moves(pos, opponent, blocks, fires):
    moves = []

    for dr, dc in KNIGHT_DIRS:
        nr, nc = pos[0] + dr, pos[1] + dc
        if is_valid_cell(nr, nc, blocks, fires, opponent):
            moves.append((nr, nc))

    return moves


# ----------------------------------
# BFS PATH VALIDATION
# ----------------------------------

def has_valid_path(start, target_row, opponent, blocks, fires):
    visited = set([start])
    queue = deque([start])

    while queue:
        r, c = queue.popleft()

        if r == target_row:
            return True

        for dr, dc in KNIGHT_DIRS:
            nr, nc = r + dr, c + dc

            if (nr, nc) not in visited and is_valid_cell(nr, nc, blocks, fires, opponent):
                visited.add((nr, nc))
                queue.append((nr, nc))

    return False


# ----------------------------------
# BLOCK VALIDATION
# ----------------------------------

def can_place_two_blocks(blocks, fires, p1, p2, c1, c2):
    if c1 == c2:
        return False

    for cell in [c1, c2]:
        if (
            cell in blocks
            or cell in fires
            or cell == p1
            or cell == p2
        ):
            return False

    temp_blocks = blocks.union({c1, c2})

    # MUST keep paths for BOTH players
    if not has_valid_path(p1, BOARD_SIZE - 1, p2, temp_blocks, fires):
        return False

    if not has_valid_path(p2, 0, p1, temp_blocks, fires):
        return False

    return True


# ----------------------------------
# CHECK IF ANY BLOCK IS POSSIBLE
# ----------------------------------

def exists_valid_block(blocks, fires, p1, p2):
    empty_cells = [
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if (r, c) not in blocks
        and (r, c) not in fires
        and (r, c) != p1
        and (r, c) != p2
    ]

    n = len(empty_cells)

    for i in range(n):
        for j in range(i + 1, n):
            if can_place_two_blocks(blocks, fires, p1, p2,
                                    empty_cells[i], empty_cells[j]):
                return True

    return False


# ----------------------------------
# FIRE GENERATION (SAFE)
# ----------------------------------

def generate_symmetric_fire_safe(p1, p2, fire_count=10):
    pair_count = max(1, fire_count // 2)

    while True:
        fires = set()

        while len(fires) < pair_count * 2:
            r = random.randint(1, BOARD_SIZE // 2 - 1)
            c = random.randint(0, BOARD_SIZE - 1)

            sym = (BOARD_SIZE - 1 - r, c)

            fires.add((r, c))
            fires.add(sym)

        # ensure valid paths exist
        if (
            has_valid_path(p1, BOARD_SIZE - 1, p2, set(), fires)
            and has_valid_path(p2, 0, p1, set(), fires)
        ):
            return fires


# ----------------------------------
# GAME STATE
# ----------------------------------

class GameState:
    def __init__(self, fire_count=10):
        self.p1 = (0, 4)
        self.p2 = (8, 4)

        self.blocks = set()
        self.fires = generate_symmetric_fire_safe(self.p1, self.p2, fire_count)

    def clone(self):
        return copy.deepcopy(self)

    # ----------------------------------
    # ACTIONS
    # ----------------------------------

    def get_moves(self, player):
        pos = self.p1 if player == 1 else self.p2
        opp = self.p2 if player == 1 else self.p1

        return get_knight_moves(pos, opp, self.blocks, self.fires)

    def must_move(self, player):
        pos = self.p1 if player == 1 else self.p2
        return is_adjacent_to_fire(pos, self.fires)

    def can_block(self, player, c1, c2):
        if self.must_move(player):
            return False

        return can_place_two_blocks(
            self.blocks, self.fires,
            self.p1, self.p2,
            c1, c2
        )

    def block_possible(self):
        return exists_valid_block(self.blocks, self.fires, self.p1, self.p2)

    def get_open_cells(self):
        return [
            (r, c)
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if (r, c) not in self.blocks
            and (r, c) not in self.fires
            and (r, c) != self.p1
            and (r, c) != self.p2
        ]

    def get_first_block_candidates(self, player):
        if self.must_move(player):
            return []

        candidates = []
        open_cells = self.get_open_cells()

        for first in open_cells:
            for second in open_cells:
                if first == second:
                    continue
                if self.can_block(player, first, second):
                    candidates.append(first)
                    break

        return candidates

    def get_second_block_candidates(self, player, first):
        if first is None or self.must_move(player):
            return []

        return [
            cell
            for cell in self.get_open_cells()
            if cell != first and self.can_block(player, first, cell)
        ]

    # ----------------------------------
    # APPLY ACTIONS
    # ----------------------------------

    def apply_move(self, player, move):
        if player == 1:
            self.p1 = move
        else:
            self.p2 = move

    def apply_block(self, player, c1, c2):
        if not self.can_block(player, c1, c2):
            return False

        self.blocks.add(c1)
        self.blocks.add(c2)
        return True

    # ----------------------------------
    # WIN
    # ----------------------------------

    def check_winner(self):
        if self.p1[0] == BOARD_SIZE - 1:
            return 1
        if self.p2[0] == 0:
            return 2
        return None