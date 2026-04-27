import math
import time
from collections import deque

from game.rules import BOARD_SIZE, KNIGHT_DIRS


WIN_SCORE = 1_000_000


class SearchTimeout(Exception):
    pass


class MinimaxAgent:
    def __init__(self, player=2, depth=6, max_block_first=8, max_block_second=5, time_limit=0.9):
        self.player = player
        self.depth = depth
        self.max_block_first = max_block_first
        self.max_block_second = max_block_second
        self.time_limit = time_limit

        self.tt = {}

    def choose_action(self, state):
        deadline = time.perf_counter() + self.time_limit
        root_player = self.player

        root_actions = self._actions(state, root_player)
        if not root_actions:
            return None

        immediate_win = self._first_immediate_winning_action(state, root_player, root_actions)
        if immediate_win is not None:
            return immediate_win

        safe_actions = self._safe_actions(state, root_player, root_actions)
        if safe_actions:
            root_actions = safe_actions

        best_action = root_actions[0]
        best_score = -math.inf

        # Iterative deepening: always keep a valid best move before timeout.
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

    def _search_root(self, state, root_actions, depth, deadline):
        alpha = -math.inf
        beta = math.inf
        best_score = -math.inf
        best_action = root_actions[0]

        ordered_actions = self._order_actions(state, root_actions, self.player, depth)

        for action in ordered_actions:
            if time.perf_counter() >= deadline:
                raise SearchTimeout

            child = self._result(state, action, self.player)
            score = -self._negamax(
                child,
                depth - 1,
                -beta,
                -alpha,
                self._other(self.player),
                deadline,
            )

            if score > best_score:
                best_score = score
                best_action = action

            alpha = max(alpha, best_score)
            if alpha >= beta:
                break

        return best_score, best_action

    def _negamax(self, state, depth, alpha, beta, current_player, deadline):
        if time.perf_counter() >= deadline:
            raise SearchTimeout

        winner = state.check_winner()
        if winner is not None:
            if winner == self.player:
                return WIN_SCORE + depth
            return -WIN_SCORE - depth

        if depth <= 0:
            return self._evaluate(state)

        key = self._state_key(state, current_player, depth)
        tt_entry = self.tt.get(key)
        if tt_entry is not None:
            return tt_entry[0]

        actions = self._actions(state, current_player)
        if not actions:
            return self._evaluate(state)

        actions = self._order_actions(state, actions, current_player, depth)

        best_value = -math.inf
        best_action = actions[0]

        for action in actions:
            if time.perf_counter() >= deadline:
                raise SearchTimeout

            child = self._result(state, action, current_player)
            value = -self._negamax(
                child,
                depth - 1,
                -beta,
                -alpha,
                self._other(current_player),
                deadline,
            )

            if value > best_value:
                best_value = value
                best_action = action

            alpha = max(alpha, best_value)
            if alpha >= beta:
                break

        self.tt[key] = (best_value, best_action)
        return best_value

    def _actions(self, state, player):
        action_list = [("move", move) for move in state.get_moves(player)]

        if state.must_move(player):
            return action_list

        if not state.block_possible():
            return action_list

        first_cells = state.get_first_block_candidates(player)
        first_cells = self._rank_first_blocks(state, player, first_cells)
        if self.max_block_first is not None:
            first_cells = first_cells[: self.max_block_first]

        for first in first_cells:
            second_cells = state.get_second_block_candidates(player, first)
            second_cells = self._rank_second_blocks(state, player, first, second_cells)
            if self.max_block_second is not None:
                second_cells = second_cells[: self.max_block_second]

            for second in second_cells:
                action_list.append(("block", (first, second)))

        return action_list

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

            opponent_actions = self._actions(child, opponent)
            opp_can_win_next = False
            for opp_action in opponent_actions:
                opp_child = self._result(child, opp_action, opponent)
                if opp_child.check_winner() == opponent:
                    opp_can_win_next = True
                    break

            if not opp_can_win_next:
                safe.append(action)

        return safe

    def _order_actions(self, state, action_list, player, depth):
        opponent = self._other(player)

        def score(action):
            child = self._result(state, action, player)

            if child.check_winner() == player:
                return WIN_SCORE

            # Strongly prioritize defensive moves that remove immediate opponent wins.
            if self._has_immediate_winning_move(child, opponent):
                defense_penalty = -300_000
            else:
                defense_penalty = 20_000

            tt_hint = 0
            key = self._state_key(child, opponent, max(depth - 1, 0))
            if key in self.tt:
                tt_hint = 3_000

            action_bias = 250 if action[0] == "block" else 0
            return defense_penalty + tt_hint + action_bias + self._evaluate(child)

        reverse = player == self.player
        return sorted(action_list, key=score, reverse=reverse)

    def _evaluate(self, state):
        agent_pos = state.p1 if self.player == 1 else state.p2
        opponent = self._other(self.player)
        opponent_pos = state.p1 if opponent == 1 else state.p2

        agent_target = BOARD_SIZE - 1 if self.player == 1 else 0
        opp_target = BOARD_SIZE - 1 if opponent == 1 else 0

        agent_dist = self._knight_distance_to_row(agent_pos, agent_target, opponent_pos, state.blocks, state.fires)
        opp_dist = self._knight_distance_to_row(opponent_pos, opp_target, agent_pos, state.blocks, state.fires)

        # Tactical immediate win/loss pressure.
        if self._has_immediate_winning_move(state, self.player):
            return WIN_SCORE - 500
        if self._has_immediate_winning_move(state, opponent):
            return -WIN_SCORE + 500

        agent_moves = len(state.get_moves(self.player))
        opp_moves = len(state.get_moves(opponent))

        agent_blocks = len(state.get_first_block_candidates(self.player))
        opp_blocks = len(state.get_first_block_candidates(opponent))

        distance_score = (opp_dist - agent_dist) * 42
        mobility_score = (agent_moves - opp_moves) * 18
        block_control = (agent_blocks - opp_blocks) * 10

        progress_score = (self._row_progress(agent_pos, self.player) - self._row_progress(opponent_pos, opponent)) * 8

        return distance_score + mobility_score + block_control + progress_score

    def _has_immediate_winning_move(self, state, player):
        target_row = BOARD_SIZE - 1 if player == 1 else 0
        for move in state.get_moves(player):
            if move[0] == target_row:
                return True
        return False

    def _rank_first_blocks(self, state, player, first_cells):
        opponent = self._other(player)
        opponent_pos = state.p1 if opponent == 1 else state.p2
        return sorted(first_cells, key=lambda cell: self._manhattan(cell, opponent_pos))

    def _rank_second_blocks(self, state, player, first, second_cells):
        opponent = self._other(player)
        opponent_pos = state.p1 if opponent == 1 else state.p2
        return sorted(second_cells, key=lambda cell: self._manhattan(cell, opponent_pos) + self._manhattan(cell, first))

    def _state_key(self, state, current_player, depth):
        blocks_key = tuple(sorted(state.blocks))
        fires_key = tuple(sorted(state.fires))
        return (state.p1, state.p2, blocks_key, fires_key, current_player, depth)

    @staticmethod
    def _other(player):
        return 2 if player == 1 else 1

    @staticmethod
    def _row_progress(pos, player):
        return pos[0] if player == 1 else (BOARD_SIZE - 1 - pos[0])

    @staticmethod
    def _manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def _knight_distance_to_row(start, target_row, opponent, blocks, fires):
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
                if nxt in visited:
                    continue
                if nxt in blocks or nxt in fires or nxt == opponent:
                    continue

                visited.add(nxt)
                queue.append((nxt, depth + 1))

        return 99
