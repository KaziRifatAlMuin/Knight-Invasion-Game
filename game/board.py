# game/board.py

import math

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

PLAYER_YELLOW = (255, 195, 30)

TARGET_TOP_TINT = (42, 95, 190)
TARGET_BOTTOM_TINT = (185, 40, 62)
BLOCK_NEUTRAL = (182, 188, 200)
BLOCK_STONE = (138, 118, 94)
BLOCK_STONE_SHADOW = (86, 70, 54)
BLOCK_STONE_HIGHLIGHT = (200, 178, 145)

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

    @staticmethod
    def _cell_center(pos):
        row, col = pos
        return (
            MARGIN_X + col * CELL_SIZE + CELL_SIZE // 2,
            MARGIN_TOP + row * CELL_SIZE + CELL_SIZE // 2,
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

    def _draw_goal_markers(self, t):
        top_y = MARGIN_TOP + 5
        bottom_y = MARGIN_TOP + BOARD_PIXEL - 10

        # Top row is target for Red (show bluish band at top), bottom row is target for Blue (show reddish band at bottom)
        for row, color, pulse_shift in [
            (0, BLUE, 0),
            (GRID_SIZE - 1, RED, 600),
        ]:
            row_rect = pygame.Rect(MARGIN_X, MARGIN_TOP + row * CELL_SIZE, BOARD_PIXEL, CELL_SIZE)
            overlay = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
            pulse = 0.5 + 0.5 * math.sin((t + pulse_shift) / 240)
            band_color = (*color, int(26 + 36 * pulse))
            glow_color = (*color, int(22 + 28 * pulse))
            pygame.draw.rect(overlay, band_color, overlay.get_rect(), border_radius=10)
            pygame.draw.rect(overlay, glow_color, overlay.get_rect(), 2, border_radius=10)
            self.screen.blit(overlay, row_rect.topleft)

            for c in range(GRID_SIZE):
                center = (
                    MARGIN_X + c * CELL_SIZE + CELL_SIZE // 2,
                    row_rect.centery,
                )
                radius = int(5 + 3 * pulse)
                pygame.draw.circle(self.screen, (*color, 0), center, radius)

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

        if color == BLUE:
            accent = (80, 150, 255)
        elif color == RED:
            accent = (255, 110, 140)
        elif color == PLAYER_YELLOW:
            accent = (255, 230, 120)
        else:
            accent = (150, 150, 150)
        pygame.draw.circle(self.screen, accent, (center[0] - 8, center[1] - 8), 5)
        pygame.draw.circle(self.screen, accent, (center[0] + 8, center[1] + 9), 3)

        pygame.draw.arc(self.screen, (255, 255, 255), pygame.Rect(center[0] - 18, center[1] - 18, 36, 36), 0.6, 2.0, 2)

        text = self.info_font.render(label, True, (255, 255, 255))
        self.screen.blit(text, (center[0] - text.get_width() // 2, center[1] - text.get_height() // 2 - 1))

    def _draw_motion_token(self, color, label, start_pos, end_pos, progress):
        start_x, start_y = self._cell_center(start_pos)
        end_x, end_y = self._cell_center(end_pos)
        x = int(start_x + (end_x - start_x) * progress)
        y = int(start_y + (end_y - start_y) * progress)
        offset = int(10 * (1 - abs(0.5 - progress) * 2))

        glow = pygame.Surface((96, 96), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*color, 60), (48, 48), 30 + offset)
        pygame.draw.circle(glow, (*color, 120), (48, 48), 22 + offset // 2)
        self.screen.blit(glow, (x - 48, y - 48))

        pygame.draw.circle(self.screen, (0, 0, 0), (x + 3, y + 4), 27)
        pygame.draw.circle(self.screen, (8, 13, 26), (x, y), 27)
        pygame.draw.circle(self.screen, color, (x, y), 24)
        pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 24, 2)

        if color == BLUE:
            accent = (80, 150, 255)
        elif color == RED:
            accent = (255, 110, 140)
        elif color == PLAYER_YELLOW:
            accent = (255, 230, 120)
        else:
            accent = (150, 150, 150)
        pygame.draw.circle(self.screen, accent, (x - 8, y - 8), 5)
        pygame.draw.circle(self.screen, accent, (x + 8, y + 9), 3)

        pygame.draw.arc(self.screen, (255, 255, 255), pygame.Rect(x - 18, y - 18, 36, 36), 0.6, 2.0, 2)

        text = self.info_font.render(label, True, (255, 255, 255))
        self.screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2 - 1))

    def draw(self, state, mode, highlights, selected, info, can_block, must_move, role_items=None, focus_text="", focus_color=None, active_color=None, block_anim_cells=None, block_anim_t=0.0, block_anim_origin="top", moving_player=None, moving_start=None, moving_end=None, moving_t=0.0, token_colors=None):
        self._draw_board_background()
        self._draw_goal_markers(pygame.time.get_ticks())
        t = pygame.time.get_ticks()
        deferred_bottom_anims = []

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = self._cell_rect(r, c)
                base = CELL_LIGHT if (r + c) % 2 == 0 else CELL_DARK
                if r == 0 or r == GRID_SIZE - 1:
                    row_color = None
                    if token_colors and isinstance(token_colors, (list, tuple)) and len(token_colors) >= 2:
                        row_color = token_colors[0] if r == 0 else token_colors[1]
                    else:
                        row_color = BLUE if r == 0 else RED

                    base = (
                        min(255, base[0] + row_color[0] // 5),
                        min(255, base[1] + row_color[1] // 5),
                        min(255, base[2] + row_color[2] // 5),
                    )
                pygame.draw.rect(self.screen, base, rect, border_radius=5)
                pygame.draw.rect(self.screen, GRID_LINE, rect, 1, border_radius=5)

                if (r, c) in state.blocks:
                    inner = rect.inflate(-8, -8)
                    pygame.draw.rect(self.screen, (28, 36, 64), inner, border_radius=6)
                    pygame.draw.rect(self.screen, BLOCK, inner, 2, border_radius=6)

                # animated block preview (before commit)
                if block_anim_cells and (r, c) in block_anim_cells:
                    prog = max(0.0, min(1.0, block_anim_t))
                    ease = 1 - (1 - prog) * (1 - prog)
                    inner = rect.inflate(-12, -12)
                    surf = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
                    alpha = int(225 * prog)
                    base_rect = surf.get_rect()
                    pygame.draw.rect(surf, (*BLOCK_STONE, alpha), base_rect, border_radius=7)
                    pygame.draw.rect(surf, (*BLOCK_STONE_SHADOW, alpha), base_rect, 2, border_radius=7)
                    top_strip = pygame.Rect(2, 2, base_rect.width - 4, max(4, base_rect.height // 4))
                    pygame.draw.rect(surf, (*BLOCK_STONE_HIGHLIGHT, int(120 + 60 * prog)), top_strip, border_radius=6)
                    pygame.draw.line(surf, (255, 255, 255, int(100 * prog)), (4, 5), (base_rect.width - 6, 5), 1)
                    border_alpha = int(180 * prog)
                    pygame.draw.rect(surf, (232, 216, 188, border_alpha), base_rect, 2, border_radius=7)
                    if block_anim_origin == "bottom":
                        start_y = MARGIN_TOP + BOARD_PIXEL + 10
                    else:
                        start_y = MARGIN_TOP - CELL_SIZE - 10
                    drop_y = int(start_y + (inner.y - start_y) * ease)
                    shadow = pygame.Surface((inner.width + 14, 14), pygame.SRCALPHA)
                    shadow_alpha = int(110 * (1 - prog) + 30)
                    pygame.draw.ellipse(shadow, (0, 0, 0, shadow_alpha), shadow.get_rect())
                    # If coming from bottom, defer drawing so it appears above tokens
                    if block_anim_origin == "bottom":
                        combo_w = inner.width + 14
                        combo_h = inner.height + 14
                        combo = pygame.Surface((combo_w, combo_h), pygame.SRCALPHA)
                        combo.blit(shadow, (0, inner.height - 2))
                        combo.blit(surf, (7, 0))
                        deferred_bottom_anims.append((combo, inner.x - 7, drop_y))
                    else:
                        self.screen.blit(shadow, (inner.x - 7, drop_y + inner.height - 2))
                        self.screen.blit(surf, (inner.x, drop_y))

                if (r, c) in state.fires:
                    self._draw_fire(rect, t)

                if highlights and (r, c) in highlights:
                    color = MOVE_COLOR if mode.startswith("move") else BLOCK_COLOR
                    glow = rect.inflate(-8, -8)
                    pulse = 0.5 + 0.5 * math.sin(t / 170 + (r + c))
                    fill = pygame.Surface((glow.width, glow.height), pygame.SRCALPHA)
                    pygame.draw.rect(fill, (*color, int(42 + 48 * pulse)), fill.get_rect(), border_radius=9)
                    pygame.draw.rect(fill, (*color, 255), fill.get_rect(), 2, border_radius=9)
                    self.screen.blit(fill, glow.topleft)
                    pygame.draw.circle(self.screen, (*color, 0), rect.center, int(8 + 4 * pulse))
                    pygame.draw.polygon(
                        self.screen,
                        color,
                        [
                            (rect.centerx, rect.centery - 10),
                            (rect.centerx - 8, rect.centery + 4),
                            (rect.centerx + 8, rect.centery + 4),
                        ],
                    )
                    pygame.draw.rect(self.screen, color, rect.inflate(-18, -18), 1, border_radius=6)

                # compute a stable selected color for block modes
                if mode.startswith("block"):
                    sel_color = None
                    if focus_color:
                        sel_color = focus_color
                    elif active_color:
                        sel_color = active_color
                    else:
                        sel_color = PLAYER_YELLOW
                else:
                    sel_color = SELECT_COLOR

                # support selected being either a single cell or a collection of cells
                selected_cells = None
                if selected is not None:
                    if isinstance(selected, tuple) and len(selected) == 2 and all(isinstance(v, int) for v in selected):
                        selected_cells = {selected}
                    else:
                        try:
                            selected_cells = set(selected)
                        except TypeError:
                            selected_cells = {selected}

                is_selected_cell = selected_cells is not None and (r, c) in selected_cells

                if is_selected_cell:
                    pulse = 0.5 + 0.5 * math.sin(t / 120)
                    outer = rect.inflate(-2, -2)
                    inner = rect.inflate(-10, -10)
                    fill = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
                    pygame.draw.rect(fill, (*sel_color, int(100 + 60 * pulse)), fill.get_rect(), border_radius=10)
                    pygame.draw.rect(fill, (*sel_color, 255), fill.get_rect(), 3, border_radius=10)
                    self.screen.blit(fill, inner.topleft)
                    pygame.draw.rect(self.screen, sel_color, outer, int(4 + 2 * pulse), border_radius=12)
                    pygame.draw.rect(self.screen, (255, 255, 255), inner, 1, border_radius=10)
                    corner = pygame.Rect(rect.right - 18, rect.y + 6, 12, 12)
                    pygame.draw.circle(self.screen, sel_color, corner.center, 6)
                    if mode.startswith("block"):
                        glow = rect.inflate(-18, -18)
                        glow_fill = pygame.Surface((glow.width, glow.height), pygame.SRCALPHA)
                        pygame.draw.rect(glow_fill, (*sel_color, int(70 + 40 * pulse)), glow_fill.get_rect(), border_radius=8)
                        pygame.draw.rect(glow_fill, (255, 255, 255, int(85 + 40 * pulse)), glow_fill.get_rect(), 2, border_radius=8)
                        self.screen.blit(glow_fill, glow.topleft)

                if mode.startswith("block") and is_selected_cell:
                    tint_color = sel_color
                    shade = pygame.Surface((rect.width - 8, rect.height - 8), pygame.SRCALPHA)
                    pygame.draw.rect(shade, (*tint_color, 110), shade.get_rect(), border_radius=8)
                    pygame.draw.rect(shade, (238, 242, 248, 160), shade.get_rect(), 2, border_radius=8)
                    self.screen.blit(shade, (rect.x + 4, rect.y + 4))

        moving_drawn = False
        # token color overrides: token_colors is a (p1_color, p2_color) tuple
        p1_color = BLUE
        p2_color = RED
        if token_colors and isinstance(token_colors, (list, tuple)) and len(token_colors) >= 2:
            p1_color, p2_color = token_colors[0], token_colors[1]

        if moving_player == 1 and moving_start and moving_end:
            self._draw_motion_token(p1_color, "P1", moving_start, moving_end, moving_t)
            moving_drawn = True
        if moving_player == 2 and moving_start and moving_end:
            self._draw_motion_token(p2_color, "P2", moving_start, moving_end, moving_t)
            moving_drawn = True

        if not (moving_drawn and moving_player == 1):
            self._draw_token(state.p1, p1_color, "P1")
        if not (moving_drawn and moving_player == 2):
            self._draw_token(state.p2, p2_color, "P2")

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
        legend_items = role_items if role_items is not None else [
            (BLUE, "Player 1"),
            (RED, "Player 2"),
        ]
        for i, (color, label) in enumerate(legend_items):
            yy = legend_y + i * 30
            pygame.draw.circle(self.screen, color, (panel_rect.x + 22, yy + 10), 8)
            text = self.small_font.render(label, True, TEXT_MAIN)
            self.screen.blit(text, (panel_rect.x + 40, yy + 1))

        rule_text = self.small_font.render("Move or block two cells", True, TEXT_MUTED)
        self.screen.blit(rule_text, (panel_rect.x + 16, panel_rect.bottom - 32))

        if focus_text:
            badge_rect = pygame.Rect(SIDEBAR_X + 12, SIDEBAR_Y + 500, SIDEBAR_WIDTH - 24, 56)
            pygame.draw.rect(self.screen, (12, 20, 36), badge_rect, border_radius=12)
            pygame.draw.rect(self.screen, focus_color if focus_color else NEON_CYAN, badge_rect, 2, border_radius=12)
            badge_text = self.small_font.render(focus_text, True, TEXT_MAIN)
            self.screen.blit(
                badge_text,
                (badge_rect.centerx - badge_text.get_width() // 2, badge_rect.centery - badge_text.get_height() // 2),
            )

        move_active = mode.startswith("move")
        block_active = mode.startswith("block")

        self._draw_button(self.move_btn, "MOVE", MOVE_COLOR, move_active, True)
        self._draw_button(self.block_btn, "BLOCK", BLOCK_COLOR, block_active, can_block and not must_move)

        # draw any deferred bottom-origin block previews on top of tokens/UI
        if deferred_bottom_anims:
            for combo, x, y in deferred_bottom_anims:
                self.screen.blit(combo, (x, y))

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
