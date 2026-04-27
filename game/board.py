# game/board.py

import pygame

CELL_SIZE = 70
GRID_SIZE = 9

WHITE = (245, 245, 245)
BLACK = (40, 40, 40)
BLUE = (70, 120, 255)
RED = (230, 80, 80)
GRAY = (140, 140, 140)

MOVE_COLOR = (100, 220, 100)
BLOCK_COLOR = (120, 120, 255)
SELECT_COLOR = (255, 255, 0)


class Board:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 24)

        # buttons
        self.move_btn = pygame.Rect(50, 640, 120, 40)
        self.block_btn = pygame.Rect(200, 640, 120, 40)

    def draw(self, state, mode, highlights, selected, info):
        self.screen.fill(WHITE)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)

                pygame.draw.rect(self.screen, WHITE, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 1)

                # fire
                if (r, c) in state.fires:
                    pygame.draw.circle(self.screen, (255, 120, 0), rect.center, 20)
                    pygame.draw.circle(self.screen, (255, 200, 0), rect.center, 10)

                # blocks
                if (r, c) in state.blocks:
                    pygame.draw.rect(self.screen, GRAY, rect)

                # highlights
                if highlights and (r, c) in highlights:
                    color = MOVE_COLOR if mode.startswith("move") else BLOCK_COLOR
                    pygame.draw.rect(self.screen, color, rect, 4)

                if selected == (r, c):
                    pygame.draw.rect(self.screen, SELECT_COLOR, rect, 5)

        # players
        br, bc = state.p1
        rr, rc = state.p2

        pygame.draw.circle(self.screen, BLUE, (bc*CELL_SIZE+35, br*CELL_SIZE+35), 22)
        pygame.draw.circle(self.screen, RED, (rc*CELL_SIZE+35, rr*CELL_SIZE+35), 22)

        self.screen.blit(self.font.render("B", True, WHITE), (bc*CELL_SIZE+25, br*CELL_SIZE+20))
        self.screen.blit(self.font.render("R", True, WHITE), (rc*CELL_SIZE+25, rr*CELL_SIZE+20))

        # info
        self.screen.blit(self.font.render(info, True, BLACK), (10, 5))

        # buttons
        pygame.draw.rect(self.screen, MOVE_COLOR, self.move_btn, border_radius=6)
        pygame.draw.rect(self.screen, BLOCK_COLOR, self.block_btn, border_radius=6)

        self.screen.blit(self.font.render("MOVE", True, BLACK), (65, 650))
        self.screen.blit(self.font.render("BLOCK", True, BLACK), (215, 650))

        pygame.display.flip()

    def get_cell(self, pos):
        x, y = pos
        return (y // CELL_SIZE, x // CELL_SIZE)

    def get_button(self, pos):
        if self.move_btn.collidepoint(pos):
            return "move"
        if self.block_btn.collidepoint(pos):
            return "block"
        return None