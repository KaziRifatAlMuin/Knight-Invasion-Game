# main.py

import random
import sys

import pygame

from game.board import Board, HEIGHT, WIDTH
from game.rules import GameState
from agents.fuzzy_agent import FuzzyAgent

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
        ("Player vs Fuzzy Agent", "Blue Knight vs Fuzzy AI"),
        ("Player vs Minimax Agent", "Coming soon"),
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


def show_win_screen(winner, is_vs_ai=False, ai_won=False):
    restart_btn = pygame.Rect(WIDTH // 2 - 200, HEIGHT - 150, 180, 58)
    quit_btn = pygame.Rect(WIDTH // 2 + 20, HEIGHT - 150, 180, 58)

    if is_vs_ai:
        if winner == 1:
            winner_name = "Blue Knight (You)"
            winner_color = (0, 229, 255)
        else:
            winner_name = "Fuzzy AI"
            winner_color = (255, 62, 163)
    else:
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
        if mode_idx == 0:
            return ("2player", choose_difficulty_fire_count())
        elif mode_idx == 1:
            return ("player_vs_fuzzy", choose_difficulty_fire_count())
        else:
            # For now, show coming soon for other modes
            show_coming_soon(mode_labels[mode_idx])
            continue


def show_coming_soon(mode_name):
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


def main_game_2player(fire_count):
    """Original 2-player mode"""
    state = GameState(fire_count)
    board = Board(screen)

    player = 1
    mode = "choose"
    selected = None
    highlights = []
    message = "Choose MOVE or BLOCK"

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

        info = f"Player {player} turn | {message}"
        board.draw(state, mode, highlights, selected, info, can_block, must_move)

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


def main_game_player_vs_fuzzy(fire_count):
    """
    Player vs Fuzzy Agent mode
    Player controls Blue Knight (Player 1), Fuzzy AI controls Red Knight (Player 2)
    """
    state = GameState(fire_count)
    board = Board(screen)
    fuzzy_agent = FuzzyAgent()  # AI controls Red (Player 2)
    
    is_ai_turn = False
    mode = "choose"
    selected = None
    highlights = []
    message = "Your turn! Choose MOVE or BLOCK"
    
    # Track AI decision delay
    ai_timer = 0
    AI_DELAY = 800  # milliseconds
    
    while True:
        winner = state.check_winner()
        if winner:
            # Winner is 1 (Blue/Player) or 2 (Red/AI)
            return winner
        
        current_player = 2 if is_ai_turn else 1
        
        # AI TURN
        if is_ai_turn:
            # Update message
            board.draw(state, mode, highlights, selected, 
                      f"AI (Fuzzy) is thinking... | {message}", 
                      state.block_possible(), state.must_move(2))
            pygame.display.flip()
            
            # Add delay for AI move (so player can see)
            if ai_timer == 0:
                ai_timer = pygame.time.get_ticks()
            
            if pygame.time.get_ticks() - ai_timer >= AI_DELAY:
                # Get AI decision from fuzzy agent
                action = fuzzy_agent.decide_action(state, 2)
                
                if action and action[0] == 'move':
                    move_pos = action[1]
                    # Convert from (row, col) format
                    state.apply_move(2, move_pos)
                    message = f"AI moved to ({move_pos[0]+1}, {move_pos[1]+1})"
                    print(f"🤖 AI moved to {move_pos}")
                    
                elif action and action[0] == 'block':
                    _, c1, c2 = action
                    if state.apply_block(2, c1, c2):
                        message = f"AI blocked cells ({c1[0]+1},{c1[1]+1}) and ({c2[0]+1},{c2[1]+1})"
                        print(f"🤖 AI blocked {c1}, {c2}")
                    else:
                        message = "AI attempted invalid block"
                
                # Switch turn
                is_ai_turn = False
                mode = "choose"
                selected = None
                highlights = []
                ai_timer = 0
                
                # Check win after AI move
                winner = state.check_winner()
                if winner:
                    continue
            else:
                # Still waiting for AI delay
                clock.tick(60)
                continue
        
        # PLAYER TURN
        must_move = state.must_move(1)
        can_block = state.block_possible()
        
        if must_move:
            message = "Adjacent to fire: you must move"
        elif mode == "choose":
            message = "Your turn! Choose MOVE or BLOCK"
        
        info = f"Blue Knight (YOU) | {message}"
        board.draw(state, mode, highlights, selected, info, can_block, must_move)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                btn = board.get_button(pos)
                
                if btn == "move":
                    if not is_ai_turn:
                        mode = "move"
                        selected = None
                        highlights = state.get_moves(1)
                        message = "Select a highlighted destination"
                    continue
                
                if btn == "block":
                    if not is_ai_turn:
                        if must_move:
                            message = "Blocking disabled: you are adjacent to fire"
                        elif not can_block:
                            message = "Blocking disabled: no valid two-cell block"
                        else:
                            mode = "block1"
                            selected = None
                            highlights = state.get_first_block_candidates(1)
                            message = "Pick first block cell"
                    continue
                
                cell = board.get_cell(pos)
                if cell is None:
                    continue
                
                # Handle move selection
                if mode == "move" and not is_ai_turn:
                    if cell in highlights:
                        state.apply_move(1, cell)
                        is_ai_turn = True
                        mode = "choose"
                        selected = None
                        highlights = []
                        message = "AI is thinking..."
                        print(f"👤 Player moved to {cell}")
                    continue
                
                # Handle block selection
                if mode == "block1" and not is_ai_turn:
                    if cell in highlights:
                        selected = cell
                        mode = "block2"
                        highlights = state.get_second_block_candidates(1, selected)
                        if highlights:
                            message = "Pick second block cell"
                        else:
                            mode = "block1"
                            selected = None
                            highlights = state.get_first_block_candidates(1)
                            message = "That first choice has no pair; pick another"
                    continue
                
                if mode == "block2" and not is_ai_turn:
                    if cell in highlights:
                        if state.apply_block(1, selected, cell):
                            is_ai_turn = True
                            mode = "choose"
                            selected = None
                            highlights = []
                            message = f"Blocks placed! AI is thinking..."
                            print(f"👤 Player blocked {selected} and {cell}")
                        else:
                            mode = "block1"
                            selected = None
                            highlights = state.get_first_block_candidates(1)
                            message = "Invalid pair; choose again"
                    elif cell == selected:
                        mode = "block1"
                        selected = None
                        highlights = state.get_first_block_candidates(1)
                        message = "First block unselected"
        
        clock.tick(60)


def main():
    while True:
        game_mode, fire_count = start_flow()
        
        if game_mode == "2player":
            winner = main_game_2player(fire_count)
            should_restart = show_win_screen(winner, is_vs_ai=False)
        elif game_mode == "player_vs_fuzzy":
            winner = main_game_player_vs_fuzzy(fire_count)
            should_restart = show_win_screen(winner, is_vs_ai=True, ai_won=(winner == 2))
        else:
            continue
        
        if not should_restart:
            break
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()