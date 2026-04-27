import math
from collections import deque

from game.rules import BOARD_SIZE, KNIGHT_DIRS


class MinimaxAgent:
	def __init__(self, player=2, depth=2, max_block_first=8, max_block_second=6):
		self.player = player
		self.depth = depth
		self.max_block_first = max_block_first
		self.max_block_second = max_block_second

	def choose_action(self, state):
		_, action = minimax(
			state,
			agent_player=self.player,
			depth=self.depth,
			max_block_first=self.max_block_first,
			max_block_second=self.max_block_second,
			current_player=self.player,
		)
		if action is not None:
			return action

		fallback_moves = actions(state, self.player)
		for action in fallback_moves:
			if action[0] == "move":
				return action
		return fallback_moves[0] if fallback_moves else None


def terminal(state):
	return state.check_winner() is not None


def utility(state, agent_player):
	winner = state.check_winner()
	if winner == agent_player:
		return 100000
	if winner is not None:
		return -100000
	return evaluate(state, agent_player)


def actions(state, player, agent_player=None, max_block_first=8, max_block_second=6):
	legal_actions = [("move", move) for move in state.get_moves(player)]

	if state.must_move(player) or not state.block_possible():
		return sort_actions(state, legal_actions, player, agent_player or player)

	first_cells = state.get_first_block_candidates(player)
	first_cells = rank_first_blocks(state, player, first_cells)[:max_block_first]

	for first in first_cells:
		seconds = state.get_second_block_candidates(player, first)
		seconds = rank_second_blocks(state, player, first, seconds)[:max_block_second]
		for second in seconds:
			legal_actions.append(("block", (first, second)))

	return sort_actions(state, legal_actions, player, agent_player or player)


def result(state, action, player):
	new_state = state.clone()
	action_type, payload = action
	if action_type == "move":
		new_state.apply_move(player, payload)
	else:
		c1, c2 = payload
		new_state.apply_block(player, c1, c2)
	return new_state


def max_value(state, depth, alpha, beta, agent_player, current_player, max_block_first, max_block_second):
	if terminal(state) or depth == 0:
		return utility(state, agent_player), None

	value = -math.inf
	best_action = None
	for action in actions(state, current_player, agent_player, max_block_first, max_block_second):
		new_state = result(state, action, current_player)
		eval_value, _ = min_value(
			new_state,
			depth - 1,
			alpha,
			beta,
			agent_player,
			other_player(current_player),
			max_block_first,
			max_block_second,
		)
		if eval_value > value:
			value, best_action = eval_value, action
		alpha = max(alpha, value)
		if alpha >= beta:
			break
	return value, best_action


def min_value(state, depth, alpha, beta, agent_player, current_player, max_block_first, max_block_second):
	if terminal(state) or depth == 0:
		return utility(state, agent_player), None

	value = math.inf
	best_action = None
	for action in actions(state, current_player, agent_player, max_block_first, max_block_second):
		new_state = result(state, action, current_player)
		eval_value, _ = max_value(
			new_state,
			depth - 1,
			alpha,
			beta,
			agent_player,
			other_player(current_player),
			max_block_first,
			max_block_second,
		)
		if eval_value < value:
			value, best_action = eval_value, action
		beta = min(beta, value)
		if alpha >= beta:
			break
	return value, best_action


def minimax(state, agent_player=2, depth=2, max_block_first=8, max_block_second=6, current_player=None):
	if current_player is None:
		current_player = agent_player

	if current_player == agent_player:
		return max_value(
			state,
			depth,
			-math.inf,
			math.inf,
			agent_player,
			current_player,
			max_block_first,
			max_block_second,
		)
	return min_value(
		state,
		depth,
		-math.inf,
		math.inf,
		agent_player,
		current_player,
		max_block_first,
		max_block_second,
	)


def evaluate(state, agent_player):
	agent_pos = state.p1 if agent_player == 1 else state.p2
	opponent = other_player(agent_player)
	opponent_pos = state.p1 if opponent == 1 else state.p2

	agent_target = BOARD_SIZE - 1 if agent_player == 1 else 0
	opponent_target = BOARD_SIZE - 1 if opponent == 1 else 0

	agent_dist = knight_distance_to_row(agent_pos, agent_target, opponent_pos, state.blocks, state.fires)
	opponent_dist = knight_distance_to_row(opponent_pos, opponent_target, agent_pos, state.blocks, state.fires)

	dist_score = (opponent_dist - agent_dist) * 30
	mobility_score = (len(state.get_moves(agent_player)) - len(state.get_moves(opponent))) * 6
	progress_score = row_progress(agent_pos, agent_player) - row_progress(opponent_pos, opponent)
	return dist_score + mobility_score + (progress_score * 3)


def sort_actions(state, action_list, player, agent_player):
	return sorted(action_list, key=lambda action: action_priority(state, action, player, agent_player), reverse=(player == agent_player))


def action_priority(state, action, player, agent_player):
	child = result(state, action, player)
	return evaluate(child, agent_player)


def rank_first_blocks(state, player, first_cells):
	opponent = other_player(player)
	opponent_pos = state.p1 if opponent == 1 else state.p2
	return sorted(first_cells, key=lambda cell: manhattan(cell, opponent_pos))


def rank_second_blocks(state, player, first, second_cells):
	opponent = other_player(player)
	opponent_pos = state.p1 if opponent == 1 else state.p2
	return sorted(second_cells, key=lambda cell: manhattan(cell, opponent_pos) + manhattan(cell, first))


def other_player(player):
	return 2 if player == 1 else 1


def row_progress(pos, player):
	return pos[0] if player == 1 else (BOARD_SIZE - 1 - pos[0])


def manhattan(a, b):
	return abs(a[0] - b[0]) + abs(a[1] - b[1])


def knight_distance_to_row(start, target_row, opponent, blocks, fires):
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
