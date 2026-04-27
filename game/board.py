# game/board.py

import pygame

GRID_SIZE = 9
CELL_SIZE = 64
BOARD_PIXEL = GRID_SIZE * CELL_SIZE
MARGIN_X = 28
MARGIN_TOP = 98
SIDEBAR_GAP = 26
SIDEBAR_WIDTH = 292
SIDE_PADDING = 24

WIDTH = MARGIN_X + BOARD_PIXEL + SIDEBAR_GAP + SIDEBAR_WIDTH + SIDE_PADDING
HEIGHT = 780

BOARD_LEFT = MARGIN_X
BOARD_RIGHT = BOARD_LEFT + BOARD_PIXEL
SIDEBAR_X = BOARD_RIGHT + SIDEBAR_GAP
SIDEBAR_Y = MARGIN_TOP - 8
SIDEBAR_H = 620

BG_TOP = (6, 10, 24)
BG_BOTTOM = (2, 4, 12)
CELL_LIGHT = (18, 24, 44)
CELL_DARK = (12, 17, 34)
GRID_LINE = (38, 56, 92)
TEXT_MAIN = (245, 250, 255)
TEXT_MUTED = (147, 174, 211)

BLUE = (0, 102, 255)
RED = (220, 20, 60)
BLOCK = (77, 88, 122)
FIRE_ORANGE = (255, 120, 40)
FIRE_YELLOW = (255, 232, 115)

MOVE_COLOR = (0, 255, 163)
BLOCK_COLOR = (138, 92, 255)
SELECT_COLOR = (255, 245, 126)
NEON_CYAN = (52, 247, 255)
NEON_PINK = (255, 62, 163)


class Board:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont("bahnschrift", 34, bold=True)
        self.info_font = pygame.font.SysFont("bahnschrift", 20, bold=True)
        self.small_font = pygame.font.SysFont("bahnschrift", 16)

        self.move_btn = pygame.Rect(SIDEBAR_X + 16, SIDEBAR_Y + 360, SIDEBAR_WIDTH - 32, 54)
        self.block_btn = pygame.Rect(SIDEBAR_X + 16, SIDEBAR_Y + 428, SIDEBAR_WIDTH - 32, 54)

    @staticmethod
    def _draw_vertical_gradient(surface, top_color, bottom_color):
        width, height = surface.get_size()
        for y in range(height):
            t = y / max(1, height - 1)
            color = (
                int(top_color[0] + (bottom_color[0] - top_color[0]) * t),
                int(top_color[1] + (bottom_color[1] - top_color[1]) * t),
                int(top_color[2] + (bottom_color[2] - top_color[2]) * t),
            )
            pygame.draw.line(surface, color, (0, y), (width, y))

    @staticmethod
    def _cell_rect(r, c):
        return pygame.Rect(
            MARGIN_X + c * CELL_SIZE,
            MARGIN_TOP + r * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        )

    def _draw_board_background(self):
        self._draw_vertical_gradient(self.screen, BG_TOP, BG_BOTTOM)

        title = self.title_font.render("KNIGHT INVASION", True, TEXT_MAIN)
        subtitle = self.small_font.render("Duel Arena", True, TEXT_MUTED)

        self.screen.blit(title, (MARGIN_X, 22))
        self.screen.blit(subtitle, (MARGIN_X + 4, 60))

        pygame.draw.line(self.screen, NEON_CYAN, (MARGIN_X, 80), (WIDTH - MARGIN_X, 80), 2)
        pygame.draw.line(self.screen, NEON_PINK, (MARGIN_X, 83), (WIDTH - MARGIN_X, 83), 1)

        board_shadow = pygame.Rect(MARGIN_X - 8, MARGIN_TOP - 8, BOARD_PIXEL + 16, BOARD_PIXEL + 16)
        pygame.draw.rect(self.screen, (4, 7, 12), board_shadow, border_radius=18)
        pygame.draw.rect(self.screen, (29, 44, 78), board_shadow, 2, border_radius=18)

        sidebar = pygame.Rect(SIDEBAR_X, SIDEBAR_Y, SIDEBAR_WIDTH, SIDEBAR_H)
        pygame.draw.rect(self.screen, (8, 13, 26), sidebar, border_radius=18)
        pygame.draw.rect(self.screen, NEON_CYAN, sidebar, 1, border_radius=18)
        pygame.draw.rect(self.screen, NEON_PINK, sidebar.inflate(-4, -4), 1, border_radius=16)
        pygame.draw.rect(self.screen, (29, 44, 78), sidebar, 2, border_radius=18)

        sidebar_title = self.small_font.render("CONTROL PANEL", True, TEXT_MUTED)
        self.screen.blit(sidebar_title, (SIDEBAR_X + 18, SIDEBAR_Y + 16))

    def _draw_goal_markers(self):
        top_y = MARGIN_TOP + 5
        bottom_y = MARGIN_TOP + BOARD_PIXEL - 10

        for c in range(GRID_SIZE):
            glow_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

            pygame.draw.circle(glow_surface, (*BLUE, 18), (CELL_SIZE // 2, CELL_SIZE // 2), 20)
            pygame.draw.circle(glow_surface, (*RED, 18), (CELL_SIZE // 2, CELL_SIZE // 2), 20)

            self.screen.blit(glow_surface, (MARGIN_X + c * CELL_SIZE, top_y - 6))
            self.screen.blit(glow_surface, (MARGIN_X + c * CELL_SIZE, bottom_y - CELL_SIZE + 6))

        # subtle stakes at each side's target row
        for x, color, y in [
            (MARGIN_X - 6, RED, MARGIN_TOP - 2),
            (MARGIN_X + BOARD_PIXEL + 2, RED, MARGIN_TOP - 2),
            (MARGIN_X - 6, BLUE, MARGIN_TOP + BOARD_PIXEL - 8),
            (MARGIN_X + BOARD_PIXEL + 2, BLUE, MARGIN_TOP + BOARD_PIXEL - 8),
        ]:
            stake_rect = pygame.Rect(x, y, 4, 26)
            pygame.draw.rect(self.screen, (*color,), stake_rect, border_radius=2)
            pygame.draw.rect(self.screen, (8, 13, 26), stake_rect.inflate(-1, -18), 1, border_radius=1)

    def _draw_fire(self, rect, t):
        center = rect.center
        pulse = int(2 * (1 + (t % 1200) / 1200))
        pygame.draw.circle(self.screen, (120, 40, 10), center, 23 + pulse)
        pygame.draw.circle(self.screen, FIRE_ORANGE, center, 19 + pulse)
        pygame.draw.circle(self.screen, FIRE_YELLOW, center, 10 + pulse // 2)
        pygame.draw.circle(self.screen, (255, 255, 255), center, 4)

    def _draw_token(self, pos, color, label):
        r, c = pos
        center = (
            MARGIN_X + c * CELL_SIZE + CELL_SIZE // 2,
            MARGIN_TOP + r * CELL_SIZE + CELL_SIZE // 2,
        )
        shadow = (center[0] + 3, center[1] + 4)
        pygame.draw.circle(self.screen, (0, 0, 0), shadow, 27)
        pygame.draw.circle(self.screen, (8, 13, 26), center, 27)
        pygame.draw.circle(self.screen, color, center, 24)
        pygame.draw.circle(self.screen, (255, 255, 255), center, 24, 2)

        accent = (80, 150, 255) if color == BLUE else (255, 110, 140)
        pygame.draw.circle(self.screen, accent, (center[0] - 8, center[1] - 8), 5)
        pygame.draw.circle(self.screen, accent, (center[0] + 8, center[1] + 9), 3)

        pygame.draw.arc(self.screen, (255, 255, 255), pygame.Rect(center[0] - 18, center[1] - 18, 36, 36), 0.6, 2.0, 2)

        text = self.info_font.render(label, True, (255, 255, 255))
        self.screen.blit(text, (center[0] - text.get_width() // 2, center[1] - text.get_height() // 2 - 1))

    def draw(self, state, mode, highlights, selected, info, can_block, must_move):
        self._draw_board_background()
        self._draw_goal_markers()
        t = pygame.time.get_ticks()

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = self._cell_rect(r, c)
                base = CELL_LIGHT if (r + c) % 2 == 0 else CELL_DARK
                pygame.draw.rect(self.screen, base, rect, border_radius=5)
                pygame.draw.rect(self.screen, GRID_LINE, rect, 1, border_radius=5)

                if (r, c) in state.blocks:
                    inner = rect.inflate(-8, -8)
                    pygame.draw.rect(self.screen, (28, 36, 64), inner, border_radius=6)
                    pygame.draw.rect(self.screen, BLOCK, inner, 2, border_radius=6)

                if (r, c) in state.fires:
                    self._draw_fire(rect, t)

                if highlights and (r, c) in highlights:
                    color = MOVE_COLOR if mode.startswith("move") else BLOCK_COLOR
                    glow = rect.inflate(-8, -8)
                    pygame.draw.rect(self.screen, color, glow, 2, border_radius=8)
                    pygame.draw.rect(self.screen, color, rect.inflate(-18, -18), 1, border_radius=6)

                if selected == (r, c):
                    pygame.draw.rect(self.screen, SELECT_COLOR, rect.inflate(-6, -6), 4, border_radius=10)
                    pygame.draw.rect(self.screen, (255, 255, 255), rect.inflate(-2, -2), 1, border_radius=10)

        self._draw_token(state.p1, BLUE, "B")
        self._draw_token(state.p2, RED, "R")

        # Bottom command panel
        panel_rect = pygame.Rect(SIDEBAR_X + 12, SIDEBAR_Y + 44, SIDEBAR_WIDTH - 24, 290)
        pygame.draw.rect(self.screen, (10, 16, 30), panel_rect, border_radius=14)
        pygame.draw.rect(self.screen, NEON_CYAN, panel_rect, 1, border_radius=14)
        pygame.draw.rect(self.screen, NEON_PINK, panel_rect.inflate(-4, -4), 1, border_radius=12)

        turn_label, _, status = info.partition("|")
        turn_label = turn_label.strip()
        status = status.strip()

        info_text = self.info_font.render(turn_label, True, TEXT_MAIN)
        self.screen.blit(info_text, (panel_rect.x + 16, panel_rect.y + 10))

        status_lines = self._wrap_text(status, self.small_font, panel_rect.width - 32)
        if not status_lines:
            status_lines = [""]

        for idx, line in enumerate(status_lines[:2]):
            color = TEXT_MUTED if idx == 0 else (200, 214, 244)
            status_text = self.small_font.render(line, True, color)
            self.screen.blit(status_text, (panel_rect.x + 16, panel_rect.y + 40 + idx * 18))

        hint = "Select destination" if mode == "move" else "Pick two cells to block" if mode.startswith("block") else "Choose action"
        if must_move:
            hint = "Must move: adjacent to fire"
        elif not can_block:
            hint = "No valid two-cell block now"

        hint_text = self.small_font.render(hint, True, NEON_CYAN if not must_move else NEON_PINK)
        self.screen.blit(hint_text, (panel_rect.x + 16, panel_rect.y + 74))

        legend_y = panel_rect.y + 118
        legend_items = [
            (BLUE, "Blue Knight"),
            (RED, "Red Knight"),
        ]
        for i, (color, label) in enumerate(legend_items):
            yy = legend_y + i * 30
            pygame.draw.circle(self.screen, color, (panel_rect.x + 22, yy + 10), 8)
            text = self.small_font.render(label, True, TEXT_MAIN)
            self.screen.blit(text, (panel_rect.x + 40, yy + 1))

        rule_text = self.small_font.render("Move or block two cells", True, TEXT_MUTED)
        self.screen.blit(rule_text, (panel_rect.x + 16, panel_rect.bottom - 32))

        move_active = mode.startswith("move")
        block_active = mode.startswith("block")

        self._draw_button(self.move_btn, "MOVE", MOVE_COLOR, move_active, True)
        self._draw_button(self.block_btn, "BLOCK", BLOCK_COLOR, block_active, can_block and not must_move)

        pygame.display.flip()

    def _draw_button(self, rect, label, accent, active, enabled):
        fill = (17, 25, 46) if enabled else (12, 14, 22)
        border = accent if active else (72, 88, 126) if enabled else (54, 59, 74)
        text_color = TEXT_MAIN if enabled else (128, 132, 142)

        pygame.draw.rect(self.screen, fill, rect, border_radius=10)
        pygame.draw.rect(self.screen, border, rect, 2, border_radius=10)
        if enabled:
            pygame.draw.rect(self.screen, (255, 255, 255), rect.inflate(-6, -6), 1, border_radius=8)

        txt = self.info_font.render(label, True, text_color)
        self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

    @staticmethod
    def _wrap_text(text, font, max_width):
        words = text.split()
        if not words:
            return []

        lines = []
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word

        lines.append(current)
        return lines

    def get_cell(self, pos):
        x, y = pos
        if not (
            MARGIN_X <= x < MARGIN_X + BOARD_PIXEL
            and MARGIN_TOP <= y < MARGIN_TOP + BOARD_PIXEL
        ):
            return None

        col = (x - MARGIN_X) // CELL_SIZE
        row = (y - MARGIN_TOP) // CELL_SIZE
        return (row, col)

    def get_button(self, pos):
        if self.move_btn.collidepoint(pos):
            return "move"
        if self.block_btn.collidepoint(pos):
            return "block"
        return None
