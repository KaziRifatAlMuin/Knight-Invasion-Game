# main.py

import random
import sys

import pygame

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


def draw_neon_panel(rect, accent_a, accent_b):
    pygame.draw.rect(screen, (10, 16, 30), rect, border_radius=16)
    pygame.draw.rect(screen, accent_a, rect, 2, border_radius=16)
    pygame.draw.rect(screen, accent_b, rect.inflate(-4, -4), 1, border_radius=14)


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
        ("2 Player", "Play local hot-seat duel"),
        ("Player vs Fuzzy Agent", "Coming soon"),
        ("Player vs Minimax Agent", "Playable"),
        ("Minimax Agent vs Fuzzy Agent", "Coming soon"),
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


def show_coming_soon(mode_name):
    # make the back button larger and centered for easier clicking
    back_btn_w, back_btn_h = 340, 72
    back_btn = pygame.Rect(WIDTH // 2 - back_btn_w // 2, HEIGHT - 140, back_btn_w, back_btn_h)

    while True:
        draw_vertical_gradient(screen, BG_TOP, BG_BOTTOM)

        title = HEADER_FONT.render(mode_name, True, (245, 250, 255))
        msg = TEXT_FONT.render("COMING SOON", True, (255, 62, 163))
        hint = SMALL_FONT.render("This mode is planned but not playable yet.", True, (158, 181, 219))

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 210))
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 272))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 316))

        mouse = pygame.mouse.get_pos()
        draw_menu_button(back_btn, "Back to mode selection", "", back_btn.collidepoint(mouse))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and back_btn.collidepoint(event.pos):
                return

        clock.tick(60)


def choose_difficulty_fire_count():
    levels = [
        ("Easy", "8-14 fires", 8, 14),
        ("Medium", "16-22 fires", 16, 22),
        ("Hard", "24-30 fires", 24, 30),
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


def show_win_screen(winner):
    restart_btn = pygame.Rect(WIDTH // 2 - 200, HEIGHT - 150, 180, 58)
    quit_btn = pygame.Rect(WIDTH // 2 + 20, HEIGHT - 150, 180, 58)

    winner_name = "Blue Knight" if winner == 1 else "Red Knight"
    winner_color = (0, 229, 255) if winner == 1 else (255, 62, 163)

    while True:
        draw_vertical_gradient(screen, BG_TOP, BG_BOTTOM)

        title = TITLE_FONT.render("VICTORY", True, (245, 250, 255))
        text = HEADER_FONT.render(f"{winner_name} Wins!", True, winner_color)
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
    mode_labels = [
        "2 Player",
        "Player vs Fuzzy Agent",
        "Player vs Minimax Agent",
        "Minimax Agent vs Fuzzy Agent",
    ]

    while True:
        mode_idx = show_mode_menu()
        if mode_idx in (0, 2):
            return mode_idx, choose_difficulty_fire_count()
        show_coming_soon(mode_labels[mode_idx])


def main_game(fire_count, mode_idx):
    state = GameState(fire_count)
    board = Board(screen)
    minimax_agent = MinimaxAgent(player=2, depth=6, max_block_first=8, max_block_second=5, time_limit=0.9) if mode_idx == 2 else None

    player = 1
    mode = "choose"
    selected = None
    highlights = []
    message = "Choose MOVE or BLOCK"

    while True:
        winner = state.check_winner()
        if winner:
            return winner

        agent_turn = minimax_agent is not None and player == minimax_agent.player
        must_move = state.must_move(player)
        can_block = state.block_possible()

        if agent_turn:
            mode = "choose"
            selected = None
            highlights = []
            message = "Minimax Agent is choosing..."
        else:
            if must_move:
                message = "Adjacent to fire: you must move"
            elif mode == "choose":
                message = "Choose MOVE or BLOCK"

        if mode_idx == 2:
            role_items = [
                ((0, 102, 255), "Blue Knight: Human"),
                ((220, 20, 60), "Red Knight: Minimax Agent"),
            ]
            if agent_turn:
                focus_text = "MINIMAX AGENT TURN"
                focus_color = (220, 20, 60)
            else:
                focus_text = "YOUR TURN (HUMAN)"
                focus_color = (0, 102, 255)
        else:
            role_items = [
                ((0, 102, 255), "Blue Knight: Player 1"),
                ((220, 20, 60), "Red Knight: Player 2"),
            ]
            focus_text = "LOCAL 2-PLAYER MODE"
            focus_color = (52, 247, 255)

        info = f"Player {player} turn | {message}"
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
        )

        if agent_turn:
            action = minimax_agent.choose_action(state)
            if action is None:
                moves = state.get_moves(player)
                if moves:
                    action = ("move", moves[0])

            if action is not None:
                action_type, payload = action
                if action_type == "move":
                    state.apply_move(player, payload)
                    message = f"Minimax moved to ({payload[0] + 1}, {payload[1] + 1})"
                else:
                    c1, c2 = payload
                    state.apply_block(player, c1, c2)
                    message = (
                        f"Minimax blocked ({c1[0] + 1},{c1[1] + 1}) and ({c2[0] + 1},{c2[1] + 1})"
                    )

            player = 3 - player
            clock.tick(60)
            continue

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


def main():
    while True:
        mode_idx, fire_count = start_flow()
        winner = main_game(fire_count, mode_idx)
        should_restart = show_win_screen(winner)
        if not should_restart:
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
