from collections import deque
import random
import copy

BOARD_SIZE = 9

# Knight moves (L-shape)
KNIGHT_DIRS = [
    (2, 1), (2, -1), (-2, 1), (-2, -1),
    (1, 2), (1, -2), (-1, 2), (-1, -2)
]

# ----------------------------------
# Utility
# ----------------------------------

def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def is_adjacent_to_fire(pos, fires):
    r, c = pos
    for fr, fc in fires:
        if max(abs(r - fr), abs(c - fc)) == 1:
            return True
    return False


def is_valid_cell(r, c, blocks, fires, opponent):
    if not in_bounds(r, c):
        return False
    if (r, c) in blocks:
        return False
    if (r, c) in fires:
        return False
    if (r, c) == opponent:
        return False
    return True


# ----------------------------------
# Knight Moves
# ----------------------------------

def get_knight_moves(pos, opponent, blocks, fires):
    moves = []
    r, c = pos

    for dr, dc in KNIGHT_DIRS:
        nr, nc = r + dr, c + dc
        if is_valid_cell(nr, nc, blocks, fires, opponent):
            moves.append((nr, nc))

    return moves


# ----------------------------------
# BFS Path Validation (CRITICAL RULE)
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
# Blocking Rule
# ----------------------------------

def can_place_two_blocks(blocks, fires, p1_pos, p2_pos, cell1, cell2):
    # Must be two distinct cells
    if cell1 == cell2:
        return False

    new_blocks = {cell1, cell2}

    # Cannot block invalid cells
    for cell in new_blocks:
        if cell in blocks or cell in fires:
            return False
        if cell == p1_pos or cell == p2_pos:
            return False

    temp_blocks = blocks.union(new_blocks)

    # MUST maintain path for BOTH players
    if not has_valid_path(p1_pos, BOARD_SIZE - 1, p2_pos, temp_blocks, fires):
        return False
    if not has_valid_path(p2_pos, 0, p1_pos, temp_blocks, fires):
        return False

    return True


# ----------------------------------
# Fire Generation (Symmetrical)
# ----------------------------------

def generate_symmetric_fire(num_pairs=3):
    fires = set()

    while len(fires) < num_pairs * 2:
        r = random.randint(0, BOARD_SIZE // 2 - 1)
        c = random.randint(0, BOARD_SIZE - 1)

        sym_r = BOARD_SIZE - 1 - r
        sym_c = c

        fires.add((r, c))
        fires.add((sym_r, sym_c))

    return fires


# ----------------------------------
# Game State
# ----------------------------------

class GameState:
    def __init__(self):
        self.p1_pos = (0, 4)   # (1,5)
        self.p2_pos = (8, 4)   # (9,5)

        self.blocks = set()
        self.fires = generate_symmetric_fire()

    def clone(self):
        return copy.deepcopy(self)

    # ----------------------------------
    # Legal Actions
    # ----------------------------------

    def get_legal_moves(self, player):
        pos = self.p1_pos if player == 1 else self.p2_pos
        opp = self.p2_pos if player == 1 else self.p1_pos

        return get_knight_moves(pos, opp, self.blocks, self.fires)

    def can_block(self, player):
        pos = self.p1_pos if player == 1 else self.p2_pos

        # SPECIAL RULE: must move if near fire
        if is_adjacent_to_fire(pos, self.fires):
            return False

        return True

    # ----------------------------------
    # Apply Move
    # ----------------------------------

    def apply_move(self, player, move):
        if player == 1:
            self.p1_pos = move
        else:
            self.p2_pos = move

    # ----------------------------------
    # Apply Block
    # ----------------------------------

    def apply_block(self, player, cell1, cell2):
        if not self.can_block(player):
            return False

        if can_place_two_blocks(self.blocks, self.fires,
                                self.p1_pos, self.p2_pos,
                                cell1, cell2):
            self.blocks.add(cell1)
            self.blocks.add(cell2)
            return True

        return False

    # ----------------------------------
    # Winner Check
    # ----------------------------------

    def check_winner(self):
        if self.p1_pos[0] == BOARD_SIZE - 1:
            return 1
        if self.p2_pos[0] == 0:
            return 2
        return None