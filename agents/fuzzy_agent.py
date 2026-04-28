# agents/fuzzy_agent.py

from collections import deque
from typing import List, Tuple, Optional, Set, Dict, Any

BOARD_SIZE = 9

# Knight movement patterns (L-shape)
KNIGHT_DIRS = [
    (2, 1), (2, -1), (-2, 1), (-2, -1),
    (1, 2), (1, -2), (-1, 2), (-1, -2)
]

# True 8-directional adjacency — matches game/rules.py is_adjacent_to_fire
ADJACENT_DIRS = [
    (-1, -1), (-1, 0), (-1, 1),
    ( 0, -1),          ( 0, 1),
    ( 1, -1), ( 1, 0), ( 1, 1),
]


class FuzzyAgent:
    """
    ENHANCED FUZZY AGENT with advanced strategic reasoning

    NEW FEATURES:
    1. Multi-step lookahead for fire spread prediction
    2. Adaptive blocking based on opponent patterns
    3. Path diversity to avoid predictable movement
    4. Risk assessment with fire danger zones
    5. Learning opponent tendencies
    6. Strategic retreat when necessary
    """

    def __init__(self):
        self.turn_count = 0
        self.first_move_done = False
        self.position_history = []
        self.opponent_positions = []  # Track opponent movement patterns
        
        # Strategic parameters
        self.BLOCK_THRESHOLD = 5
        self.AGGRESSION_LEVEL = 0.7  # 0=defensive, 1=aggressive
        self.RISK_TOLERANCE = 0.3    # 0=cautious, 1=reckless
        
        # Learning components
        self.opponent_patterns = {}   # Store opponent move frequencies
        self.fire_cell_memory = []    # Remember fire positions over time
        self.block_effectiveness = {}  # Track which blocks were effective
        
        # Path diversity
        self.recent_moves = deque(maxlen=6)
        self.alternative_paths = {}   # Cache alternative BFS paths
        
        # Strategic zones (pre-computed)
        self._init_strategic_zones()
        
        # FIS components
        self._init_fuzzy_sets()
        self._init_fuzzy_rules()

        print("\n" + "=" * 70)
        print("🔴 ENHANCED FUZZY AGENT with ADVANCED AI")
        print("=" * 70)
        print("   Agent: Red Knight (Player 2)")
        print("   Starting Position: (8, 4) - Bottom row")
        print("   Goal: Reach row 0 (top)")
        print(f"   Aggression: {self.AGGRESSION_LEVEL:.1f} | Risk Tolerance: {self.RISK_TOLERANCE:.1f}")
        print("   Features: Fire prediction, opponent learning, path diversity")
        print("=" * 70 + "\n")

    # =========================================================
    # STRATEGIC ZONES (pre-computed map features)
    # =========================================================
    
    def _init_strategic_zones(self):
        """Pre-compute strategic importance of board positions"""
        self.control_zones = {}
        self.choke_points = set()
        
        # Center control is valuable for knight mobility
        center = [(3,3), (3,4), (3,5), (4,3), (4,4), (4,5), (5,3), (5,4), (5,5)]
        
        # Choke points (positions with limited exit options)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                # Count how many knight moves from this position
                moves = [(r+dr, c+dc) for dr, dc in KNIGHT_DIRS 
                        if 0 <= r+dr < BOARD_SIZE and 0 <= c+dc < BOARD_SIZE]
                if len(moves) <= 3:  # Limited mobility = choke point
                    self.choke_points.add((r, c))
                
                # Strategic importance based on position
                if (r, c) in center:
                    self.control_zones[(r, c)] = 0.8  # High control value
                elif r == 0 or r == BOARD_SIZE-1:  # Goal rows
                    self.control_zones[(r, c)] = 1.0
                elif c == 0 or c == BOARD_SIZE-1:  # Edges
                    self.control_zones[(r, c)] = 0.5
                else:
                    self.control_zones[(r, c)] = 0.3

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
            # Race-based rules
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
            
            # Opponent proximity rules
            {'name': 'Opponent critical - MUST BLOCK',
             'antecedents': [('opponent_dist', 'critical')],
             'consequent': ('action', 'must_block'), 'weight': 1.0},
            {'name': 'Opponent dangerous - PREFER BLOCK',
             'antecedents': [('opponent_dist', 'dangerous')],
             'consequent': ('action', 'prefer_block'), 'weight': 0.9},
            
            # Distance to goal rules
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

    # =========================================================
    # ADVANCED FIRE PREDICTION
    # =========================================================
    
    def predict_fire_spread(self, fires: Set[Tuple[int, int]], turns: int = 2) -> Set[Tuple[int, int]]:
        """
        Predict where fire might spread in future turns
        Uses cellular automata simulation
        """
        if not fires:
            return set()
            
        predicted_fires = set(fires)
        
        for _ in range(turns):
            new_fires = set()
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    # Count adjacent fires (8-directional)
                    adjacent_count = sum(1 for dr, dc in ADJACENT_DIRS
                                       if (r + dr, c + dc) in predicted_fires)
                    
                    # Fire spreads to cells with 3+ adjacent fires (match rules.py)
                    if (r, c) not in predicted_fires and adjacent_count >= 3:
                        new_fires.add((r, c))
            predicted_fires.update(new_fires)
        
        return predicted_fires - set(fires)  # Return only new fire cells
    
    def calculate_fire_danger_zone(self, pos: Tuple[int, int], fires: Set[Tuple[int, int]]) -> float:
        """
        Calculate danger level of a position based on fire proximity and spread
        Returns value between 0 (safe) and 1 (critical)
        """
        if not fires:
            return 0.0
            
        r, c = pos
        
        # Immediate adjacency danger
        if self.is_cell_adjacent_to_fire(pos, fires):
            # Check if it's surrounded on multiple sides
            adj_fires = sum(1 for dr, dc in ADJACENT_DIRS 
                          if (r + dr, c + dc) in fires)
            if adj_fires >= 3:
                return 1.0  # Will be on fire next turn
            elif adj_fires >= 2:
                return 0.9
            else:
                return 0.7
        
        # Predict future fire spread
        future_fires = self.predict_fire_spread(fires, turns=1)
        if pos in future_fires:
            return 0.8
            
        # Distance-based danger
        min_dist = min(abs(r - fr) + abs(c - fc) for fr, fc in fires)
        danger = max(0, 1.0 - (min_dist / 5.0))
        
        return danger

    def is_cell_adjacent_to_fire(self, pos, fires):
        """Check if position is adjacent to any fire cell"""
        if not fires:
            return False
        r, c = pos
        for dr, dc in ADJACENT_DIRS:
            if (r + dr, c + dc) in fires:
                return True
        return False

    def filter_fire_safe_moves(self, moves, fires, risk_tolerance=None):
        """Filter moves based on fire danger with adaptive risk tolerance"""
        if risk_tolerance is None:
            risk_tolerance = self.RISK_TOLERANCE
            
        safe_moves = []
        for move in moves:
            danger = self.calculate_fire_danger_zone(move, fires)
            if danger <= risk_tolerance:
                safe_moves.append(move)
        
        return safe_moves

    # =========================================================
    # OPPONENT LEARNING
    # =========================================================
    
    def update_opponent_patterns(self, opp_pos: Tuple[int, int]):
        """Learn opponent's movement patterns"""
        self.opponent_positions.append(opp_pos)
        
        if len(self.opponent_positions) >= 2:
            prev = self.opponent_positions[-2]
            curr = self.opponent_positions[-1]
            
            # Record transition
            key = (prev, curr)
            self.opponent_patterns[key] = self.opponent_patterns.get(key, 0) + 1
            
            # Keep only recent patterns
            if len(self.opponent_positions) > 20:
                self.opponent_positions = self.opponent_positions[-10:]
    
    def predict_opponent_next_move(self, opp_pos: Tuple[int, int], 
                                   blocks: Set, fires: Set, my_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Predict opponent's most likely next moves based on learned patterns"""
        predictions = []
        
        # Pattern-based prediction
        for (prev, next_pos), count in self.opponent_patterns.items():
            if prev == opp_pos:
                predictions.append((next_pos, count))
        
        if predictions:
            # Sort by frequency
            predictions.sort(key=lambda x: x[1], reverse=True)
            return [p[0] for p in predictions[:3]]
        
        # Fallback: BFS-based prediction
        valid_moves = self.get_knight_moves(opp_pos, blocks, fires, my_pos)
        if valid_moves:
            # Assume opponent takes optimal path
            opp_goal = BOARD_SIZE - 1
            return sorted(valid_moves, 
                         key=lambda m: self.bfs_shortest_path(m, opp_goal, blocks, fires, my_pos))
        
        return []
    
    def is_opponent_predictable(self) -> bool:
        """Check if opponent has shown predictable patterns"""
        if len(self.opponent_patterns) < 3:
            return False
        
        # Check if any pattern repeats frequently
        max_freq = max(self.opponent_patterns.values()) if self.opponent_patterns else 0
        total = sum(self.opponent_patterns.values())
        
        return max_freq / total > 0.5 if total > 0 else False

    # =========================================================
    # ADVANCED BLOCKING STRATEGY
    # =========================================================
    
    def find_predictive_blocks(self, state, player, opp_pos: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Block predicted opponent paths before they become obvious
        """
        blocks = state.blocks
        fires = state.fires
        my_pos = state.p2
        opp_goal = BOARD_SIZE - 1
        
        # Get predicted opponent moves
        predicted_moves = self.predict_opponent_next_move(opp_pos, blocks, fires, my_pos)
        
        if not predicted_moves:
            return None
        
        # Evaluate blocking each predicted path
        best_pair = None
        best_gain = 0
        
        for target in predicted_moves[:2]:  # Focus on top predictions
            # Find optimal block pair for this target
            pair = self.find_optimal_block_for_position(target, state, player, opp_pos)
            if pair:
                # Calculate effectiveness
                new_dist = self.bfs_shortest_path(opp_pos, opp_goal, 
                                                 blocks | {pair[0], pair[1]}, 
                                                 fires, my_pos)
                baseline = self.bfs_shortest_path(opp_pos, opp_goal, blocks, fires, my_pos)
                gain = new_dist - baseline
                
                if gain > best_gain:
                    best_gain = gain
                    best_pair = pair
        
        if best_pair:
            print(f"   🧠 PREDICTIVE BLOCK: targeting opponent pattern with gain +{best_gain}")
            return best_pair
        
        return None
    
    def find_optimal_block_for_position(self, target: Tuple[int, int], state, player, opp_pos: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Find optimal block pair for a specific target position
        """
        blocks = state.blocks
        fires = state.fires
        my_pos = state.p2
        
        # Get all positions that can reach the target
        reaching_positions = []
        for dr, dc in KNIGHT_DIRS:
            nr, nc = target[0] - dr, target[1] - dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                reaching_positions.append((nr, nc))
        
        # Filter valid positions
        valid_positions = [p for p in reaching_positions 
                          if self._is_valid_cell(p[0], p[1], blocks, fires, my_pos, opp_pos)]
        
        # Find best pair to block
        for i in range(len(valid_positions)):
            for j in range(i+1, len(valid_positions)):
                if state.can_block(player, valid_positions[i], valid_positions[j]):
                    return [valid_positions[i], valid_positions[j]]
        
        return None
    
    def find_strategic_retreat(self, my_pos: Tuple[int, int], blocks: Set, 
                               fires: Set, opp_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        Find safe retreat when danger is high
        """
        all_moves = self.get_knight_moves(my_pos, blocks, fires, opp_pos)
        if not all_moves:
            return None
        
        # Score each move for safety and strategic value
        scored_moves = []
        for move in all_moves:
            danger = self.calculate_fire_danger_zone(move, fires)
            strategic_value = self.control_zones.get(move, 0)
            retreat_score = (1 - danger) * 0.6 + strategic_value * 0.4
            scored_moves.append((move, retreat_score))
        
        # Choose safest strategic retreat
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        
        # Only retreat if safer than current position
        current_danger = self.calculate_fire_danger_zone(my_pos, fires)
        if scored_moves and scored_moves[0][1] > (1 - current_danger):
            return scored_moves[0][0]
        
        return None

    # =========================================================
    # PATH DIVERSITY
    # =========================================================
    
    def get_bfs_path(self, start: Tuple[int, int], target_row: int,
                    blocks: Set, fires: Set, opponent: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Get actual BFS path (not just distance)"""
        if start[0] == target_row:
            return [start]
        
        visited = {start}
        queue = deque([(start, [start])])
        
        while queue:
            (r, c), path = queue.popleft()
            
            for dr, dc in KNIGHT_DIRS:
                nr, nc = r + dr, c + dc
                if self._is_valid_cell(nr, nc, blocks, fires, opponent, start):
                    nxt = (nr, nc)
                    if nxt not in visited:
                        if nr == target_row:
                            return path + [nxt]
                        visited.add(nxt)
                        queue.append((nxt, path + [nxt]))
        
        return None

    # =========================================================
    # KNIGHT MOVEMENT (enhanced)
    # =========================================================

    def _is_valid_cell(self, r: int, c: int, blocks: Set, fires: Set, 
                      opponent: Tuple[int, int], my_pos: Tuple[int, int]) -> bool:
        """Enhanced validation with strategic considerations"""
        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
            return False
        if (r, c) in blocks:
            return False
        if (r, c) in fires:
            return False
        if (r, c) == opponent:
            return False
        return True

    def get_knight_moves(self, pos: Tuple[int, int], blocks: Set, 
                        fires: Set, opponent: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get all valid knight moves from position"""
        r, c = pos
        return [
            (r + dr, c + dc)
            for dr, dc in KNIGHT_DIRS
            if self._is_valid_cell(r + dr, c + dc, blocks, fires, opponent, pos)
        ]

    def bfs_shortest_path(self, start: Tuple[int, int], target_row: int,
                         blocks: Set, fires: Set, opponent: Tuple[int, int]) -> int:
        """Calculate shortest path distance to target row"""
        if start[0] == target_row:
            return 0
        visited = {start}
        queue = deque([(start, 0)])
        while queue:
            (r, c), dist = queue.popleft()
            for dr, dc in KNIGHT_DIRS:
                nr, nc = r + dr, c + dc
                if self._is_valid_cell(nr, nc, blocks, fires, opponent, start):
                    nxt = (nr, nc)
                    if nxt not in visited:
                        if nr == target_row:
                            return dist + 1
                        visited.add(nxt)
                        queue.append((nxt, dist + 1))
        return 999

    # =========================================================
    # ENHANCED MOVE SELECTION
    # =========================================================

    def get_best_move_toward_goal(self, my_pos: Tuple[int, int], my_goal: int,
                                  blocks: Set, fires: Set, opponent_pos: Tuple[int, int],
                                  consider_diversity: bool = True) -> Optional[Tuple[int, int]]:
        """
        Enhanced move selection with path diversity and strategic considerations
        """
        all_moves = self.get_knight_moves(my_pos, blocks, fires, opponent_pos)
        if not all_moves:
            return None

        # Calculate danger for current position
        current_danger = self.calculate_fire_danger_zone(my_pos, fires)
        
        # Strategic retreat if danger is critical
        if current_danger > 0.8:
            retreat = self.find_strategic_retreat(my_pos, blocks, fires, opponent_pos)
            if retreat:
                print(f"   🏃 STRATEGIC RETREAT: danger={current_danger:.2f}")
                return retreat
        
        # Adaptive risk tolerance based on game state
        risk_tolerance = self.RISK_TOLERANCE
        if my_pos[0] <= 2:  # Close to goal, more aggressive
            risk_tolerance = min(0.6, risk_tolerance + 0.3)
        
        safe_moves = self.filter_fire_safe_moves(all_moves, fires, risk_tolerance)
        
        def enhanced_score(move):
            # Calculate multiple factors
            bfs_dist = self.bfs_shortest_path(move, my_goal, blocks, fires, opponent_pos)
            progress = my_pos[0] - move[0]  # Row advancement
            
            # Strategic value
            strategic_value = self.control_zones.get(move, 0)
            
            # Fire danger penalty
            fire_danger = self.calculate_fire_danger_zone(move, fires)
            
            # Path diversity bonus (avoid recent moves)
            diversity_bonus = 0
            if consider_diversity and self.recent_moves:
                if move not in self.recent_moves:
                    diversity_bonus = 0.5
            
            # Choke point bonus
            choke_bonus = 0.3 if move in self.choke_points else 0
            
            # Combine scores (lower is better)
            score = bfs_dist * 1.0 - progress * 0.5 - strategic_value * 0.3 - diversity_bonus - choke_bonus + fire_danger * 2.0
            
            return score
        
        # Choose best move based on enhanced scoring
        if safe_moves:
            best_move = min(safe_moves, key=enhanced_score)
        else:
            # No safe moves, take least dangerous
            best_move = min(all_moves, key=lambda m: self.calculate_fire_danger_zone(m, fires))
        
        # Update move history
        self.recent_moves.append(best_move)
        
        return best_move

    # =========================================================
    # ENHANCED BLOCKING
    # =========================================================

    def find_best_blocks_to_defend(self, state, player, opp_pos: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Enhanced blocking with predictive and learning components
        """
        # Try predictive blocking first
        if self.is_opponent_predictable():
            predictive_blocks = self.find_predictive_blocks(state, player, opp_pos)
            if predictive_blocks:
                return predictive_blocks
        
        # Fall back to standard blocking
        return self._find_standard_blocks(state, player, opp_pos)
    
    def _find_standard_blocks(self, state, player, opp_pos: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Original blocking strategy"""
        blocks = state.blocks
        fires = state.fires
        my_pos = state.p2
        opp_goal = BOARD_SIZE - 1

        baseline = self.bfs_shortest_path(opp_pos, opp_goal, blocks, fires, my_pos)
        if baseline >= 999:
            return None

        ranked_next = self._rank_opponent_next_moves(opp_pos, opp_goal, blocks, fires, my_pos)
        two_hop = sorted(
            self._two_hop_cells(opp_pos, blocks, fires, my_pos),
            key=lambda m: self.bfs_shortest_path(m, opp_goal, blocks, fires, my_pos)
        )

        def eval_pair(c1, c2):
            if not self._is_valid_cell(c1[0], c1[1], blocks, fires, my_pos, opp_pos):
                return -1
            if not self._is_valid_cell(c2[0], c2[1], blocks, fires, my_pos, opp_pos):
                return -1
            if c1 == c2:
                return -1
            if not state.can_block(player, c1, c2):
                return -1
            new_dist = self.bfs_shortest_path(
                opp_pos, opp_goal, blocks | {c1, c2}, fires, my_pos)
            gain = new_dist - baseline
            
            # Track block effectiveness
            self.block_effectiveness[(c1, c2)] = gain
            return gain

        best_pair = None
        best_gain = 0

        # Tier 1: both from immediate next moves
        for i in range(len(ranked_next)):
            for j in range(i + 1, len(ranked_next)):
                gain = eval_pair(ranked_next[i], ranked_next[j])
                if gain > best_gain:
                    best_gain = gain
                    best_pair = (ranked_next[i], ranked_next[j])
                    if best_gain >= 3:  # Early exit if good enough
                        return list(best_pair)

        # Tier 2: best 1-hop + best 2-hop
        for anchor in ranked_next:
            for support in two_hop:
                gain = eval_pair(anchor, support)
                if gain > best_gain:
                    best_gain = gain
                    best_pair = (anchor, support)

        # Tier 3: fallback
        if not best_pair:
            combined = ranked_next + [c for c in two_hop if c not in ranked_next]
            combined = combined[:24]
            for i in range(len(combined)):
                for j in range(i + 1, len(combined)):
                    gain = eval_pair(combined[i], combined[j])
                    if gain > best_gain:
                        best_gain = gain
                        best_pair = (combined[i], combined[j])

        return list(best_pair) if best_pair else None

    def _rank_opponent_next_moves(self, opp_pos: Tuple[int, int], opp_goal: int,
                                  blocks: Set, fires: Set, my_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Rank opponent's next moves from best to worst"""
        next_moves = self.get_knight_moves(opp_pos, blocks, fires, my_pos)
        return sorted(
            next_moves,
            key=lambda m: self.bfs_shortest_path(m, opp_goal, blocks, fires, my_pos)
        )

    def _two_hop_cells(self, opp_pos: Tuple[int, int], blocks: Set, 
                      fires: Set, my_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Cells opponent can reach in exactly 2 knight moves"""
        one_hop = set(self.get_knight_moves(opp_pos, blocks, fires, my_pos))
        two_hop = set()
        for mid in one_hop:
            for cell in self.get_knight_moves(mid, blocks, fires, my_pos):
                if cell != opp_pos and cell not in one_hop:
                    two_hop.add(cell)
        return list(two_hop)

    # =========================================================
    # LOOP DETECTION (enhanced)
    # =========================================================

    def check_and_break_loop(self, my_pos: Tuple[int, int], blocks: Set,
                            fires: Set, opponent_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Enhanced loop detection with active avoidance"""
        self.position_history.append(my_pos)
        if len(self.position_history) > 10:
            self.position_history.pop(0)

        # Check for loops
        if len(self.position_history) >= 6:
            recent = self.position_history[-6:]
            if len(set(recent[:3]) & set(recent[3:])) >= 2:
                print("   🔄 LOOP DETECTED — forcing strategic escape")
                
                all_moves = self.get_knight_moves(my_pos, blocks, fires, opponent_pos)
                safe_moves = self.filter_fire_safe_moves(all_moves, fires)
                
                # Escape to highest strategic value position not recently visited
                escape_targets = []
                for move in (safe_moves or all_moves):
                    if move not in self.position_history[-4:]:
                        strategic_score = self.control_zones.get(move, 0)
                        fire_danger = self.calculate_fire_danger_zone(move, fires)
                        escape_targets.append((move, strategic_score - fire_danger))
                
                if escape_targets:
                    escape_targets.sort(key=lambda x: x[1], reverse=True)
                    return escape_targets[0][0]
        
        return None

    # =========================================================
    # MAIN DECISION ENGINE (enhanced)
    # =========================================================

    def decide_action(self, state, player):
        """Enhanced decision engine with all new features"""
        self.turn_count += 1

        my_pos = state.p2
        opp_pos = state.p1
        blocks = state.blocks
        fires = state.fires
        my_goal = 0
        opp_goal = BOARD_SIZE - 1

        # Update learning
        self.update_opponent_patterns(opp_pos)
        self.fire_cell_memory.append(fires)
        if len(self.fire_cell_memory) > 10:
            self.fire_cell_memory.pop(0)

        print(f"\n{'=' * 70}")
        print(f"🔴 ENHANCED FUZZY AGENT - TURN {self.turn_count}")
        print(f"{'=' * 70}")
        print(f"   My Position : {my_pos} | Opponent: {opp_pos}")
        print(f"   Fire Danger : {self.calculate_fire_danger_zone(my_pos, fires):.2f}")
        print(f"   Predictable? : {self.is_opponent_predictable()}")

        # Priority 0: Emergency must move
        if state.must_move(player):
            print("   🔥 MUST MOVE — currently adjacent to fire")
            move = self.get_best_move_toward_goal(my_pos, my_goal, blocks, fires, opp_pos)
            if move:
                danger = self.calculate_fire_danger_zone(move, fires)
                tag = "✅ safe" if danger <= 0.3 else "⚠️ risky"
                print(f"   🏃 FIRE ESCAPE: {my_pos} → {move}  ({tag})")
                self.first_move_done = True
                return ('move', move)

        # First move
        if not self.first_move_done:
            move = self.get_best_move_toward_goal(my_pos, my_goal, blocks, fires, opp_pos)
            if move:
                self.first_move_done = True
                print(f"   🏃 FIRST MOVE: {my_pos} → {move}")
                return ('move', move)

        # Loop detection
        loop_move = self.check_and_break_loop(my_pos, blocks, fires, opp_pos)
        if loop_move:
            print(f"   🔄 LOOP BREAK: {my_pos} → {loop_move}")
            return ('move', loop_move)

        # BFS race analysis
        my_moves = self.bfs_shortest_path(my_pos, my_goal, blocks, fires, opp_pos)
        opp_moves = self.bfs_shortest_path(opp_pos, opp_goal, blocks, fires, my_pos)

        print(f"\n   📊 BFS RACE:")
        print(f"      RED  (me)  needs {my_moves}  moves → row 0")
        print(f"      BLUE (opp) needs {opp_moves} moves → row 8")

        # Winning move check
        all_my_moves = self.get_knight_moves(my_pos, blocks, fires, opp_pos)
        win_moves = [m for m in all_my_moves if m[0] == my_goal]
        safe_win = self.filter_fire_safe_moves(win_moves, fires)

        if safe_win:
            print(f"\n   🏆 SAFE WINNING MOVE: {my_pos} → {safe_win[0]}")
            return ('move', safe_win[0])
        if win_moves:
            print(f"\n   🏆 WINNING MOVE (accepting risk): {my_pos} → {win_moves[0]}")
            return ('move', win_moves[0])

        # FIS evaluation
        race_adv = opp_moves - my_moves
        f_race = self._fuzzify(race_adv, self.race_sets)
        f_dist = self._fuzzify(my_moves, self.distance_sets)
        f_opp = self._fuzzify(opp_moves, self.opponent_dist_sets)
        rule_output = self._evaluate_rules(f_race, f_dist, f_opp)
        crisp = self._defuzzify(rule_output)
        action_pref = self._get_action(crisp)

        # Adjust based on aggression level
        if self.AGGRESSION_LEVEL > 0.7:
            # More aggressive - prefer moving over blocking
            if action_pref in ['prefer_block', 'must_block']:
                action_pref = 'balanced'
        elif self.AGGRESSION_LEVEL < 0.3:
            # More defensive - prefer blocking
            if action_pref in ['prefer_move', 'must_move']:
                action_pref = 'balanced'

        print(f"\n   🎯 FIS OUTPUT: {action_pref}  (crisp={crisp:.2f})")
        print(f"   🎮 Aggression: {self.AGGRESSION_LEVEL:.2f}")

        # Decision: Block or Move?
        should_block = (opp_moves < my_moves or opp_moves <= self.BLOCK_THRESHOLD or
                       action_pref in ['prefer_block', 'must_block'])

        if should_block:
            print(f"\n   🎯 DECISION: BLOCK  (opponent ahead or close to goal)")
            blocks_pair = self.find_best_blocks_to_defend(state, player, opp_pos)
            if blocks_pair and len(blocks_pair) >= 2:
                if state.can_block(player, blocks_pair[0], blocks_pair[1]):
                    print(f"   🛡️  BLOCKING: {blocks_pair[0]}, {blocks_pair[1]}")
                    return ('block', (blocks_pair[0], blocks_pair[1]))
            print("   ❌ No valid block found — moving instead")

        # Move
        best_move = self.get_best_move_toward_goal(my_pos, my_goal, blocks, fires, opp_pos)
        if best_move:
            direction = ("UP" if best_move[0] < my_pos[0] else
                        "DOWN" if best_move[0] > my_pos[0] else "SAME ROW")
            danger = self.calculate_fire_danger_zone(best_move, fires)
            tag = "✅" if danger <= 0.3 else "⚠️" if danger <= 0.7 else "🔥"
            print(f"   🏃 MOVING {direction} {tag}: {my_pos} → {best_move} (danger={danger:.2f})")
            return ('move', best_move)

        # Fallback
        print("   ⚠️  FALLBACK")
        moves = self.get_knight_moves(my_pos, blocks, fires, opp_pos)
        if moves:
            best = min(moves, key=lambda m: self.calculate_fire_danger_zone(m, fires))
            print(f"   🏃 FALLBACK: {my_pos} → {best}")
            return ('move', best)

        print("   ❌ NO LEGAL ACTION!")
        return ('wait', None)