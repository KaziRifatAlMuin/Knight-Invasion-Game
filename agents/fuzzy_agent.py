
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



    def _init_fuzzy_rules(self):
        self.rules = [
            {'name': 'Opponent much ahead - MUST BLOCK',
             'antecedents': [('race', 'opponent_ahead_much')],
             'consequent': ('action', 'must_block'), 'weight': 1.0},
            {'name': 'Opponent ahead - PREFER BLOCK',
             'antecedents': [('race', 'opponent_ahead')],
             'consequent': ('action', 'prefer_block'), 'weight': 0.95},
            {'name': 'Tied race - BALANCED',
             'antecedents': [('race', 'tied')],
             'consequent': ('action', 'balanced'), 'weight': 0.7},
            {'name': 'Me ahead - PREFER MOVE',
             'antecedents': [('race', 'me_ahead')],
             'consequent': ('action', 'prefer_move'), 'weight': 0.95},
            {'name': 'Me much ahead - MUST MOVE',
             'antecedents': [('race', 'me_ahead_much')],
             'consequent': ('action', 'must_move'), 'weight': 1.0},
            {'name': 'Opponent critical - MUST BLOCK',
             'antecedents': [('opponent_dist', 'critical')],
             'consequent': ('action', 'must_block'), 'weight': 1.0},
            {'name': 'Opponent dangerous - PREFER BLOCK',
             'antecedents': [('opponent_dist', 'dangerous')],
             'consequent': ('action', 'prefer_block'), 'weight': 0.9},
            {'name': 'Very close to goal - MUST MOVE',
             'antecedents': [('distance', 'very_close')],
             'consequent': ('action', 'must_move'), 'weight': 1.0},
        ]



    def _triangular_membership(self, x, a, b, c):
        if x <= a or x >= c:
            return 0.0
        if a < x <= b:
            return (x - a) / (b - a) if b != a else 1.0
        return (c - x) / (c - b) if c != b else 1.0

    def _fuzzify(self, value, fuzzy_sets):
        return {
            term: self._triangular_membership(value, a, b, c)
            for term, (a, b, c) in fuzzy_sets.items()
        }

    def _evaluate_rules(self, f_race, f_distance, f_opponent):
        output = {k: 0.0 for k in self.output_sets}
        for rule in self.rules:
            strengths = []
            for var_type, term in rule['antecedents']:
                if var_type == 'race':
                    strengths.append(f_race.get(term, 0))
                elif var_type == 'distance':
                    strengths.append(f_distance.get(term, 0))
                elif var_type == 'opponent_dist':
                    strengths.append(f_opponent.get(term, 0))
            strength = min(strengths) * rule['weight'] if strengths else 0
            key = rule['consequent'][1]
            output[key] = max(output[key], strength)
        return output

    def _defuzzify(self, output):
        centers = {
            'must_move': 1.0, 'prefer_move': 3.0, 'balanced': 5.0,
            'prefer_block': 7.0, 'must_block': 9.0,
        }
        num = den = 0.0
        for term, strength in output.items():
            if strength > 0:
                num += strength * centers[term]
                den += strength
        return num / den if den > 0 else 5.0

    def _get_action(self, value):
        if value <= 2.5:   return 'must_move'
        if value <= 4.5:   return 'prefer_move'
        if value <= 6.5:   return 'balanced'
        if value <= 8.5:   return 'prefer_block'
        return 'must_block'