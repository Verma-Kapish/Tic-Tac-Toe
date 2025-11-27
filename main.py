"""
Next‑Gen Handwritten Tic Tac Toe (Tkinter)
- Colorful, modern look
- Handwritten-style X and O with simple stroke animation
- Draws a full 3-length winning line and confetti effect
- Two-player (local) play

Run with: python tic_tac_toe_handwritten_tkinter.py (requires Python 3.x)
"""

import tkinter as tk
from tkinter import font
import random
import math

# --- Configuration ---
WINDOW_W, WINDOW_H = 540, 640
BOARD_SIZE = 3
MARGIN = 40
BOARD_W = WINDOW_W - MARGIN * 2
CELL = BOARD_W // BOARD_SIZE
LINE_WIDTH = 6
SYMBOL_WIDTH = 8
ANIM_SPEED = 10  # ms per animation frame
CONFETTI_COUNT = 40

# Color palette (feel free to tweak)
BG_TOP = (28, 40, 80)
BG_BOTTOM = (15, 135, 185)
GRID_COLOR = "#f8f9fa"
TILE_COLORS = ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF"]
X_COLOR = "#2E2B5F"
O_COLOR = "#2E8B57"
HIGHLIGHT = "#FFD166"

# Utility
def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb

def blend(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# --- App ---
class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        root.title("!Tic-Tac-Toe 🎮")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WINDOW_W, height=WINDOW_H, highlightthickness=0)
        self.canvas.pack()

        # fonts (handwritten-like). If unavailable, Tk will fallback.
        self.font_hand = font.Font(family="Segoe Script", size=48, weight="bold")
        self.font_small = font.Font(family="Segoe Script", size=14)

        # game state
        self.board = [None] * 9  # None, 'X', 'O'
        self.player = 'X'
        self.game_over = False
        self.animating = False
        self.winning_line = None

        # confetti state
        self.confetti = []

        # draw UI
        self.draw_background()
        self.draw_header()
        self.draw_board_grid()
        self.draw_control_buttons()

        # bind
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_background(self):
        # simple vertical gradient
        steps = 60
        for i in range(steps):
            t = i / (steps - 1)
            c = blend(BG_TOP, BG_BOTTOM, t)
            self.canvas.create_rectangle(0, i * (WINDOW_H / steps), WINDOW_W, (i+1) * (WINDOW_H/steps), fill=rgb_to_hex(c), width=0)
        # soft vignette (subtle)
        self.canvas.create_oval(-200, -200, WINDOW_W+200, WINDOW_H+200, outline='', fill='', width=0)

    def draw_header(self):
        # Title card
        self.canvas.create_rectangle(MARGIN, 10, WINDOW_W - MARGIN, 90, fill='#0b1b2b', outline='', width=0, tags='title_card')
        self.canvas.create_text(WINDOW_W//2, 30, text="TIC — TAC — TOE", font=("Helvetica", 18, 'bold'), fill='#ffd700')
        self.turn_text = self.canvas.create_text(WINDOW_W//2, 60, text="Player X's turn", font=("Segoe Script", 14), fill='#ffffff')

    def draw_board_grid(self):
        # background tiles (subtle rounded look)
        self.cells_coords = []
        start_x = MARGIN
        start_y = 110
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1 = start_x + c * CELL + 8
                y1 = start_y + r * CELL + 8
                x2 = x1 + CELL - 16
                y2 = y1 + CELL - 16
                color = random.choice(TILE_COLORS)
                tile = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='', width=0, tags=('cell_bg', f'cell_{r}_{c}'))
                self.cells_coords.append((x1, y1, x2, y2))

        # draw grid lines thinner + modern
        for i in range(1, BOARD_SIZE):
            # vertical
            x = start_x + i * CELL
            for offset in (0, 1, 2, -1):
                self.canvas.create_line(x+offset, start_y+6, x+offset, start_y+BOARD_SIZE*CELL-6, fill=GRID_COLOR, width=LINE_WIDTH-2-offset)
            # horizontal
            y = start_y + i * CELL
            for offset in (0, 1, 2, -1):
                self.canvas.create_line(start_x+6, y+offset, start_x+BOARD_SIZE*CELL-6, y+offset, fill=GRID_COLOR, width=LINE_WIDTH-2-offset)

    def draw_control_buttons(self):
        # Reset button
        btn_x = WINDOW_W // 2
        self.canvas.create_rectangle(btn_x-70, WINDOW_H-80, btn_x+70, WINDOW_H-40, fill='#ffffff', outline='', width=0)
        self.canvas.create_text(btn_x, WINDOW_H-60, text='New Game', font=('Helvetica', 12, 'bold'), fill='#0b1b2b', tags='reset_btn')
        self.canvas.tag_bind('reset_btn', '<Button-1>', lambda e: self.reset_game())

        # small hint
        self.canvas.create_text(WINDOW_W//2, WINDOW_H-20, text='Handwritten style • Click a tile to play', font=('Helvetica', 10), fill='#ffffff')

    def on_click(self, event):
        if self.game_over or self.animating:
            # allow clicking reset button area
            # check reset rect
            bx1, by1, bx2, by2 = (WINDOW_W//2-70, WINDOW_H-80, WINDOW_W//2+70, WINDOW_H-40)
            if bx1 <= event.x <= bx2 and by1 <= event.y <= by2:
                self.reset_game()
            return

        # detect which cell clicked
        for idx, (x1, y1, x2, y2) in enumerate(self.cells_coords):
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                if self.board[idx] is None:
                    self.place_symbol(idx, self.player)
                return

    def place_symbol(self, idx, player):
        self.board[idx] = player
        self.animating = True
        x1, y1, x2, y2 = self.cells_coords[idx]
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        size = CELL * 0.28
        if player == 'X':
            self.animate_x(cx, cy, size, idx, 0)
        else:
            self.animate_o(cx, cy, size, idx, 0)

    # --- Animations ---
    def animate_x(self, cx, cy, size, idx, step):
        # draw two strokes progressively
        max_steps = 10
        if step == 0:
            # store id list for cleanup
            self.board_anim_ids = []
        t = step / max_steps
        # endpoints for stroke 1
        xA1, yA1 = cx - size, cy - size
        xA2, yA2 = cx + size, cy + size
        # endpoints for stroke 2
        xB1, yB1 = cx - size, cy + size
        xB2, yB2 = cx + size, cy - size

        # partial positions
        px1 = xA1 + (xA2 - xA1) * t
        py1 = yA1 + (yA2 - yA1) * t
        px2 = xB1 + (xB2 - xB1) * t
        py2 = yB1 + (yB2 - yB1) * t

        # remove previous partial strokes from this cell
        for _id in getattr(self, 'board_anim_ids', []):
            try:
                self.canvas.delete(_id)
            except: pass
        self.board_anim_ids = []

        # jitter to look handwritten
        jitter = 4 * (1 - abs(0.5 - t))
        id1 = self.canvas.create_line(xA1+jitter, yA1+jitter, px1, py1, width=SYMBOL_WIDTH, capstyle='round', joinstyle='round', fill=X_COLOR)
        id2 = self.canvas.create_line(xB1-jitter, yB1+jitter, px2, py2, width=SYMBOL_WIDTH, capstyle='round', joinstyle='round', fill=X_COLOR)
        self.board_anim_ids.extend([id1, id2])

        if step < max_steps:
            self.root.after(ANIM_SPEED, lambda: self.animate_x(cx, cy, size, idx, step+1))
        else:
            # finalize: draw a crisp X text (handwritten font) to look polished
            for _id in self.board_anim_ids:
                self.canvas.delete(_id)
            txt = self.canvas.create_text(cx, cy, text='X', font=self.font_hand, fill=X_COLOR, anchor='center')
            self.animating = False
            self.after_move()

    def animate_o(self, cx, cy, size, idx, step):
        # draw an expanding arc to look like a pen drawing O
        max_steps = 16
        if step == 0:
            self.board_anim_ids = []
        extent = 360 * (step / max_steps)
        for _id in getattr(self, 'board_anim_ids', []):
            try:
                self.canvas.delete(_id)
            except: pass
        self.board_anim_ids = []

        bbox = (cx - size, cy - size, cx + size, cy + size)
        id_arc = self.canvas.create_arc(bbox, start=90, extent=extent, style='arc', width=SYMBOL_WIDTH, outline=O_COLOR)
        self.board_anim_ids.append(id_arc)

        if step < max_steps:
            self.root.after(ANIM_SPEED, lambda: self.animate_o(cx, cy, size, idx, step+1))
        else:
            for _id in self.board_anim_ids:
                self.canvas.delete(_id)
            txt = self.canvas.create_text(cx, cy, text='O', font=self.font_hand, fill=O_COLOR, anchor='center')
            self.animating = False
            self.after_move()

    def after_move(self):
        # check for win or draw
        winner, line = self.check_win()
        if winner:
            self.game_over = True
            self.draw_winning_line(line)
            self.canvas.itemconfigure(self.turn_text, text=f"Player {winner} wins!", fill=HIGHLIGHT)
            self.spawn_confetti()
            return
        if all(v is not None for v in self.board):
            self.game_over = True
            self.canvas.itemconfigure(self.turn_text, text="It's a draw!", fill='#eeeeee')
            return
        # switch player
        self.player = 'O' if self.player == 'X' else 'X'
        self.canvas.itemconfigure(self.turn_text, text=f"Player {self.player}'s turn")

    def check_win(self):
        lines = [
            (0,1,2), (3,4,5), (6,7,8),
            (0,3,6), (1,4,7), (2,5,8),
            (0,4,8), (2,4,6)
        ]
        for a,b,c in lines:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a], (a,b,c)
        return None, None

    def draw_winning_line(self, line):
        # compute centers
        centers = []
        for (x1,y1,x2,y2) in self.cells_coords:
            centers.append(((x1+x2)/2, (y1+y2)/2))
        a, b, c = line
        x1, y1 = centers[a]
        x3, y3 = centers[c]
        # draw multiple layered lines for glow
        for i, width in enumerate((18, 12, 6)):
            color = HIGHLIGHT if i == 0 else '#fff3bf'
            self.canvas.create_line(x1, y1, x3, y3, width=width, capstyle='round', fill=color)

    # --- Confetti ---
    def spawn_confetti(self):
        self.confetti = []
        for i in range(CONFETTI_COUNT):
            x = random.uniform(MARGIN, WINDOW_W - MARGIN)
            y = random.uniform(120, WINDOW_H - 160)
            vx = random.uniform(-3, 3)
            vy = random.uniform(-1, 4)
            size = random.uniform(4, 9)
            color = random.choice(TILE_COLORS)
            cid = self.canvas.create_oval(x, y, x+size, y+size, fill=color, outline='')
            self.confetti.append({'id': cid, 'x': x, 'y': y, 'vx': vx, 'vy': vy, 'size': size})
        self.animate_confetti()

    def animate_confetti(self):
        still = False
        for p in self.confetti:
            p['vy'] += 0.15  # gravity
            p['x'] += p['vx']
            p['y'] += p['vy']
            if p['y'] < WINDOW_H - 20:
                still = True
            self.canvas.coords(p['id'], p['x'], p['y'], p['x']+p['size'], p['y']+p['size'])
        if still:
            self.root.after(30, self.animate_confetti)

    def reset_game(self):
        # clear board visuals but keep background
        self.canvas.delete('all')
        self.board = [None] * 9
        self.player = 'X'
        self.game_over = False
        self.animating = False
        self.draw_background()
        self.draw_header()
        self.draw_board_grid()
        self.draw_control_buttons()
        self.confetti = []


if __name__ == '__main__':
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()
