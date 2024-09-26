import tkinter
import tkinter as tk
from tkinter import messagebox, simpledialog
import PIL
from PIL import Image, ImageTk
import random
import os

class PauseMenu(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Paused")
        self.geometry("400x400")
        self.resizable(False, False)
        self.configure(bg=master.current_theme['bg'])
        self.protocol("WM_DELETE_WINDOW", self.master.on_closing)
        try:
            self.icon_img = ImageTk.PhotoImage(file='TetrisIcon.ico')
            self.iconphoto(False, self.icon_img)
        except Exception as e:
            print(f"Error loading icon: {e}")


        # Center the window
        self.center_window()

        # Create a frame for the pause menu content
        self.menu_frame = tk.Frame(self, bg=master.current_theme['bg'])
        self.menu_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Add a heading label
        tk.Label(self.menu_frame, text="Game Paused", font=("Helvetica", 28, 'bold'),
                 bg=master.current_theme['bg'], fg=master.current_theme['fg']).pack(pady=10)

        # Add buttons with improved styling
        button_style = {
            'font': ('Helvetica', 16),
            'width': 20,
            'padx': 10,
            'pady': 10,
            'bg': master.current_theme['fg'],
            'fg': master.current_theme['bg']
        }

        tk.Button(self.menu_frame, text="Resume", command=self.resume_game, **button_style).pack(pady=10)
        tk.Button(self.menu_frame, text="Restart", command=self.restart_game, **button_style).pack(pady=10)
        tk.Button(self.menu_frame, text="Quit", command=self.quit_game, **button_style, ).pack(pady=10)

    def center_window(self):
        self.update_idletasks()  # Update "requested size" from geometry manager
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def resume_game(self):
        self.destroy()
        self.master.resume_game()

    def restart_game(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to restart?"):
            self.master.restart_game()
            self.destroy()

    def quit_game(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.master.quit()

class Tetris(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title('Tetris')
        self.geometry("490x700")
        self.resizable(False, False)
        self.paused = False
        self.center_window()
        try:
            self.icon_img = ImageTk.PhotoImage(file='TetrisIcon.ico')
            self.iconphoto(False, self.icon_img)
        except Exception as e:
            print(f"Error loading icon: {e}")
        self.deiconify()

        # Define colors for themes
        self.dark_theme = {
            'bg': 'black',
            'fg': 'white',
            'border': 'gray',
            'cell': '#00FFFF',
            'next_bg': 'black',
            'next_border': 'gray',
            'title': '#FF6347'
        }

        self.light_theme = {
            'bg': 'white',
            'fg': 'black',
            'border': 'black',
            'cell': '#00FFFF',
            'next_bg': 'white',
            'next_border': 'black',
            'title': '#FF4500'
        }

        # Set default theme to dark
        self.current_theme = self.dark_theme

        # Create title frame to hold colored letters
        self.title_frame = tk.Frame(self, bg=self.current_theme['bg'])
        self.title_frame.grid(row=0, column=0, columnspan=2, pady=5)

        # Create colored letters for the title
        self.create_colored_title()

        # Create game canvas
        self.canvas = tk.Canvas(self, width=300, height=600, bg=self.current_theme['bg'])
        self.canvas.grid(row=1, column=0, rowspan=3, padx=5, pady=5)
        self.create_border(self.canvas)

        # Create score label
        self.score_label = tk.Label(self, text="Score: 0", font=('Helvetica', 14), bg=self.current_theme['bg'],
                                    fg=self.current_theme['fg'])
        self.score_label.grid(row=1, column=1, padx=5, pady=5, sticky="n")

        # Create high score label
        self.high_score_label = tk.Label(self, text="High Score: 0", font=('Helvetica', 14),
                                         bg=self.current_theme['bg'], fg=self.current_theme['fg'])
        self.high_score_label.grid(row=1, column=1, padx=5, pady=40, sticky="n")

        # Create level label
        self.level_label = tk.Label(self, text="Level: 0", font=('Helvetica', 14), bg=self.current_theme['bg'],
                                    fg=self.current_theme['fg'])
        self.level_label.grid(row=2, column=1, padx=5, pady=100, sticky="n")

        # Create next piece canvas
        self.next_canvas = tk.Canvas(self, width=120, height=120, bg=self.current_theme['next_bg'])
        self.next_canvas.grid(row=3, column=1, padx=5, pady=5, sticky="n")
        self.create_border(self.next_canvas)

        # Create reset high score button
        self.reset_button = tk.Button(self, text="Reset High Score", command=self.reset_high_score,
                                      bg=self.current_theme['bg'], fg=self.current_theme['fg'])
        self.reset_button.grid(row=2, column=1, padx=5, pady=5, sticky="n")

        # Create theme toggle button
        self.theme_button = tk.Button(self, text="Switch to Light Theme", command=self.toggle_theme,
                                      bg=self.current_theme['bg'], fg=self.current_theme['fg'])
        self.theme_button.grid(row=2, column=1, padx=5, pady=35, sticky="n")
        self.theme_button.config(state='disabled')  # Disable the theme button initially

        # Initialize game variables
        self.score = 0
        self.high_score = self.load_high_score()
        self.update_high_score_label()
        self.level = 0
        self.update_level_label()
        self.game_over = False
        self.update_interval = 50  # Update every 50 milliseconds
        self.fall_interval = 800 # Initial block falls every 1000 milliseconds
        self.fall_timer = 0

        self.board = [[0] * 10 for _ in range(20)]

        self.shapes = [
            [[1, 1, 1, 1]],  # I
            [[1, 1],
             [1, 1]],  # O
            [[0, 1, 0],
             [1, 1, 1]],  # T
            [[1, 1, 0],
             [0, 1, 1]],  # Z
            [[0, 1, 1],
             [1, 1, 0]],  # S
            [[1, 1, 1],
             [1, 0, 0]],  # L
            [[1, 1, 1],
             [0, 0, 1]],  # J
        ]
        self.shape_names = ['I', 'O', 'T', 'Z', 'S', 'L', 'J']
        self.shape_dict = dict(zip(self.shape_names, self.shapes))

        self.shape_colors = [
            '#00FFFF', '#FFFF00', '#800080', '#0000FF', '#FFA500', '#00FF00', '#FF0000', '#fb6f92'
        ]

        self.current_shape = None
        self.current_color = None
        self.current_x = 0
        self.current_y = 0

        self.bag = []
        self.fill_bag()
        self.next_shape = self.get_next_shape()

        self.bind_all('<Key>', self.key_pressed)

        self.countdown(3)

    def on_closing(self):
        pass

    def center_window(self):
        self.update_idletasks()  # Update "requested size" from geometry manager
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_colored_title(self):
        # Colors of the Tetris title resembling the original
        colors = ['#FF0000', '#FF9900', '#FFFF00', '#33FF00', '#00CCFF', '#0033CC']
        letters = 'TETRIS'
        for i, letter in enumerate(letters):
            label = tk.Label(self.title_frame, text=letter, font=('Helvetica', 24, 'bold'), bg=self.current_theme['bg'],
                             fg=colors[i], padx=2)
            label.grid(row=0, column=i)

    def countdown(self, count):
        self.theme_button.config(state='disabled')
        self.reset_button.config(state='disabled')

        if count > 0:
            self.canvas.delete('all')
            self.counting = True
            self.configure(bg=self.current_theme['bg'])
            self.canvas.create_text(
                150, 300, text=str(count), fill=self.current_theme['fg'], font=("Helvetica", 48)
            )
            self.after(1000, self.countdown, count - 1)
        else:
            self.counting = False
            self.theme_button.config(state='normal')
            self.reset_button.config(state='normal')
            self.new_shape()  # Start the game
            self.update()  # Start the game loop

    def new_shape(self):
        self.current_shape = self.next_shape
        self.current_color = self.shape_colors[self.shapes.index(self.current_shape)]
        self.next_shape = self.get_next_shape()
        self.current_x = 3
        self.current_y = 0

        if self.collision():
            self.game_over = True
            if self.score > self.high_score:
                if not self.isDebug:
                    self.high_score = self.score
                    self.save_high_score()
                    self.update_high_score_label()
            self.show_game_over_screen()
            self.theme_button.config(state='disabled')  # Disable the theme button after game over

        self.draw_next_shape()

    def get_next_shape(self):
        if not self.bag:
            self.fill_bag()
        print(self.bag[::-1])
        shape_name = self.bag.pop()
        return self.shape_dict[shape_name]

    def fill_bag(self):
        self.bag = self.shape_names[:]
        random.shuffle(self.bag)


    def collision(self):
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell and (
                        x + self.current_x < 0 or
                        x + self.current_x >= len(self.board[0]) or
                        y + self.current_y >= len(self.board) or
                        self.board[y + self.current_y][x + self.current_x]
                ):
                    return True
        return False

    def freeze(self):
        if self.game_over:
            return

        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.board[y + self.current_y][x + self.current_x] = self.current_color

        self.score += 50  # Add 50 points for placing a piece
        self.score_label.config(text=f"Score: {self.score}")
        self.clear_lines()
        self.update_level()  # Update the level based on the new score
        self.new_shape()

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        lines_cleared = len(self.board) - len(new_board)
        if lines_cleared < 4:
            self.score += lines_cleared * 100
            
        else:
            self.score += 500
            print('TETRIS')
        self.score_label.config(text=f"Score: {self.score}")
        while len(new_board) < len(self.board):
            new_board.insert(0, [0] * len(self.board[0]))
        self.board = new_board

    def update_level(self):
        self.level = min(self.score // 1000, 20)
        self.fall_interval = max(800 - self.level * 60, 10) if self.level <= 9 else max(200 - (self.level - 10) * 20, 10)
        if self.score >= 21000:
            self.level = "Death_Wall"
            self.fall_interval = 10
        self.level_label.config(text=f"Level: {self.level}")

    def rotate(self):
        if self.game_over:
            return

        self.current_shape = [list(row) for row in zip(*self.current_shape[::-1])]
        if self.collision():
            self.current_shape = [list(row) for row in zip(*self.current_shape)][::-1]

    def move(self, dx, dy):
        if self.game_over:
            return

        self.current_x += dx
        if self.collision():
            self.current_x -= dx

        self.current_y += dy
        if self.collision():
            self.current_y -= dy
            if dy:
                self.freeze()

    def key_pressed(self, event):
        if self.game_over:
            if event.keysym == 'r':
                self.restart_game()
            elif event.keysym == 'q':
                self.quit()
            return

        if not self.counting:
            if event.keysym == 'Left':
                self.move(-1, 0)
            elif event.keysym == 'Right':
                self.move(1, 0)
            elif event.keysym == 'Down':
                self.move(0, 1)
            elif event.keysym == 'Up':
                self.rotate()
            elif event.keysym == 'space':
                self.drop()
            elif event.keysym == 'p':
                self.pause_game()
            elif event.keysym == 'd':
                self.debug_score()
        else:
            return

        self.draw_board()
    def debug_score(self):
        self.score = simpledialog.askinteger('Score', 'Enter the new score')
        self.score_label.config(text=f"Score: {self.score}")
        self.isDebug = True

    def resume_game(self):
        self.paused = False
        self.update()
    def pause_game(self):
        if self.paused:
            return
        self.paused = True
        self.pause_menu = PauseMenu(self)
        self.pause_menu.grab_set()

    def drop(self):
        if self.game_over:
            return

        while not self.collision():
            self.current_y += 1
        self.current_y -= 1
        self.freeze()

    def draw_board(self):
        self.canvas.delete('all')
        self.draw_grid()
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_cell(self.canvas, x, y, cell)
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_cell(self.canvas, x + self.current_x, y + self.current_y, self.current_color)

    def draw_cell(self, canvas, x, y, color):
        cell_size = 30
        x0 = x * cell_size
        y0 = y * cell_size
        x1 = x0 + cell_size
        y1 = y0 + cell_size
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=self.current_theme['border'])

    def draw_next_shape(self):
        self.next_canvas.delete('all')
        self.draw_grid(next_canvas=True)
        offset_x = (4 - len(self.next_shape[0])) // 2
        offset_y = (4 - len(self.next_shape)) // 2
        for y, row in enumerate(self.next_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_cell(self.next_canvas, offset_x + x, offset_y + y, self.shape_colors[self.shapes.index(self.next_shape)])

    def draw_grid(self, next_canvas=False):
        if next_canvas:
            canvas = self.next_canvas
            width, height = 120, 120
            cell_size = 30
        else:
            canvas = self.canvas
            width, height = 300, 600
            cell_size = 30

        for i in range(0, width, cell_size):
            canvas.create_line(i, 0, i, height, fill=self.current_theme['border'], width=1)
        for i in range(0, height, cell_size):
            canvas.create_line(0, i, width, i, fill=self.current_theme['border'], width=1)

    def create_border(self, canvas):
        canvas.create_rectangle(
            0, 0, canvas.winfo_width(), canvas.winfo_height(),
            outline=self.current_theme['border'], width=2
        )

    def load_high_score(self):
        if os.path.exists('highscore.txt'):
            with open('highscore.txt', 'r') as file:
                return int(file.read().strip())
        return 0

    def save_high_score(self):
        with open('highscore.txt', 'w') as file:
            file.write(str(self.high_score))

    def reset_high_score(self):
        if messagebox.askyesno("Reset High Score", "Are you sure you want to reset the high score?"):
            self.high_score = 0
            self.save_high_score()
            self.update_high_score_label()
            print("High score has been reset.")

    def update_high_score_label(self):
        self.high_score_label.config(text=f"High Score: {self.high_score}")

    def update_level_label(self):
        self.level_label.config(text=f"Level: {self.level}")

    def update(self):
        if self.game_over:
            self.show_game_over_screen()
            return

        if self.paused:
            return  # Stop the update loop if the game is paused

        self.fall_timer += self.update_interval
        if self.fall_timer >= self.fall_interval:
            self.move(0, 1)
            self.fall_timer = 0

        self.draw_board()
        self.after(self.update_interval, self.update)

    def show_game_over_screen(self):
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, 300, 600, fill=self.current_theme['bg'], outline='')
        self.canvas.create_text(
            150, 250, text="GAME OVER", fill=self.current_theme['fg'], font=("Helvetica", 24, "bold")
        )
        self.canvas.create_text(
            150, 300, text=f"Final Score: {self.score}", fill=self.current_theme['fg'], font=("Helvetica", 18)
        )
        self.canvas.create_text(
            150, 580, text="Press 'r' to restart or 'q' to quit", fill=self.current_theme['fg'], font=("Helvetica", 11)
        )
        self.create_replay_button()

    def create_replay_button(self):
        if hasattr(self, 'replay_button'):
            self.replay_button.destroy()
        self.replay_button = tk.Button(self.canvas, text="Play Again", font=("Helvetica", 14), command=self.restart_game,
                                      bg=self.current_theme['fg'], fg=self.current_theme['bg'])
        self.replay_button.place(x=100, y=350, width=100, height=40)

    def restart_game(self):
        self.score = 0
        self.level = 0
        self.bag = []
        self.fall_interval = 800
        self.fall_timer = 0
        self.score_label.config(text="Score: 0")
        self.level_label.config(text="Level: 0")
        self.board = [[0] * 10 for _ in range(20)]
        self.game_over = False
        self.paused = False
        self.isDebug = False
        self.next_shape = self.get_next_shape()
        self.new_shape()
        self.update()
        if hasattr(self, 'replay_button'):
            self.replay_button.destroy()
        self.theme_button.config(state='normal')  # Re-enable the theme button after restarting the game

    def toggle_theme(self):
        if self.current_theme == self.dark_theme:
            self.current_theme = self.light_theme
            self.theme_button.config(text="Switch to Dark Theme")
        else:
            self.current_theme = self.dark_theme
            self.theme_button.config(text="Switch to Light Theme")

        self.configure(bg=self.current_theme['bg'])
        self.title_frame.config(bg=self.current_theme['bg'])
        self.canvas.config(bg=self.current_theme['bg'])
        self.next_canvas.config(bg=self.current_theme['next_bg'])
        self.score_label.config(bg=self.current_theme['bg'], fg=self.current_theme['fg'])
        self.high_score_label.config(bg=self.current_theme['bg'], fg=self.current_theme['fg'])
        self.level_label.config(bg=self.current_theme['bg'], fg=self.current_theme['fg'])
        self.reset_button.config(bg=self.current_theme['bg'], fg=self.current_theme['fg'])
        self.theme_button.config(bg=self.current_theme['bg'], fg=self.current_theme['fg'])

        self.draw_board()
        self.draw_next_shape()
        self.create_border(self.canvas)
        self.create_border(self.next_canvas)

if __name__ == '__main__':
    app = Tetris()
    app.mainloop()
    print("program: Quit")
