import math
import time
from collections import deque

from game.rules import BOARD_SIZE, KNIGHT_DIRS


WIN_SCORE = 1_000_000


class SearchTimeout(Exception):
    pass


class MinimaxAgent:
    def __init__(self, player=2, depth=6, max_block_first=10, max_block_second=6, time_limit=0.9):
        self.player = player
        self.depth = depth
        self.max_block_first = max_block_first
        self.max_block_second = max_block_second
        self.time_limit = time_limit
        self.tt = {}

    # ─────────────────────────────────────────────
    #  Public entry
    # ─────────────────────────────────────────────

    def choose_action(self, state):
        deadline = time.perf_counter() + self.time_limit
        root_player = self.player

        root_actions = self._actions(state, root_player)
        if not root_actions:
            return None

        # Instant win — take it immediately.
        immediate_win = self._first_immediate_winning_action(state, root_player, root_actions)
        if immediate_win is not None:
            return immediate_win

        # Filter out moves that hand opponent an instant win.
        safe_actions = self._safe_actions(state, root_player, root_actions)
        if safe_actions:
            root_actions = safe_actions

        best_action = root_actions[0]
        best_score = -math.inf

        for search_depth in range(1, self.depth + 1):
            try:
                score, action = self._search_root(state, root_actions, search_depth, deadline)
            except SearchTimeout:
                break

            if action is not None:
                best_action = action
                best_score = score

            if abs(best_score) >= WIN_SCORE - 100:
                break
            if time.perf_counter() >= deadline:
                break

        return best_action

    # ─────────────────────────────────────────────
    #  Root search
    # ─────────────────────────────────────────────

    def _search_root(self, state, root_actions, depth, deadline):
        alpha = -math.inf
        beta = math.inf
        best_score = -math.inf
        best_action = root_actions[0]

        ordered = self._order_actions(state, root_actions, self.player, depth)

        for action in ordered:
            if time.perf_counter() >= deadline:
                raise SearchTimeout

            child = self._result(state, action, self.player)
            score = -self._negamax(child, depth - 1, -beta, -alpha,
                                   self._other(self.player), deadline)

            if score > best_score:
                best_score = score
                best_action = action

            alpha = max(alpha, best_score)
            if alpha >= beta:
                break

        return best_score, best_action

    # ─────────────────────────────────────────────
    #  Negamax + alpha-beta
    # ─────────────────────────────────────────────

    def _negamax(self, state, depth, alpha, beta, current_player, deadline):
        if time.perf_counter() >= deadline:
            raise SearchTimeout

        winner = state.check_winner()
        if winner is not None:
            return (WIN_SCORE + depth) if winner == self.player else (-WIN_SCORE - depth)

        if depth <= 0:
            # Evaluate always from the root agent's perspective; negate for opponent.
            raw = self._evaluate(state)
            return raw if current_player == self.player else -raw

        key = self._state_key(state, current_player, depth)
        tt_entry = self.tt.get(key)
        if tt_entry is not None:
            flag, val, _ = tt_entry
            if flag == "exact":
                return val
            if flag == "lower" and val >= beta:
                return val
            if flag == "upper" and val <= alpha:
                return val

        actions = self._actions(state, current_player)
        if not actions:
            raw = self._evaluate(state)
            return raw if current_player == self.player else -raw

        actions = self._order_actions(state, actions, current_player, depth)

        orig_alpha = alpha
        best_value = -math.inf

        for action in actions:
            if time.perf_counter() >= deadline:
                raise SearchTimeout

            child = self._result(state, action, current_player)
            value = -self._negamax(child, depth - 1, -beta, -alpha,
                                   self._other(current_player), deadline)

            if value > best_value:
                best_value = value
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break

        # Store in transposition table with flag.
        if best_value <= orig_alpha:
            flag = "upper"
        elif best_value >= beta:
            flag = "lower"
        else:
            flag = "exact"
        self.tt[key] = (flag, best_value, None)

        return best_value

    # ─────────────────────────────────────────────
    #  Action generation
    # ─────────────────────────────────────────────

    def _actions(self, state, player):
        moves = state.get_moves(player)
        action_list = [("move", m) for m in moves]

        if state.must_move(player):
            return action_list
        if not state.block_possible():
            return action_list

        # ── Block candidates: prioritise cells where opponent can land next ──
        opponent = self._other(player)
        opp_next_moves = set(state.get_moves(opponent))
        opp_target_row = BOARD_SIZE - 1 if opponent == 1 else 0

        first_cells = state.get_first_block_candidates(player)

        # Score each candidate: cells reachable by opponent AND close to their
        # target row are the most dangerous — block those first.
        def first_priority(cell):
            in_opp_reach = cell in opp_next_moves             # immediate threat
            row_closeness = abs(cell[0] - opp_target_row)     # 0 = already on target
            return (0 if in_opp_reach else 1, row_closeness)

        first_cells = sorted(first_cells, key=first_priority)
        if self.max_block_first:
            first_cells = first_cells[:self.max_block_first]

        for first in first_cells:
            second_cells = state.get_second_block_candidates(player, first)

            def second_priority(cell):
                in_opp_reach = cell in opp_next_moves
                row_closeness = abs(cell[0] - opp_target_row)
                return (0 if in_opp_reach else 1, row_closeness)

            second_cells = sorted(second_cells, key=second_priority)
            if self.max_block_second:
                second_cells = second_cells[:self.max_block_second]

            for second in second_cells:
                action_list.append(("block", (first, second)))

        return action_list

    # ─────────────────────────────────────────────
    #  Action ordering — called at every node
    # ─────────────────────────────────────────────

    def _order_actions(self, state, action_list, player, depth):
        """
        Sort actions so alpha-beta sees the best moves first.

        Move actions  → sorted by how much they improve BFS distance to target
                        (smaller BFS distance = better for current player).
        Block actions → sorted by how much they increase opponent's BFS distance
                        (larger increase = better).
        Winning moves always come first.
        """
        opponent = self._other(player)
        agent_target  = BOARD_SIZE - 1 if player == 1 else 0
        opp_target    = BOARD_SIZE - 1 if opponent == 1 else 0

        agent_pos  = state.p1 if player   == 1 else state.p2
        opp_pos    = state.p1 if opponent == 1 else state.p2

        # Pre-compute current distances (cheap BFS calls).
        cur_agent_dist = self._knight_distance_to_row(
            agent_pos, agent_target, opp_pos, state.blocks, state.fires)
        cur_opp_dist = self._knight_distance_to_row(
            opp_pos, opp_target, agent_pos, state.blocks, state.fires)

        # TT hint.
        tt_bonus = {}
        for action in action_list:
            child = self._result(state, action, player)
            key = self._state_key(child, opponent, max(depth - 1, 0))
            tt_bonus[id(action)] = 1 if key in self.tt else 0

        def score(action):
            action_type, payload = action
            child = self._result(state, action, player)

            # Immediate win → absolute top priority.
            if child.check_winner() == player:
                return 10_000_000

            new_agent_pos = child.p1 if player   == 1 else child.p2
            new_opp_pos   = child.p1 if opponent == 1 else child.p2

            if action_type == "move":
                # How much closer did we get to our target row?
                new_dist = self._knight_distance_to_row(
                    new_agent_pos, agent_target, new_opp_pos,
                    child.blocks, child.fires)
                dist_gain = cur_agent_dist - new_dist       # positive = good
                return dist_gain * 1000 + tt_bonus.get(id(action), 0) * 100

            else:  # block
                # How much did we push the opponent back?
                new_opp_dist = self._knight_distance_to_row(
                    new_opp_pos, opp_target, new_agent_pos,
                    child.blocks, child.fires)
                dist_damage = new_opp_dist - cur_opp_dist   # positive = good
                return dist_damage * 1000 + tt_bonus.get(id(action), 0) * 100

        return sorted(action_list, key=score, reverse=True)

    # ─────────────────────────────────────────────
    #  Evaluation function (always from self.player's POV)
    # ─────────────────────────────────────────────

    def _evaluate(self, state):
        opponent = self._other(self.player)

        agent_pos = state.p1 if self.player == 1 else state.p2
        opp_pos   = state.p1 if opponent    == 1 else state.p2

        agent_target = BOARD_SIZE - 1 if self.player == 1 else 0
        opp_target   = BOARD_SIZE - 1 if opponent    == 1 else 0

        # ── BFS distances (most important signal) ──────────────────────────
        agent_dist = self._knight_distance_to_row(
            agent_pos, agent_target, opp_pos,   state.blocks, state.fires)
        opp_dist   = self._knight_distance_to_row(
            opp_pos,   opp_target,   agent_pos, state.blocks, state.fires)

        # Penalise unreachable state heavily.
        if agent_dist == 99:
            return -WIN_SCORE + 200
        if opp_dist == 99:
            return  WIN_SCORE - 200

        # ── Tactical threat detection ──────────────────────────────────────
        if self._has_immediate_winning_move(state, self.player):
            return WIN_SCORE - 500
        if self._has_immediate_winning_move(state, opponent):
            return -WIN_SCORE + 500

        # ── Mobility (knight moves available) ─────────────────────────────
        agent_moves = len(state.get_moves(self.player))
        opp_moves   = len(state.get_moves(opponent))

        # ── Blocking power (how many first-block candidates each has) ─────
        agent_block_power = len(state.get_first_block_candidates(self.player))
        opp_block_power   = len(state.get_first_block_candidates(opponent))

        # ── Row progress ──────────────────────────────────────────────────
        agent_progress = self._row_progress(agent_pos, self.player)
        opp_progress   = self._row_progress(opp_pos,   opponent)

        # ── Weighted combination ───────────────────────────────────────────
        # Distance is the dominant term.  Everything else is a tiebreaker.
        score = 0
        score += (opp_dist   - agent_dist)    * 500   # BFS distance delta
        score += (agent_progress - opp_progress) * 60  # raw row progress
        score += (agent_moves  - opp_moves)   * 20    # mobility
        score += (agent_block_power - opp_block_power) * 8  # blocking potential

        return score

    # ─────────────────────────────────────────────
    #  Helpers
    # ─────────────────────────────────────────────

    def _result(self, state, action, player):
        child = state.clone()
        action_type, payload = action
        if action_type == "move":
            child.apply_move(player, payload)
        else:
            c1, c2 = payload
            child.apply_block(player, c1, c2)
        return child

    def _first_immediate_winning_action(self, state, player, action_list):
        for action in action_list:
            child = self._result(state, action, player)
            if child.check_winner() == player:
                return action
        return None

    def _safe_actions(self, state, player, action_list):
        opponent = self._other(player)
        safe = []
        for action in action_list:
            child = self._result(state, action, player)
            if child.check_winner() == player:
                safe.append(action)
                continue
            if not self._has_immediate_winning_move(child, opponent):
                safe.append(action)
        return safe

    def _has_immediate_winning_move(self, state, player):
        target_row = BOARD_SIZE - 1 if player == 1 else 0
        for move in state.get_moves(player):
            if move[0] == target_row:
                return True
        return False

    def _state_key(self, state, current_player, depth):
        return (state.p1, state.p2,
                tuple(sorted(state.blocks)),
                tuple(sorted(state.fires)),
                current_player, depth)

    @staticmethod
    def _other(player):
        return 2 if player == 1 else 1

    @staticmethod
    def _row_progress(pos, player):
        return pos[0] if player == 1 else (BOARD_SIZE - 1 - pos[0])

    @staticmethod
    def _knight_distance_to_row(start, target_row, opponent, blocks, fires):
        """BFS distance from `start` to any cell in `target_row`."""
        visited = {start}
        queue = deque([(start, 0)])

        while queue:
            (r, c), depth = queue.popleft()
            if r == target_row:
                return depth

            for dr, dc in KNIGHT_DIRS:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE):
                    continue
                nxt = (nr, nc)
                if nxt in visited or nxt in blocks or nxt in fires or nxt == opponent:
                    continue
                visited.add(nxt)
                queue.append((nxt, depth + 1))

        return 99  # unreachable