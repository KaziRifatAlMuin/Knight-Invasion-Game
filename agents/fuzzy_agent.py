
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


    def _init_fuzzy_sets(self):
        self.distance_sets = {
            'very_close': (0, 0, 2), 'close': (1, 2, 4),
            'medium': (3, 5, 7), 'far': (5, 7, 8), 'very_far': (7, 8, 8),
        }
        self.opponent_dist_sets = {
            'critical': (0, 0, 2), 'dangerous': (1, 3, 5),
            'moderate': (3, 5, 7), 'safe': (5, 7, 8), 'very_safe': (6, 8, 8),
        }
        self.race_sets = {
            'opponent_ahead_much': (-8, -6, -3), 'opponent_ahead': (-5, -3, -1),
            'tied': (-2, 0, 2), 'me_ahead': (1, 3, 5), 'me_ahead_much': (3, 6, 8),
        }
        self.output_sets = {
            'must_move': (0, 0, 2), 'prefer_move': (1, 3, 5),
            'balanced': (3, 5, 7), 'prefer_block': (5, 7, 9), 'must_block': (8, 10, 10),
        }