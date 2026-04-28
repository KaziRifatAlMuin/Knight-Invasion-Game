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
        ("2 Player", "Play local hot-seat duel"),
        ("Player vs Fuzzy Agent", "Blue (You) vs Red (Fuzzy AI)"),
        ("Player vs Minimax Agent", "Blue (You) vs Red (Minimax AI)"),
        ("Minimax vs Fuzzy Agent", "Blue (Minimax) vs Red (Fuzzy AI)"),
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

    if "Fuzzy" in mode_name:
        if winner == 1:
            winner_name = "Minimax AI (Blue)"
            winner_color = (0, 229, 255)
        else:
            winner_name = "Fuzzy AI (Red)"
            winner_color = (255, 62, 163)
    elif "Minimax" in mode_name:
        if winner == 1:
            winner_name = "Minimax AI (Blue)"
            winner_color = (0, 229, 255)
        else:
            winner_name = "Minimax AI (Red)"
            winner_color = (255, 62, 163)
    elif "Minimax vs Fuzzy" in mode_name:
        if winner == 1:
            winner_name = "Minimax AI (Blue)"
            winner_color = (0, 229, 255)
        else:
            winner_name = "Fuzzy AI (Red)"
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
    while True:
        mode_idx = show_mode_menu()
        fire_count = choose_difficulty_fire_count()
        return mode_idx, fire_count


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

        role_items = [
            ((0, 102, 255), "Blue Knight: Player 1"),
            ((220, 20, 60), "Red Knight: Player 2"),
        ]
        board.draw(
            state,
            mode,
            highlights,
            selected,
            f"Player {player} | {message}",
            can_block,
            must_move,
            role_items=role_items,
            focus_text="LOCAL 2-PLAYER MODE",
            focus_color=(52, 247, 255),
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
    """Player vs Fuzzy Agent mode"""
    state = GameState(fire_count)
    board = Board(screen)
    fuzzy_agent = FuzzyAgent()
    
    player = 1
    mode = "choose"
    selected = None
    highlights = []
    message = "Your turn! Choose MOVE or BLOCK"
    ai_timer = 0
    AI_DELAY = 800
    
    while True:
        winner = state.check_winner()
        if winner:
            return winner
        
        must_move = state.must_move(player)
        can_block = state.block_possible()
        
        if player == 2:
            role_items = [
                ((0, 102, 255), "Blue Knight: YOU (Human)"),
                ((220, 20, 60), "Red Knight: Fuzzy AI"),
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
                focus_color=(220, 20, 60),
            )
            pygame.display.flip()
            
            if ai_timer == 0:
                ai_timer = pygame.time.get_ticks()
            
            if pygame.time.get_ticks() - ai_timer >= AI_DELAY:
                action = fuzzy_agent.decide_action(state, 2)
                
                if action and action[0] == 'move':
                    move_pos = action[1]
                    state.apply_move(2, move_pos)
                    print(f"🤖 Fuzzy AI moved to {move_pos}")
                    
                elif action and action[0] == 'block':
                    _, (c1, c2) = action
                    if state.apply_block(2, c1, c2):
                        print(f"🤖 Fuzzy AI blocked {c1}, {c2}")
                
                player = 1
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
                ((0, 102, 255), "Blue Knight: YOU (Human)"),
                ((220, 20, 60), "Red Knight: Fuzzy AI"),
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
                focus_color=(0, 102, 255),
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
                    highlights = state.get_moves(1)
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
                        highlights = state.get_first_block_candidates(1)
                        message = "Pick first block cell"
                    continue
                
                cell = board.get_cell(pos)
                if cell is None:
                    continue
                
                if mode == "move":
                    if cell in highlights:
                        state.apply_move(1, cell)
                        player = 2
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
                        highlights = state.get_second_block_candidates(1, selected)
                        if highlights:
                            message = "Pick second block cell"
                        else:
                            mode = "block1"
                            selected = None
                            highlights = state.get_first_block_candidates(1)
                            message = "That first choice has no pair; pick another"
                    continue
                
                if mode == "block2":
                    if cell in highlights:
                        if state.apply_block(1, selected, cell):
                            player = 2
                            mode = "choose"
                            selected = None
                            highlights = []
                            message = "Blocks placed! AI is thinking..."
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


def main_game_player_vs_minimax(fire_count):
    """Player vs Minimax Agent mode"""
    state = GameState(fire_count)
    board = Board(screen)
    minimax_agent = MinimaxAgent(player=2, depth=6, max_block_first=8, max_block_second=5, time_limit=0.9)
    
    player = 1
    mode = "choose"
    selected = None
    highlights = []
    message = "Your turn! Choose MOVE or BLOCK"
    ai_timer = 0
    AI_DELAY = 800
    
    while True:
        winner = state.check_winner()
        if winner:
            return winner
        
        must_move = state.must_move(player)
        can_block = state.block_possible()
        
        if player == 2:
            role_items = [
                ((0, 102, 255), "Blue Knight: YOU (Human)"),
                ((220, 20, 60), "Red Knight: Minimax AI"),
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
                focus_color=(220, 20, 60),
            )
            pygame.display.flip()
            
            if ai_timer == 0:
                ai_timer = pygame.time.get_ticks()
            
            if pygame.time.get_ticks() - ai_timer >= AI_DELAY:
                action = minimax_agent.choose_action(state)
                
                if action and action[0] == 'move':
                    move_pos = action[1]
                    state.apply_move(2, move_pos)
                    print(f"🤖 Minimax AI moved to {move_pos}")
                    
                elif action and action[0] == 'block':
                    c1, c2 = action[1]
                    if state.apply_block(2, c1, c2):
                        print(f"🤖 Minimax AI blocked {c1}, {c2}")
                
                player = 1
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
                ((0, 102, 255), "Blue Knight: YOU (Human)"),
                ((220, 20, 60), "Red Knight: Minimax AI"),
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
                focus_color=(0, 102, 255),
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
                    highlights = state.get_moves(1)
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
                        highlights = state.get_first_block_candidates(1)
                        message = "Pick first block cell"
                    continue
                
                cell = board.get_cell(pos)
                if cell is None:
                    continue
                
                if mode == "move":
                    if cell in highlights:
                        state.apply_move(1, cell)
                        player = 2
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
                        highlights = state.get_second_block_candidates(1, selected)
                        if highlights:
                            message = "Pick second block cell"
                        else:
                            mode = "block1"
                            selected = None
                            highlights = state.get_first_block_candidates(1)
                            message = "That first choice has no pair; pick another"
                    continue
                
                if mode == "block2":
                    if cell in highlights:
                        if state.apply_block(1, selected, cell):
                            player = 2
                            mode = "choose"
                            selected = None
                            highlights = []
                            message = "Blocks placed! AI is thinking..."
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


def main_game_minimax_vs_fuzzy(fire_count):
    """Minimax vs Fuzzy Agent mode (AI vs AI)"""
    state = GameState(fire_count)
    board = Board(screen)
    minimax_agent = MinimaxAgent(player=1, depth=6, max_block_first=8, max_block_second=5, time_limit=0.9)
    fuzzy_agent = FuzzyAgent()
    
    player = 1
    ai_timer = 0
    AI_DELAY = 800
    
    game_winner = None
    
    while game_winner is None:
        winner = state.check_winner()
        if winner:
            game_winner = winner
            break
        
        must_move = state.must_move(player)
        can_block = state.block_possible()
        
        if player == 1:
            agent_name = "Minimax AI (Blue)"
            agent_color = (0, 102, 255)
        else:
            agent_name = "Fuzzy AI (Red)"
            agent_color = (220, 20, 60)
        
        role_items = [
            ((0, 102, 255), "Blue Knight: Minimax AI"),
            ((220, 20, 60), "Red Knight: Fuzzy AI"),
        ]
        
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
        )
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        
        if ai_timer == 0:
            ai_timer = pygame.time.get_ticks()
        
        if pygame.time.get_ticks() - ai_timer >= AI_DELAY:
            try:
                if player == 1:
                    action = minimax_agent.choose_action(state)
                else:
                    action = fuzzy_agent.decide_action(state, 2)
                
                if action is None:
                    moves = state.get_moves(player)
                    if moves:
                        action = ("move", moves[0])
                    else:
                        print(f"{agent_name} has no moves! Switching turn.")
                        player = 3 - player
                        ai_timer = 0
                        continue
                
                if action is not None:
                    action_type, payload = action
                    if action_type == "move":
                        state.apply_move(player, payload)
                        print(f"{agent_name} moved to {payload}")
                    elif action_type == "block":
                        c1, c2 = payload
                        state.apply_block(player, c1, c2)
                        print(f"{agent_name} blocked {c1}, {c2}")
                
                player = 3 - player
                
            except Exception as e:
                print(f"Error in {agent_name}: {e}")
                player = 3 - player
            
            ai_timer = 0
        
        clock.tick(60)
    
    return game_winner


def main():
    while True:
        mode_idx, fire_count = start_flow()
        
        if mode_idx == 0:
            winner = main_game_2player(fire_count)
            mode_name = "2 Player"
        elif mode_idx == 1:
            winner = main_game_player_vs_fuzzy(fire_count)
            mode_name = "Player vs Fuzzy"
            if winner == 1:
                print("\n" + "="*60)
                print("🏆 YOU WON! Blue Knight reached the goal! 🏆")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("🏆 FUZZY AI WON! Better luck next time! 🏆")
                print("="*60)
        elif mode_idx == 2:
            winner = main_game_player_vs_minimax(fire_count)
            mode_name = "Player vs Minimax"
            if winner == 1:
                print("\n" + "="*60)
                print("🏆 YOU WON! Blue Knight reached the goal! 🏆")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("🏆 MINIMAX AI WON! Better luck next time! 🏆")
                print("="*60)
        elif mode_idx == 3:
            winner = main_game_minimax_vs_fuzzy(fire_count)
            mode_name = "Minimax vs Fuzzy"
            if winner == 1:
                print("\n" + "="*60)
                print("🏆 MINIMAX AI (BLUE) WINS THE MATCH! 🏆")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("🏆 FUZZY AI (RED) WINS THE MATCH! 🏆")
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