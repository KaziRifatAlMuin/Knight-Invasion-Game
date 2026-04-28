# agents/fuzzy_agent.py - Part 1: Class Structure, Constants, and Initialization

from collections import deque

BOARD_SIZE = 9

# Knight movement patterns (L-shape)
KNIGHT_DIRS = [
    (2, 1), (2, -1), (-2, 1), (-2, -1),
    (1, 2), (1, -2), (-1, 2), (-1, -2)
]

# True 8-directional adjacency - matches game/rules.py is_adjacent_to_fire
ADJACENT_DIRS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]


class FuzzyAgent:
    """
    FUZZY AGENT with FULL FIS (Fuzzy Inference System)

    PRIORITY ORDER (HIGHEST TO LOWEST):
    1. FIRE SAFETY - NEVER land on a cell adjacent to fire if any safe move exists
    2. WIN NOW - move to goal row immediately
    3. BLOCK - if opponent near goal or ahead in BFS race
    4. MOVE - BFS-optimal move toward goal (fire-safe preferred)
    """

    def __init__(self):
        self.turn_count = 0
        self.first_move_done = False
        self.position_history = []
        self.BLOCK_THRESHOLD = 5

        self._init_fuzzy_sets()
        self._init_fuzzy_rules()

        print("\n" + "=" * 70)
        print("FUZZY AGENT with FULL FIS INITIALIZED")
        print("=" * 70)
        print("   Agent: Red Knight (Player 2)")
        print("   Starting Position: (8, 4) - Bottom row")
        print("   Goal: Reach row 0 (top)")
        print("   Fire avoidance: strict 8-directional adjacency")
        print(f"   Blocking threshold: {self.BLOCK_THRESHOLD} moves from goal")
        print("=" * 70 + "\n")