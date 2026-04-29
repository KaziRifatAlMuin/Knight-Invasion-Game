# main.py

import random
import sys

import pygame

from agents.fuzzy_agent import FuzzyAgent
from agents.minimax_agent import MinimaxAgent
from game.board import Board, HEIGHT, WIDTH
from game.rules import GameState


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Knight Invasion")
clock = pygame.time.Clock()

TITLE_FONT = pygame.font.SysFont("bahnschrift", 52, bold=True)
HEADER_FONT = pygame.font.SysFont("bahnschrift", 34, bold=True)
TEXT_FONT = pygame.font.SysFont("bahnschrift", 22)
SMALL_FONT = pygame.font.SysFont("bahnschrift", 17)

BG_TOP = (6, 10, 24)
BG_BOTTOM = (2, 4, 12)
AI_BLUE = (0, 102, 255)
AI_RED = (220, 20, 60)
PLAYER_YELLOW = (255, 195, 30)
ACCENT_CYAN = (52, 247, 255)
# stone color (hex #9c7a5a -> rgb 156,122,90)
BLOCK_NEUTRAL = (156, 122, 90)


def draw_vertical_gradient(surface, top_color, bottom_color):
    width, height = surface.get_size()
    for y in range(height):
        t = y / max(1, height - 1)
        color = (
            int(top_color[0] + (bottom_color[0] - top_color[0]) * t),
            int(top_color[1] + (bottom_color[1] - top_color[1]) * t),
            int(top_color[2] + (bottom_color[2] - top_color[2]) * t),
        )
        pygame.draw.line(surface, color, (0, y), (width, y))


def draw_menu_button(rect, label, sublabel="", hovered=False):
    fill = (17, 25, 46) if not hovered else (20, 36, 66)
    border = (0, 229, 255) if hovered else (138, 92, 255)
    pygame.draw.rect(screen, fill, rect, border_radius=14)
    pygame.draw.rect(screen, border, rect, 2, border_radius=14)
    if hovered:
        pygame.draw.rect(screen, (255, 62, 163), rect.inflate(-5, -5), 1, border_radius=12)

    text = TEXT_FONT.render(label, True, (245, 250, 255))
    screen.blit(text, (rect.x + 18, rect.y + 14))

    if sublabel:
        sub = SMALL_FONT.render(sublabel, True, (158, 181, 219))
        screen.blit(sub, (rect.x + 18, rect.y + 43))


def show_mode_menu():
    options = [
        ("Two Player", "Local hot-seat duel"),
        ("Player vs Minimax AI", "You vs the Minimax AI"),
        ("Player vs Fuzzy AI", "You vs the Fuzzy AI"),
        ("Minimax AI vs Fuzzy AI", "AI duel: Minimax vs Fuzzy"),
    ]

    buttons = []
    start_y = 180
    for i in range(4):
        buttons.append(pygame.Rect(70, start_y + i * 98, WIDTH - 140, 78))

    while True:
        draw_vertical_gradient(screen, BG_TOP, BG_BOTTOM)

        title = TITLE_FONT.render("KNIGHT INVASION", True, (245, 250, 255))
        subtitle = SMALL_FONT.render("Choose game mode", True, (158, 181, 219))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 64))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 126))

        mouse = pygame.mouse.get_pos()

        for i, btn in enumerate(buttons):
            draw_menu_button(btn, options[i][0], options[i][1], btn.collidepoint(mouse))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for idx, btn in enumerate(buttons):
                    if btn.collidepoint(event.pos):
                        return idx

        clock.tick(60)


def choose_difficulty_fire_count():
    levels = [
        ("Easy", "4-8 fires", 4, 8),
        ("Medium", "8-12 fires", 8, 12),
        ("Hard", "12-16 fires", 12, 16),
    ]

    buttons = [
        pygame.Rect(130, 220 + i * 105, WIDTH - 260, 84)
        for i in range(3)
    ]

    while True:
        draw_vertical_gradient(screen, BG_TOP, BG_BOTTOM)

        title = HEADER_FONT.render("SELECT DIFFICULTY", True, (245, 250, 255))
        subtitle = SMALL_FONT.render("Difficulty controls total fire cells", True, (158, 181, 219))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 112))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 158))

        mouse = pygame.mouse.get_pos()

        for i, btn in enumerate(buttons):
            label = levels[i][0]
            sub = levels[i][1]
            draw_menu_button(btn, label, sub, btn.collidepoint(mouse))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn in enumerate(buttons):
                    if btn.collidepoint(event.pos):
                        low, high = levels[i][2], levels[i][3]
                        even_counts = [n for n in range(low, high + 1) if n % 2 == 0]
                        return random.choice(even_counts)

        clock.tick(60)


def show_win_screen(winner, mode_name=""):
    restart_btn = pygame.Rect(WIDTH // 2 - 200, HEIGHT - 150, 180, 58)
    quit_btn = pygame.Rect(WIDTH // 2 + 20, HEIGHT - 150, 180, 58)

    if mode_name == "Two Player":
        winner_name = "Player 1" if winner == 1 else "Player 2"
        winner_color = (0, 229, 255) if winner == 1 else (255, 62, 163)
    elif mode_name == "Player vs Minimax AI":
        winner_name = "You" if winner == 2 else "Minimax AI"
        winner_color = (255, 195, 30) if winner == 2 else (0, 102, 255)
    elif mode_name == "Player vs Fuzzy AI":
        winner_name = "You" if winner == 2 else "Fuzzy AI"
        winner_color = (255, 195, 30) if winner == 2 else (220, 20, 60)
    elif mode_name == "Minimax AI vs Fuzzy AI":
        winner_name = "Minimax AI" if winner == 1 else "Fuzzy AI"
        winner_color = (0, 102, 255) if winner == 1 else (220, 20, 60)
    else:
        winner_name = "Winner"
        winner_color = (245, 250, 255)

    while True:
        draw_vertical_gradient(screen, BG_TOP, BG_BOTTOM)

        title = TITLE_FONT.render("VICTORY", True, (245, 250, 255))
        text = HEADER_FONT.render(f"{winner_name} won!", True, winner_color)
        hint = SMALL_FONT.render("Play again or exit the arena", True, (158, 181, 219))

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 236))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 286))

        mouse = pygame.mouse.get_pos()
        draw_menu_button(restart_btn, "Play Again", "", restart_btn.collidepoint(mouse))
        draw_menu_button(quit_btn, "Quit", "", quit_btn.collidepoint(mouse))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn.collidepoint(event.pos):
                    return True
                if quit_btn.collidepoint(event.pos):
                    return False

        clock.tick(60)


def start_flow():
    while True:
        mode_idx = show_mode_menu()
        fire_count = choose_difficulty_fire_count()
        return mode_idx, fire_count


def _safe_quit_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()


class SwappedStateView:
    """Read-only view that swaps player 1 and player 2 for AI logic."""

    def __init__(self, state):
        self._state = state
        self.p1 = state.p2
        self.p2 = state.p1
        self.blocks = state.blocks
        self.fires = state.fires

    def _swap_player(self, player):
        return 3 - player

    def clone(self):
        return SwappedStateView(self._state.clone())

    def get_moves(self, player):
        return self._state.get_moves(self._swap_player(player))

    def must_move(self, player):
        return self._state.must_move(self._swap_player(player))

    def can_block(self, player, c1, c2):
        return self._state.can_block(self._swap_player(player), c1, c2)

    def block_possible(self):
        return self._state.block_possible()

    def get_open_cells(self):
        return self._state.get_open_cells()

    def get_first_block_candidates(self, player):
        return self._state.get_first_block_candidates(self._swap_player(player))

    def get_second_block_candidates(self, player, first):
        return self._state.get_second_block_candidates(self._swap_player(player), first)

    def check_winner(self):
        return self._state.check_winner()


def animate_move(board, state, player, start_pos, end_pos, info, can_block, must_move, role_items, focus_text, focus_color, token_colors, mode="choose", highlights=None, selected=None, frames=24, active_color=None):
    if highlights is None:
        highlights = []
    for step in range(frames):
        _safe_quit_events()
        progress = (step + 1) / frames
        board.draw(
            state,
            mode,
            highlights,
            selected,
            info,
            can_block,
            must_move,
            role_items=role_items,
            focus_text=focus_text,
            focus_color=focus_color,
            active_color=active_color,
            moving_player=player,
            moving_start=start_pos,
            moving_end=end_pos,
            moving_t=progress,
            token_colors=token_colors,
        )
        clock.tick(60)


def _block_origin_for_player(player):
    return "top" if player == 1 else "bottom"


def animate_block(board, state, block_cells, info, can_block, must_move, role_items, focus_text, focus_color, token_colors, mode="choose", highlights=None, selected=None, delay_ms=500, duration_ms=1500, active_color=None, block_anim_origin="top"):
    if highlights is None:
        highlights = []
    block_cells = list(block_cells)
    if delay_ms > 0:
        start = pygame.time.get_ticks()
        while True:
            _safe_quit_events()
            elapsed = pygame.time.get_ticks() - start
            progress = min(1.0, elapsed / max(1, delay_ms))
            board.draw(
                state,
                "block2",
                highlights,
                selected,
                info,
                can_block,
                must_move,
                role_items=role_items,
                focus_text=focus_text,
                focus_color=focus_color,
                active_color=active_color,
                block_anim_origin=block_anim_origin,
                token_colors=token_colors,
            )
            if progress >= 1.0:
                break
            clock.tick(60)

    start = pygame.time.get_ticks()
    while True:
        _safe_quit_events()
        elapsed = pygame.time.get_ticks() - start
        progress = min(1.0, elapsed / max(1, duration_ms))
        # while the block animation runs, hide available-cell highlights
        board.draw(
            state,
            mode,
            [],
            selected,
            info,
            can_block,
            must_move,
            role_items=role_items,
            focus_text=focus_text,
            focus_color=focus_color,
            active_color=active_color,
            block_anim_cells=block_cells,
            block_anim_t=progress,
            block_anim_origin=block_anim_origin,
            token_colors=token_colors,
        )
        if progress >= 1.0:
            break
        clock.tick(60)


def main_game_2player(fire_count):
    """Two Player mode"""
    state = GameState(fire_count)
    board = Board(screen)

    player = 1
    mode = "choose"
    selected = None
    highlights = []
    message = "Choose MOVE or BLOCK"
    role_items = [
        (AI_BLUE, "Player 1"),
        (AI_RED, "Player 2"),
    ]

    while True:
        winner = state.check_winner()
        if winner:
            return winner

        must_move = state.must_move(player)
        can_block = state.block_possible()

        if must_move:
            message = "Adjacent to fire: you must move"
        elif mode == "choose":
            message = "Choose MOVE or BLOCK"

        board.draw(
            state,
            mode,
            highlights,
            selected,
            f"Player {player} | {message}",
            can_block,
            must_move,
            role_items=role_items,
            focus_text="TWO PLAYER MODE",
            focus_color=ACCENT_CYAN,
            active_color=AI_BLUE if player == 1 else AI_RED,
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type != pygame.MOUSEBUTTONDOWN:
                continue

            pos = event.pos
            btn = board.get_button(pos)

            if btn == "move":
                mode = "move"
                selected = None
                highlights = state.get_moves(player)
                message = "Select one highlighted destination"
                continue

            if btn == "block":
                if must_move:
                    message = "Blocking disabled: you are adjacent to fire"
                elif not can_block:
                    message = "Blocking disabled: no valid two-cell block"
                else:
                    mode = "block1"
                    selected = None
                    highlights = state.get_first_block_candidates(player)
                    message = "Pick first block cell"
                continue

            cell = board.get_cell(pos)
            if cell is None:
                continue

            if mode == "move":
                if cell in highlights:
                    start_pos = state.p1 if player == 1 else state.p2
                    animate_move(
                        board,
                        state,
                        player,
                        start_pos,
                        cell,
                        f"Player {player} | {message}",
                        can_block,
                        must_move,
                        role_items,
                        "TWO PLAYER MODE",
                        ACCENT_CYAN,
                        token_colors=(AI_BLUE, AI_RED),
                        mode="move",
                        highlights=highlights,
                        selected=selected,
                            active_color=AI_BLUE if player == 1 else AI_RED,
                    )
                    state.apply_move(player, cell)
                    player = 3 - player
                    mode = "choose"
                    selected = None
                    highlights = []
                    message = "Turn switched"
                continue

            if mode == "block1":
                if cell in highlights:
                    selected = cell
                    mode = "block2"
                    highlights = state.get_second_block_candidates(player, selected)
                    if highlights:
                        message = "Pick second block cell"
                    else:
                        mode = "block1"
                        selected = None
                        highlights = state.get_first_block_candidates(player)
                        message = "That first choice has no pair; pick another"
                continue

            if mode == "block2":
                if cell in highlights:
                    if state.apply_block(player, selected, cell):
                        animate_block(
                            board,
                            state,
                            [selected, cell],
                            f"Player {player} | Blocks placed",
                            can_block,
                            must_move,
                            role_items,
                            "TWO PLAYER MODE",
                            ACCENT_CYAN,
                            token_colors=(AI_BLUE, AI_RED),
                            mode="block2",
                            highlights=highlights,
                            selected=[selected, cell],
                            active_color=AI_BLUE if player == 1 else AI_RED,
                            block_anim_origin=_block_origin_for_player(player),
                        )
                        player = 3 - player
                        mode = "choose"
                        selected = None
                        highlights = []
                        message = "Blocks placed. Turn switched"
                    else:
                        mode = "block1"
                        selected = None
                        highlights = state.get_first_block_candidates(player)
                        message = "Invalid pair; choose again"
                elif cell == selected:
                    mode = "block1"
                    selected = None
                    highlights = state.get_first_block_candidates(player)
                    message = "First block unselected"

        clock.tick(60)


def main_game_player_vs_fuzzy(fire_count):
    """Player vs Fuzzy AI mode"""
    state = GameState(fire_count)
    board = Board(screen)
    fuzzy_agent = FuzzyAgent()

    player = 2
    mode = "choose"
    selected = None
    highlights = []
    message = "Your turn! Choose MOVE or BLOCK"
    ai_timer = 0
    AI_DELAY = 700
    AI_COLOR = AI_RED
    token_colors = (AI_COLOR, PLAYER_YELLOW)

    while True:
        winner = state.check_winner()
        if winner:
            return winner

        must_move = state.must_move(player)
        can_block = state.block_possible()

        if player == 1:
            role_items = [
                (AI_COLOR, "Fuzzy AI"),
                (PLAYER_YELLOW, "You"),
            ]
            board.draw(
                state,
                mode,
                highlights,
                selected,
                "Fuzzy AI is thinking...",
                can_block,
                must_move,
                role_items=role_items,
                focus_text="FUZZY AI TURN",
                focus_color=AI_COLOR,
                token_colors=token_colors,
            )

            if ai_timer == 0:
                ai_timer = pygame.time.get_ticks()

            if pygame.time.get_ticks() - ai_timer >= AI_DELAY:
                action = fuzzy_agent.decide_action(SwappedStateView(state), 2)

                if action and action[0] == "move":
                    move_pos = action[1]
                    animate_move(
                        board,
                        state,
                        1,
                        state.p1,
                        move_pos,
                        "Fuzzy AI is thinking...",
                        can_block,
                        must_move,
                        role_items,
                        "FUZZY AI TURN",
                        AI_COLOR,
                        token_colors,
                        mode="move",
                        highlights=highlights,
                        selected=selected,
                        frames=28,
                    )
                    state.apply_move(1, move_pos)
                    print(f"🤖 Fuzzy AI moved to {move_pos}")

                elif action and action[0] == "block":
                    _, (c1, c2) = action
                    animate_block(
                        board,
                        state,
                        [c1, c2],
                        "Fuzzy AI is thinking...",
                        can_block,
                        must_move,
                        role_items,
                        "FUZZY AI TURN",
                        AI_COLOR,
                        token_colors,
                        mode="block2",
                        highlights=highlights,
                        selected=[c1, c2],
                        duration_ms=1500,
                        delay_ms=500,
                        block_anim_origin="top",
                    )
                    if state.apply_block(1, c1, c2):
                        print(f"🤖 Fuzzy AI blocked {c1}, {c2}")

                player = 2
                mode = "choose"
                selected = None
                highlights = []
                ai_timer = 0
            else:
                clock.tick(60)
                continue
        else:
            if must_move:
                message = "Adjacent to fire: you must move"
            elif mode == "choose":
                message = "Your turn! Choose MOVE or BLOCK"

            role_items = [
                (AI_COLOR, "Fuzzy AI"),
                (PLAYER_YELLOW, "You"),
            ]
            board.draw(
                state,
                mode,
                highlights,
                selected,
                f"YOUR TURN | {message}",
                can_block,
                must_move,
                role_items=role_items,
                focus_text="YOUR TURN",
                focus_color=PLAYER_YELLOW,
                token_colors=token_colors,
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type != pygame.MOUSEBUTTONDOWN:
                    continue

                pos = event.pos
                btn = board.get_button(pos)

                if btn == "move":
                    mode = "move"
                    selected = None
                    highlights = state.get_moves(2)
                    message = "Select a highlighted destination"
                    continue

                if btn == "block":
                    if must_move:
                        message = "Blocking disabled: you are adjacent to fire"
                    elif not can_block:
                        message = "Blocking disabled: no valid two-cell block"
                    else:
                        mode = "block1"
                        selected = None
                        highlights = state.get_first_block_candidates(2)
                        message = "Pick first block cell"
                    continue

                cell = board.get_cell(pos)
                if cell is None:
                    continue

                if mode == "move":
                    if cell in highlights:
                        animate_move(
                            board,
                            state,
                            2,
                            state.p2,
                            cell,
                            f"YOUR TURN | {message}",
                            can_block,
                            must_move,
                            role_items,
                            "YOUR TURN",
                            PLAYER_YELLOW,
                            token_colors,
                            mode="move",
                            highlights=highlights,
                            selected=selected,
                            frames=24,
                        )
                        state.apply_move(2, cell)
                        player = 1
                        mode = "choose"
                        selected = None
                        highlights = []
                        message = "AI is thinking..."
                        print(f"👤 Player moved to {cell}")
                    continue

                if mode == "block1":
                    if cell in highlights:
                        selected = cell
                        mode = "block2"
                        highlights = state.get_second_block_candidates(2, selected)
                        if highlights:
                            message = "Pick second block cell"
                        else:
                            mode = "block1"
                            selected = None
                            highlights = state.get_first_block_candidates(2)
                            message = "That first choice has no pair; pick another"
                    continue

                if mode == "block2":
                    if cell in highlights:
                        animate_block(
                            board,
                            state,
                            [selected, cell],
                            f"YOUR TURN | {message}",
                            can_block,
                            must_move,
                            role_items,
                            "YOUR TURN",
                            PLAYER_YELLOW,
                            token_colors,
                            mode="block2",
                            highlights=highlights,
                            selected=[selected, cell],
                            duration_ms=1500,
                            delay_ms=500,
                            block_anim_origin=_block_origin_for_player(2),
                        )
                        if state.apply_block(2, selected, cell):
                            player = 1
                            mode = "choose"
                            selected = None
                            highlights = []
                            message = "Blocks placed. AI is thinking..."
                            print(f"👤 Player blocked {selected} and {cell}")
                        else:
                            mode = "block1"
                            selected = None
                            highlights = state.get_first_block_candidates(2)
                            message = "Invalid pair; choose again"
                    elif cell == selected:
                        mode = "block1"
                        selected = None
                        highlights = state.get_first_block_candidates(2)
                        message = "First block unselected"

        clock.tick(60)


def main_game_player_vs_minimax(fire_count):
    """Player vs Minimax AI mode"""
    state = GameState(fire_count)
    board = Board(screen)
    minimax_agent = MinimaxAgent(player=1, depth=6, max_block_first=8, max_block_second=5, time_limit=0.9)

    player = 2
    mode = "choose"
    selected = None
    highlights = []
    message = "Your turn! Choose MOVE or BLOCK"
    ai_timer = 0
    AI_DELAY = 700
    AI_COLOR = AI_BLUE
    token_colors = (AI_COLOR, PLAYER_YELLOW)

    while True:
        winner = state.check_winner()
        if winner:
            return winner

        must_move = state.must_move(player)
        can_block = state.block_possible()

        if player == 1:
            role_items = [
                (AI_COLOR, "Minimax AI"),
                (PLAYER_YELLOW, "You"),
            ]
            board.draw(
                state,
                mode,
                highlights,
                selected,
                "Minimax AI is thinking...",
                can_block,
                must_move,
                role_items=role_items,
                focus_text="MINIMAX AI TURN",
                focus_color=AI_COLOR,
                token_colors=token_colors,
            )

            if ai_timer == 0:
                ai_timer = pygame.time.get_ticks()

            if pygame.time.get_ticks() - ai_timer >= AI_DELAY:
                action = minimax_agent.choose_action(state)

                if action and action[0] == "move":
                    move_pos = action[1]
                    animate_move(
                        board,
                        state,
                        1,
                        state.p1,
                        move_pos,
                        "Minimax AI is thinking...",
                        can_block,
                        must_move,
                        role_items,
                        "MINIMAX AI TURN",
                        AI_COLOR,
                        token_colors,
                        mode="move",
                        highlights=highlights,
                        selected=selected,
                        frames=28,
                    )
                    state.apply_move(1, move_pos)
                    print(f"🤖 Minimax AI moved to {move_pos}")

                elif action and action[0] == "block":
                    c1, c2 = action[1]
                    animate_block(
                        board,
                        state,
                        [c1, c2],
                        "Minimax AI is thinking...",
                        can_block,
                        must_move,
                        role_items,
                        "MINIMAX AI TURN",
                        AI_COLOR,
                        token_colors,
                        mode="block2",
                        highlights=highlights,
                        selected=[c1, c2],
                        duration_ms=1500,
                        delay_ms=500,
                        block_anim_origin="top",
                    )
                    if state.apply_block(1, c1, c2):
                        print(f"🤖 Minimax AI blocked {c1}, {c2}")

                player = 2
                mode = "choose"
                selected = None
                highlights = []
                ai_timer = 0
            else:
                clock.tick(60)
                continue
        else:
            if must_move:
                message = "Adjacent to fire: you must move"
            elif mode == "choose":
                message = "Your turn! Choose MOVE or BLOCK"

            role_items = [
                (AI_COLOR, "Minimax AI"),
                (PLAYER_YELLOW, "You"),
            ]
            board.draw(
                state,
                mode,
                highlights,
                selected,
                f"YOUR TURN | {message}",
                can_block,
                must_move,
                role_items=role_items,
                focus_text="YOUR TURN",
                focus_color=PLAYER_YELLOW,
                token_colors=token_colors,
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type != pygame.MOUSEBUTTONDOWN:
                    continue

                pos = event.pos
                btn = board.get_button(pos)

                if btn == "move":
                    mode = "move"
                    selected = None
                    highlights = state.get_moves(2)
                    message = "Select a highlighted destination"
                    continue

                if btn == "block":
                    if must_move:
                        message = "Blocking disabled: you are adjacent to fire"
                    elif not can_block:
                        message = "Blocking disabled: no valid two-cell block"
                    else:
                        mode = "block1"
                        selected = None
                        highlights = state.get_first_block_candidates(2)
                        message = "Pick first block cell"
                    continue

                cell = board.get_cell(pos)
                if cell is None:
                    continue

                if mode == "move":
                    if cell in highlights:
                        animate_move(
                            board,
                            state,
                            2,
                            state.p2,
                            cell,
                            f"YOUR TURN | {message}",
                            can_block,
                            must_move,
                            role_items,
                            "YOUR TURN",
                            PLAYER_YELLOW,
                            token_colors,
                            mode="move",
                            highlights=highlights,
                            selected=selected,
                            frames=24,
                        )
                        state.apply_move(2, cell)
                        player = 1
                        mode = "choose"
                        selected = None
                        highlights = []
                        message = "AI is thinking..."
                        print(f"👤 Player moved to {cell}")
                    continue

                if mode == "block1":
                    if cell in highlights:
                        selected = cell
                        mode = "block2"
                        highlights = state.get_second_block_candidates(2, selected)
                        if highlights:
                            message = "Pick second block cell"
                        else:
                            mode = "block1"
                            selected = None
                            highlights = state.get_first_block_candidates(2)
                            message = "That first choice has no pair; pick another"
                    continue

                if mode == "block2":
                    if cell in highlights:
                        animate_block(
                            board,
                            state,
                            [selected, cell],
                            f"YOUR TURN | {message}",
                            can_block,
                            must_move,
                            role_items,
                            "YOUR TURN",
                            PLAYER_YELLOW,
                            token_colors,
                            mode="block2",
                            highlights=highlights,
                            selected=[selected, cell],
                            duration_ms=1500,
                            delay_ms=500,
                            block_anim_origin=_block_origin_for_player(2),
                        )
                        if state.apply_block(2, selected, cell):
                            player = 1
                            mode = "choose"
                            selected = None
                            highlights = []
                            message = "Blocks placed. AI is thinking..."
                            print(f"👤 Player blocked {selected} and {cell}")
                        else:
                            mode = "block1"
                            selected = None
                            highlights = state.get_first_block_candidates(2)
                            message = "Invalid pair; choose again"
                    elif cell == selected:
                        mode = "block1"
                        selected = None
                        highlights = state.get_first_block_candidates(2)
                        message = "First block unselected"

        clock.tick(60)


def main_game_minimax_vs_fuzzy(fire_count):
    """Minimax AI vs Fuzzy AI mode"""
    state = GameState(fire_count)
    board = Board(screen)
    minimax_agent = MinimaxAgent(player=1, depth=6, max_block_first=8, max_block_second=5, time_limit=0.9)
    fuzzy_agent = FuzzyAgent()

    player = 1
    ai_timer = 0
    AI_DELAY = 700
    role_items = [
        (AI_BLUE, "Minimax AI"),
        (AI_RED, "Fuzzy AI"),
    ]

    while True:
        winner = state.check_winner()
        if winner:
            return winner

        must_move = state.must_move(player)
        can_block = state.block_possible()

        agent_name = "Minimax AI" if player == 1 else "Fuzzy AI"
        agent_color = AI_BLUE if player == 1 else AI_RED

        board.draw(
            state,
            "choose",
            [],
            None,
            f"{agent_name} is thinking...",
            can_block,
            must_move,
            role_items=role_items,
            focus_text=f"{agent_name.upper()} TURN",
            focus_color=agent_color,
            token_colors=(AI_BLUE, AI_RED),
        )

        _safe_quit_events()

        if ai_timer == 0:
            ai_timer = pygame.time.get_ticks()

        if pygame.time.get_ticks() - ai_timer >= AI_DELAY:
            try:
                action = minimax_agent.choose_action(state) if player == 1 else fuzzy_agent.decide_action(state, 2)

                if action is None:
                    moves = state.get_moves(player)
                    if moves:
                        action = ("move", moves[0])
                    else:
                        print(f"{agent_name} has no moves! Switching turn.")
                        player = 3 - player
                        ai_timer = 0
                        continue

                action_type, payload = action
                if action_type == "move":
                    start_pos = state.p1 if player == 1 else state.p2
                    animate_move(
                        board,
                        state,
                        player,
                        start_pos,
                        payload,
                        f"{agent_name} is thinking...",
                        can_block,
                        must_move,
                        role_items,
                        f"{agent_name.upper()} TURN",
                        agent_color,
                        (AI_BLUE, AI_RED),
                        mode="move",
                        frames=28,
                    )
                    state.apply_move(player, payload)
                    print(f"{agent_name} moved to {payload}")
                elif action_type == "block":
                    c1, c2 = payload
                    animate_block(
                        board,
                        state,
                        [c1, c2],
                        f"{agent_name} is thinking...",
                        can_block,
                        must_move,
                        role_items,
                        f"{agent_name.upper()} TURN",
                        agent_color,
                        (AI_BLUE, AI_RED),
                        mode="block2",
                        selected=[c1, c2],
                        duration_ms=1500,
                        delay_ms=500,
                        block_anim_origin=_block_origin_for_player(player),
                    )
                    if state.apply_block(player, c1, c2):
                        print(f"{agent_name} blocked {c1}, {c2}")

                player = 3 - player

            except Exception as e:
                print(f"Error in {agent_name}: {e}")
                player = 3 - player

            ai_timer = 0

        clock.tick(60)


def main():
    while True:
        mode_idx, fire_count = start_flow()
        
        if mode_idx == 0:
            winner = main_game_2player(fire_count)
            mode_name = "Two Player"
        elif mode_idx == 1:
            winner = main_game_player_vs_minimax(fire_count)
            mode_name = "Player vs Minimax AI"
            if winner == 2:
                print("\n" + "="*60)
                print("🏆 YOU WON! Your token reached the goal! 🏆")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("🏆 MINIMAX AI WON! Better luck next time! 🏆")
                print("="*60)
        elif mode_idx == 2:
            winner = main_game_player_vs_fuzzy(fire_count)
            mode_name = "Player vs Fuzzy AI"
            if winner == 2:
                print("\n" + "="*60)
                print("🏆 YOU WON! Your token reached the goal! 🏆")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("🏆 FUZZY AI WON! Better luck next time! 🏆")
                print("="*60)
        elif mode_idx == 3:
            winner = main_game_minimax_vs_fuzzy(fire_count)
            mode_name = "Minimax AI vs Fuzzy AI"
            if winner == 1:
                print("\n" + "="*60)
                print("🏆 MINIMAX AI WINS THE MATCH! 🏆")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("🏆 FUZZY AI WINS THE MATCH! 🏆")
                print("="*60)
        else:
            continue
        
        should_restart = show_win_screen(winner, mode_name)
        if not should_restart:
            break
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()