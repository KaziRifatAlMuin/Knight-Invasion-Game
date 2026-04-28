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
        # Reserved transposition table / cache. Currently not heavily used,
        # but left here for future speedups (store evaluated positions).
        self.tt = {}

    # ─────────────────────────────────────────────
    #  Public entry
    # ─────────────────────────────────────────────

    def choose_action(self, state):
        """Choose best action for `self.player` using bounded minimax.

        Workflow:
        1. Generate all legal actions (moves and bounded block pairs).
        2. Iteratively deepen the search from depth=1 up to configured depth.
           Each iteration calls the `minimax` entry point that runs alpha-beta
           via `max_value` / `min_value` functions.
        3. Respect a time `deadline` — if the deadline is reached a
           SearchTimeout is raised and the best action found so far is used.

        The iterative deepening pattern ensures we always return a legal
        action even when the time limit prevents a full-depth search.
        """

        deadline = time.perf_counter() + self.time_limit

        actions_list = actions(state, self.player, self.max_block_first, self.max_block_second)
        if not actions_list:
            return None

        best_action = actions_list[0]
        best_score = -math.inf

        # Iterative deepening: helps provide progressively better moves and
        # allows returning the best-so-far if time runs out.
        for search_depth in range(1, self.depth + 1):
            try:
                score, action = minimax(
                    state,
                    self.player,
                    search_depth,
                    self.max_block_first,
                    self.max_block_second,
                    deadline,
                )
            except SearchTimeout:
                break

            if action is not None:
                best_action = action
                best_score = score

            # Stop early if a decisive score is found.
            if best_score >= WIN_SCORE - 100:
                break

        return best_action


def actions(state, player, max_block_first=10, max_block_second=6):
    """
    Returns a list of all possible actions for the current player.
    Actions are either:
    - ("move", (row, col))
    - ("block", ((r1, c1), (r2, c2)))
    """

    move_actions = [("move", move) for move in state.get_moves(player)]

    if state.must_move(player) or not state.block_possible():
        return move_actions

    opponent = 2 if player == 1 else 1
    opp_moves = set(state.get_moves(opponent))
    opp_target_row = BOARD_SIZE - 1 if opponent == 1 else 0

    first_cells = state.get_first_block_candidates(player)

    def first_priority(cell):
        in_opp_reach = cell in opp_moves
        row_closeness = abs(cell[0] - opp_target_row)
        return (0 if in_opp_reach else 1, row_closeness)

    first_cells = sorted(first_cells, key=first_priority)
    if max_block_first:
        first_cells = first_cells[:max_block_first]

    block_actions = []
    for first in first_cells:
        second_cells = state.get_second_block_candidates(player, first)

        def second_priority(cell):
            in_opp_reach = cell in opp_moves
            row_closeness = abs(cell[0] - opp_target_row)
            return (0 if in_opp_reach else 1, row_closeness)

        second_cells = sorted(second_cells, key=second_priority)
        if max_block_second:
            second_cells = second_cells[:max_block_second]

        for second in second_cells:
            block_actions.append(("block", (first, second)))

    return move_actions + block_actions


def result(state, action, player):
    """
    Returns a new state after applying an action.
    """

    child = state.clone()
    action_type, payload = action

    if action_type == "move":
        child.apply_move(player, payload)
    else:
        c1, c2 = payload
        child.apply_block(player, c1, c2)

    return child


def terminal(state):
    """
    Returns True if the game is over, otherwise False.
    """

    return state.check_winner() is not None


def utility(state, agent):
    """
    Returns:
      1  if the agent wins
     -1  if the opponent wins
      0  otherwise, then a heuristic score is used for non-terminal states.
    """

    winner = state.check_winner()
    if winner == agent:
        return WIN_SCORE
    if winner is not None:
        return -WIN_SCORE
    return evaluate(state, agent)


def max_value(state, depth, alpha, beta, agent, max_block_first=10, max_block_second=6, deadline=None):
    """
        Compute the maximum utility value for the current state.

        This is the 'max' player in minimax. It performs alpha-beta pruning:

        - `alpha` is the best already explored option along the path to the root
            for the maximizer (lower bound).
        - `beta` is the best already explored option along the path to the root
            for the minimizer (upper bound).

        When we find a move with value >= beta, the minimizer above will avoid
        this branch so we can stop exploring (beta cutoff). Likewise updates to
        alpha tighten the bound and allow more pruning.

        The function returns (value, best_action) where `value` is the estimated
        utility for the maximizer and `best_action` is the action achieving it.
    """

    if deadline is not None and time.perf_counter() >= deadline:
        raise SearchTimeout

    if terminal(state) or depth == 0:
        return utility(state, agent), None

    value = -math.inf
    best_action = None

    for action in actions(state, agent, max_block_first, max_block_second):
        if deadline is not None and time.perf_counter() >= deadline:
            raise SearchTimeout

        child = result(state, action, agent)
        child_value, _ = min_value(
            child,
            depth - 1,
            alpha,
            beta,
            agent,
            max_block_first,
            max_block_second,
            deadline,
        )

        if child_value > value:
            value = child_value
            best_action = action

        alpha = max(alpha, value)
        if alpha >= beta:
            # Alpha-beta cutoff: no need to check remaining sibling moves.
            break

    return value, best_action


def min_value(state, depth, alpha, beta, agent, max_block_first=10, max_block_second=6, deadline=None):
    """
    Compute the minimum utility value for the current state.

    This mirrors `max_value` but for the opponent. It minimizes the utility
    and also uses alpha-beta pruning. When a value <= alpha is found, the
    maximizer above will avoid this branch (alpha cutoff) and we can stop.
    """

    if deadline is not None and time.perf_counter() >= deadline:
        raise SearchTimeout

    if terminal(state) or depth == 0:
        return utility(state, agent), None

    opponent = 2 if agent == 1 else 1
    value = math.inf
    best_action = None

    for action in actions(state, opponent, max_block_first, max_block_second):
        if deadline is not None and time.perf_counter() >= deadline:
            raise SearchTimeout

        child = result(state, action, opponent)
        child_value, _ = max_value(
            child,
            depth - 1,
            alpha,
            beta,
            agent,
            max_block_first,
            max_block_second,
            deadline,
        )

        if child_value < value:
            value = child_value
            best_action = action

        beta = min(beta, value)
        if beta <= alpha:
            # Beta cutoff: this branch cannot influence the minimizer's parent.
            break

    return value, best_action


def bfs_distance(state, start, target_row, opponent):
    """Return approximate shortest knight-move distance from `start` to any
    cell on `target_row` while avoiding `blocks`, `fires`, and the `opponent`.

    This BFS is a cheap heuristic used by the evaluation function to estimate
    how close a knight is to its goal row. It is not aware of future block
    placements; it simply measures reachability given the current obstacles.
    """

    visited = {start}
    queue = deque([(start, 0)])

    while queue:
        (r, c), distance = queue.popleft()
        if r == target_row:
            return distance

        for dr, dc in KNIGHT_DIRS:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE):
                continue
            nxt = (nr, nc)
            if nxt in visited or nxt in state.blocks or nxt in state.fires or nxt == opponent:
                continue
            visited.add(nxt)
            queue.append((nxt, distance + 1))

    return 99


def evaluate(state, agent):
    """Heuristic evaluation of non-terminal states.

    The evaluation combines several signals (ordered by importance):
    1. BFS distance for both players (most important).
    2. Row progress (how far along the board the knight is).
    3. Mobility (available knight moves).
    4. Blocking potential (how many first-block candidates are available).

    Positive scores favor `agent`, negative scores favor the opponent.
    """

    opponent = 2 if agent == 1 else 1

    agent_pos = state.p1 if agent == 1 else state.p2
    opp_pos = state.p1 if opponent == 1 else state.p2

    agent_target = BOARD_SIZE - 1 if agent == 1 else 0
    opp_target = BOARD_SIZE - 1 if opponent == 1 else 0

    agent_dist = bfs_distance(state, agent_pos, agent_target, opp_pos)
    opp_dist = bfs_distance(state, opp_pos, opp_target, agent_pos)

    if agent_dist == 99:
        return -WIN_SCORE + 200
    if opp_dist == 99:
        return WIN_SCORE - 200

    agent_moves = len(state.get_moves(agent))
    opp_moves = len(state.get_moves(opponent))

    agent_block_power = len(state.get_first_block_candidates(agent)) if not state.must_move(agent) else 0
    opp_block_power = len(state.get_first_block_candidates(opponent)) if not state.must_move(opponent) else 0

    agent_progress = agent_pos[0] if agent == 1 else (BOARD_SIZE - 1 - agent_pos[0])
    opp_progress = opp_pos[0] if opponent == 1 else (BOARD_SIZE - 1 - opp_pos[0])

    score = 0
    score += (opp_dist - agent_dist) * 500
    score += (agent_progress - opp_progress) * 60
    score += (agent_moves - opp_moves) * 20
    score += (agent_block_power - opp_block_power) * 8

    return score


def minimax(state, agent, depth=6, max_block_first=10, max_block_second=6, deadline=None):
    """
    Returns the best (value, action) for the current player.
    """

    if deadline is not None and time.perf_counter() >= deadline:
        raise SearchTimeout

    return max_value(
        state,
        depth,
        -math.inf,
        math.inf,
        agent,
        max_block_first,
        max_block_second,
        deadline,
    )