# main.py

import pygame
import sys
import random

from game.board import Board
from game.rules import GameState


WIDTH, HEIGHT = 630, 700

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Knight Invasion")

title_font = pygame.font.SysFont("arialblack", 60)
btn_font = pygame.font.SysFont("arial", 30)


# ---------------------------
# START SCREEN
# ---------------------------

def choose_fire_pairs(screen):
    easy = pygame.Rect(215, 250, 200, 60)
    med = pygame.Rect(215, 330, 200, 60)
    hard = pygame.Rect(215, 410, 200, 60)

    while True:
        screen.fill((245, 245, 245))

        title = title_font.render("Knight Invasion", True, (0, 0, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))

        mouse = pygame.mouse.get_pos()

        for btn, text in [(easy, "Easy"), (med, "Medium"), (hard, "Hard")]:
            color = (120, 180, 255) if btn.collidepoint(mouse) else (70, 120, 255)
            pygame.draw.rect(screen, color, btn, border_radius=10)

            label = btn_font.render(text, True, (255, 255, 255))
            screen.blit(label, (
                btn.x + btn.width//2 - label.get_width()//2,
                btn.y + btn.height//2 - label.get_height()//2
            ))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy.collidepoint(mouse):
                    print("Easy selected")
                    return random.choice([3, 4, 5])
                if med.collidepoint(mouse):
                    print("Medium selected")
                    return random.choice([8, 9, 10, 11])
                if hard.collidepoint(mouse):
                    print("Hard selected")
                    return random.choice([14, 15, 16, 17])


# ---------------------------
# MAIN GAME
# ---------------------------

def show_cells(cells):
    return [(r+1, c+1) for r, c in cells]


def main():
    state = GameState(choose_fire_pairs(screen))
    board = Board(screen)

    player = 1
    mode = "choose"

    selected = None
    highlights = []

    print("\nGame Started!\n")

    while True:

        print(f"\nPlayer {player} turn")

        if state.must_move(player):
            print("MUST MOVE:", show_cells(state.get_moves(player)))

        elif state.block_possible():
            print("Moves:", show_cells(state.get_moves(player)))
            print("Block available")

        else:
            print("No block possible → must move")

        info = f"Player {player}"

        board.draw(state, mode, highlights, selected, info)

        winner = state.check_winner()
        if winner:
            print("Winner:", winner)
            pygame.time.wait(3000)
            break

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:

                pos = pygame.mouse.get_pos()

                # button click
                btn = board.get_button(pos)

                if btn == "move":
                    mode = "move"
                    highlights = state.get_moves(player)

                elif btn == "block":
                    if not state.must_move(player) and state.block_possible():
                        mode = "block1"
                        highlights = [
                            (r, c)
                            for r in range(9)
                            for c in range(9)
                            if (r, c) not in state.blocks
                            and (r, c) not in state.fires
                            and (r, c) != state.p1
                            and (r, c) != state.p2
                        ]

                # grid click
                cell = board.get_cell(pos)

                if mode == "move":
                    if cell in highlights:
                        state.apply_move(player, cell)
                        player = 3 - player
                        mode = "choose"
                        highlights = []

                elif mode == "block1":
                    if cell in highlights:
                        selected = cell
                        mode = "block2"

                        highlights = [
                            (r2, c2)
                            for r2 in range(9)
                            for c2 in range(9)
                            if (r2, c2) != selected
                            and state.can_block(player, selected, (r2, c2))
                        ]

                elif mode == "block2":
                    if cell in highlights:
                        state.apply_block(player, selected, cell)
                        player = 3 - player
                        mode = "choose"
                        selected = None
                        highlights = []

        pygame.time.delay(40)


if __name__ == "__main__":
    main()