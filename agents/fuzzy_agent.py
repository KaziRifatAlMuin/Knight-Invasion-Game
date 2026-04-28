
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
    


    def is_cell_adjacent_to_fire(self, pos, fires):
        if not fires:
            return False
        r, c = pos
        for dr, dc in ADJACENT_DIRS:
            if (r + dr, c + dc) in fires:
                return True
        return False

    def filter_fire_safe_moves(self, moves, fires):
        return [m for m in moves if not self.is_cell_adjacent_to_fire(m, fires)]


    def _is_valid_cell(self, r, c, blocks, fires, opponent):
        return (
            0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE
            and (r, c) not in blocks
            and (r, c) not in fires
            and (r, c) != opponent
        )

    def get_knight_moves(self, pos, blocks, fires, opponent):
        r, c = pos
        return [
            (r + dr, c + dc)
            for dr, dc in KNIGHT_DIRS
            if self._is_valid_cell(r + dr, c + dc, blocks, fires, opponent)
        ]

    def bfs_shortest_path(self, start, target_row, blocks, fires, opponent):
        if start[0] == target_row:
            return 0
        visited = {start}
        queue = deque([(start, 0)])
        while queue:
            (r, c), dist = queue.popleft()
            for dr, dc in KNIGHT_DIRS:
                nr, nc = r + dr, c + dc
                if self._is_valid_cell(nr, nc, blocks, fires, opponent):
                    nxt = (nr, nc)
                    if nxt not in visited:
                        if nr == target_row:
                            return dist + 1
                        visited.add(nxt)
                        queue.append((nxt, dist + 1))
        return 999



    def get_best_move_toward_goal(self, my_pos, my_goal, blocks, fires, opponent_pos):
        """
        Two-pass move selector - fire-safe cells always win over fire-adjacent ones.

        PASS 1 - score only fire-safe moves by BFS distance to goal.
                  Return best safe move if any exist.

        PASS 2 - only if ZERO safe moves available: accept fire-adjacent moves,
                  pick best BFS score among them, print a warning.
        """
        all_moves = self.get_knight_moves(my_pos, blocks, fires, opponent_pos)
        if not all_moves:
            return None

        safe_moves = self.filter_fire_safe_moves(all_moves, fires)

        def bfs_score(move):
            bfs = self.bfs_shortest_path(move, my_goal, blocks, fires, opponent_pos)
            progress = my_pos[0] - move[0]
            return (bfs, -progress)

        if safe_moves:
            return min(safe_moves, key=bfs_score)

        print("   WARNING: ALL legal moves are fire-adjacent - forced to accept risk")
        return min(all_moves, key=bfs_score)
    


    def get_opponent_next_moves(self, opp_pos, blocks, fires, my_pos):
        return self.get_knight_moves(opp_pos, blocks, fires, my_pos)

    def get_opponent_winning_moves(self, opp_pos, blocks, fires, my_pos):
        opp_goal = BOARD_SIZE - 1
        return [
            m for m in self.get_knight_moves(opp_pos, blocks, fires, my_pos)
            if m[0] == opp_goal
        ]

    def rank_opponent_next_moves(self, opp_pos, opp_goal, blocks, fires, my_pos):
        """
        Opponent's immediate (1-hop) moves sorted best-to-worst for opponent.
        Lowest post-move BFS = best move for them = highest block priority.
        """
        next_moves = self.get_knight_moves(opp_pos, blocks, fires, my_pos)
        return sorted(
            next_moves,
            key=lambda m: self.bfs_shortest_path(m, opp_goal, blocks, fires, my_pos)
        )

    def _two_hop_cells(self, opp_pos, blocks, fires, my_pos):
        """Cells the opponent can reach in exactly 2 knight moves."""
        one_hop = set(self.get_knight_moves(opp_pos, blocks, fires, my_pos))
        two_hop = set()
        for mid in one_hop:
            for cell in self.get_knight_moves(mid, blocks, fires, my_pos):
                if cell != opp_pos and cell not in one_hop:
                    two_hop.add(cell)
        return list(two_hop)

    def _is_placeable(self, cell, blocks, fires, my_pos, opp_pos):
        return (
            cell not in blocks and cell not in fires
            and cell != my_pos and cell != opp_pos
        )
    


    def find_best_blocks_to_defend(self, state, player, opp_pos):
        """
        Find block pair (c1, c2) targeting cells the opponent most wants to
        move to, maximizing BFS detour imposed.

        TIER 1 - both cells from opponent's best immediate next moves
        TIER 2 - opponent's best next move + best 2-hop support cell
        TIER 3 - fallback: any valid pair from combined 1-hop + 2-hop pool
        """
        blocks = state.blocks
        fires = state.fires
        my_pos = state.p2
        opp_goal = BOARD_SIZE - 1

        baseline = self.bfs_shortest_path(opp_pos, opp_goal, blocks, fires, my_pos)
        if baseline >= 999:
            return None

        ranked_next = self.rank_opponent_next_moves(
            opp_pos, opp_goal, blocks, fires, my_pos)
        two_hop = sorted(
            self._two_hop_cells(opp_pos, blocks, fires, my_pos),
            key=lambda m: self.bfs_shortest_path(m, opp_goal, blocks, fires, my_pos)
        )

        def eval_pair(c1, c2):
            if not self._is_placeable(c1, blocks, fires, my_pos, opp_pos):
                return -1
            if not self._is_placeable(c2, blocks, fires, my_pos, opp_pos):
                return -1
            if c1 == c2:
                return -1
            if not state.can_block(player, c1, c2):
                return -1
            new_dist = self.bfs_shortest_path(
                opp_pos, opp_goal, blocks | {c1, c2}, fires, my_pos)
            return new_dist - baseline

        best_pair = None
        best_gain = 0

        # Tier 1: both cells from opponent's immediate next moves
        for i in range(len(ranked_next)):
            for j in range(i + 1, len(ranked_next)):
                gain = eval_pair(ranked_next[i], ranked_next[j])
                if gain > best_gain:
                    best_gain = gain
                    best_pair = (ranked_next[i], ranked_next[j])

        if best_pair:
            return list(best_pair)

        # Tier 2: best next-move anchor + best 2-hop support
        for anchor in ranked_next:
            for support in two_hop:
                gain = eval_pair(anchor, support)
                if gain > best_gain:
                    best_gain = gain
                    best_pair = (anchor, support)
            if best_pair:
                break

        if best_pair:
            return list(best_pair)

        # Tier 3: fallback over full combined pool
        combined = ranked_next + [c for c in two_hop if c not in ranked_next]
        combined = combined[:24]
        for i in range(len(combined)):
            for j in range(i + 1, len(combined)):
                gain = eval_pair(combined[i], combined[j])
                if gain > best_gain:
                    best_gain = gain
                    best_pair = (combined[i], combined[j])

        if best_pair:
            return list(best_pair)

        return None