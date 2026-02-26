import customtkinter as ctk
import random

# -------------------------
# HELPER: CENTER WINDOW
# -------------------------

def center_window(window, width, height):
    window.update_idletasks()
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    x = int((screen_w - width) / 2)
    y = int((screen_h - height) / 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


# -------------------------
# RESET POPUP WINDOW
# -------------------------

class ResetPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Reset Game")
        self.geometry("300x180")
        center_window(self, 300, 180)
        self.parent = parent

        label = ctk.CTkLabel(self, text="Reset the scores too?", font=ctk.CTkFont(size=16))
        label.pack(pady=20)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        yes_btn = ctk.CTkButton(btn_frame, text="Yes", width=80, command=self.reset_with_scores)
        no_btn = ctk.CTkButton(btn_frame, text="No", width=80, command=self.reset_without_scores)

        yes_btn.pack(side="left", padx=10)
        no_btn.pack(side="left", padx=10)

    def reset_with_scores(self):
        self.parent.x_wins = 0
        self.parent.o_wins = 0
        self.parent.ties = 0
        self.parent.update_scoreboard()
        self.parent.reset_board()
        self.destroy()

    def reset_without_scores(self):
        self.parent.reset_board()
        self.destroy()


# -------------------------
# MODE & DIFFICULTY WINDOWS
# -------------------------

selected_mode = None
selected_difficulty = None


class ModeWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Game Mode")
        self.geometry("300x220")
        center_window(self, 300, 220)

        label = ctk.CTkLabel(self, text="Select Game Mode", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=20)

        ctk.CTkButton(self, text="Player vs Player", command=self.choose_pvp).pack(pady=10)
        ctk.CTkButton(self, text="Player vs Computer", command=self.choose_ai).pack(pady=10)

    def choose_pvp(self):
        global selected_mode, selected_difficulty
        selected_mode = "pvp"
        selected_difficulty = None
        self.destroy()

    def choose_ai(self):
        global selected_mode
        selected_mode = "ai"
        self.destroy()


class DifficultyWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Choose Difficulty")
        self.geometry("300x250")
        center_window(self, 300, 250)

        label = ctk.CTkLabel(self, text="Select Difficulty", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=20)

        ctk.CTkButton(self, text="Easy", command=lambda: self.choose("easy")).pack(pady=10)
        ctk.CTkButton(self, text="Medium", command=lambda: self.choose("medium")).pack(pady=10)
        ctk.CTkButton(self, text="Unbeatable", command=lambda: self.choose("unbeatable")).pack(pady=10)

    def choose(self, difficulty):
        global selected_difficulty
        selected_difficulty = difficulty
        self.destroy()


# -------------------------
# MAIN GAME
# -------------------------

class TicTacToe(ctk.CTk):
    def __init__(self, mode, difficulty):
        super().__init__()
        self.title("Tic Tac Toe")
        self.geometry("800x600")
        center_window(self, 800, 600)

        self.mode = mode
        self.difficulty = difficulty
        self.turn = True
        self.game_over = False

        # Scoreboard
        self.x_wins = 0
        self.o_wins = 0
        self.ties = 0

        # Difficulty adjustment counters
        self.loss_streak = 0
        self.tie_streak = 0

        # Layout
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Board frame
        self.board_frame = ctk.CTkFrame(self)
        self.board_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        for i in range(3):
            self.board_frame.columnconfigure(i, weight=1)
            self.board_frame.rowconfigure(i, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self)
        self.sidebar.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Scoreboard UI
        title = ctk.CTkLabel(self.sidebar, text="SCOREBOARD", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, pady=(10, 5), padx=10, sticky="n")

        self.score_x_label = ctk.CTkLabel(self.sidebar, text="X Wins: 0", font=ctk.CTkFont(size=16))
        self.score_o_label = ctk.CTkLabel(self.sidebar, text="O Wins: 0", font=ctk.CTkFont(size=16))
        self.score_ties_label = ctk.CTkLabel(self.sidebar, text="Ties: 0", font=ctk.CTkFont(size=16))

        self.score_x_label.grid(row=1, column=0, sticky="n", pady=(5, 0))
        self.score_o_label.grid(row=1, column=0, sticky="n", pady=(30, 0))
        self.score_ties_label.grid(row=1, column=0, sticky="n", pady=(55, 0))

        # Reset button
        self.reset_button = ctk.CTkButton(
            self.sidebar,
            text="Reset Game",
            width=120,
            command=self.open_reset_popup
        )
        self.reset_button.grid(row=1, column=0, pady=(110, 0))

        # End panel
        self.end_panel = ctk.CTkFrame(self.sidebar)
        self.end_panel.grid(row=2, column=0, sticky="n", pady=(40, 0))
        self.end_panel.grid_remove()

        self.end_label = ctk.CTkLabel(self.end_panel, text="", font=ctk.CTkFont(size=16))
        self.end_label.pack(pady=(10, 10))

        btn_frame = ctk.CTkFrame(self.end_panel, fg_color="transparent")
        btn_frame.pack(pady=(0, 10))

        self.yes_button = ctk.CTkButton(btn_frame, text="Yes", width=70, command=self.handle_yes_button)
        self.no_button = ctk.CTkButton(btn_frame, text="No", width=70, command=self.no_more_play)

        self.yes_button.pack(side="left", padx=5)
        self.no_button.pack(side="left", padx=5)

        # Board buttons
        self.buttons = []
        for r in range(3):
            row_buttons = []
            for c in range(3):
                btn = CellButton(self.board_frame, self, r, c)
                btn.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    # -------------------------
    # RESET POPUP
    # -------------------------

    def open_reset_popup(self):
        ResetPopup(self)

    # -------------------------
    # SCOREBOARD
    # -------------------------

    def update_scoreboard(self):
        self.score_x_label.configure(text=f"X Wins: {self.x_wins}")
        self.score_o_label.configure(text=f"O Wins: {self.o_wins}")
        self.score_ties_label.configure(text=f"Ties: {self.ties}")

    # -------------------------
    # WIN LOGIC
    # -------------------------

    def board_full(self):
        return all(btn.text != "" for row in self.buttons for btn in row)

    def has_winner(self, symbol):
        b = self.buttons

        for r in range(3):
            if all(b[r][c].text == symbol for c in range(3)):
                return True

        for c in range(3):
            if all(b[r][c].text == symbol for r in range(3)):
                return True

        if b[0][0].text == symbol and b[1][1].text == symbol and b[2][2].text == symbol:
            return True

        if b[0][2].text == symbol and b[1][1].text == symbol and b[2][0].text == symbol:
            return True

        return False

    def get_winning_line(self, symbol):
        b = self.buttons

        for r in range(3):
            if all(b[r][c].text == symbol for c in range(3)):
                return [b[r][0], b[r][1], b[r][2]]

        for c in range(3):
            if all(b[r][c].text == symbol for r in range(3)):
                return [b[0][c], b[1][c], b[2][c]]

        if b[0][0].text == symbol and b[1][1].text == symbol and b[2][2].text == symbol:
            return [b[0][0], b[1][1], b[2][2]]

        if b[0][2].text == symbol and b[1][1].text == symbol and b[2][0].text == symbol:
            return [b[0][2], b[1][1], b[2][0]]

        return None

    def color_board_for_win(self, symbol):
        winning = self.get_winning_line(symbol)
        for row in self.buttons:
            for btn in row:
                btn.set_color("green" if btn in winning else "red")

    def color_board_for_tie(self):
        for row in self.buttons:
            for btn in row:
                btn.set_color("red")

    # -------------------------
    # DIFFICULTY DOWNGRADE
    # -------------------------

    def decrease_difficulty(self):
        if self.mode != "ai":
            return

        order = ["unbeatable", "medium", "easy"]

        if self.difficulty == "easy":
            self.end_label.configure(text="You're already on Easy.\nPlay again?")
            return

        idx = order.index(self.difficulty)
        self.difficulty = order[idx + 1]

        self.end_label.configure(text=f"Difficulty lowered to {self.difficulty.capitalize()}.\nPlay again?")

    def handle_yes_button(self):
        if "Decrease difficulty?" in self.end_label.cget("text"):
            self.decrease_difficulty()

        self.reset_board()

    # -------------------------
    # AI LOGIC
    # -------------------------

    def find_winning_move(self, symbol):
        for r in range(3):
            for c in range(3):
                btn = self.buttons[r][c]
                if btn.text == "":
                    btn.text = symbol
                    if self.has_winner(symbol):
                        btn.text = ""
                        return btn
                    btn.text = ""
        return None

    def minimax(self, is_max):
        if self.has_winner("O"):
            return 1
        if self.has_winner("X"):
            return -1
        if self.board_full():
            return 0

        best = -999 if is_max else 999
        symbol = "O" if is_max else "X"

        for r in range(3):
            for c in range(3):
                btn = self.buttons[r][c]
                if btn.text == "":
                    btn.text = symbol
                    score = self.minimax(not is_max)
                    btn.text = ""
                    best = max(best, score) if is_max else min(best, score)

        return best

    def best_move_minimax(self):
        best_score = -999
        best_btn = None

        for r in range(3):
            for c in range(3):
                btn = self.buttons[r][c]
                if btn.text == "":
                    btn.text = "O"
                    score = self.minimax(False)
                    btn.text = ""
                    if score > best_score:
                        best_score = score
                        best_btn = btn

        return best_btn

    def computer_move(self):
        if self.game_over:
            return

        if self.difficulty == "easy":
            empty = [btn for row in self.buttons for btn in row if btn.text == ""]
            random.choice(empty).set_symbol("O")

        elif self.difficulty == "medium":
            win = self.find_winning_move("O")
            if win:
                win.set_symbol("O")
            else:
                block = self.find_winning_move("X")
                if block:
                    block.set_symbol("O")
                else:
                    empty = [btn for row in self.buttons for btn in row if btn.text == ""]
                    random.choice(empty).set_symbol("O")

        elif self.difficulty == "unbeatable":
            best = self.best_move_minimax()
            best.set_symbol("O")

        # Check win
        if self.has_winner("O"):
            self.game_over = True
            self.o_wins += 1
            self.loss_streak += 1
            self.tie_streak = 0
            self.update_scoreboard()
            self.color_board_for_win("O")

            if self.loss_streak >= 3:
                self.show_end_panel("Computer (O) wins!\nYou've lost 3 times.\nDecrease difficulty?")
                self.loss_streak = 0
                return

            self.show_end_panel("Computer (O) wins!")
            return

        # Check tie
        if self.board_full():
            self.game_over = True
            self.ties += 1
            self.tie_streak += 1
            self.loss_streak = 0
            self.update_scoreboard()
            self.color_board_for_tie()

            if self.tie_streak >= 5:
                self.show_end_panel("It's a tie!\nYou've tied 5 times.\nDecrease difficulty?")
                self.tie_streak = 0
                return

            self.show_end_panel("It's a tie!")
            return

        self.turn = True

    # -------------------------
    # GAME FLOW
    # -------------------------

    def show_end_panel(self, message):
        self.end_label.configure(text=message)
        self.end_panel.grid()

    def handle_player_move(self, btn):
        if self.game_over or btn.text != "":
            return

        if self.mode == "pvp":
            symbol = "X" if self.turn else "O"
            btn.set_symbol(symbol)

            if self.has_winner(symbol):
                self.game_over = True
                if symbol == "X":
                    self.x_wins += 1
                else:
                    self.o_wins += 1
                self.update_scoreboard()
                self.color_board_for_win(symbol)
                self.show_end_panel(f"{symbol} wins!")
                return

            if self.board_full():
                self.game_over = True
                self.ties += 1
                self.update_scoreboard()
                self.color_board_for_tie()
                self.show_end_panel("It's a tie!")
                return

            self.turn = not self.turn

        else:
            if not self.turn:
                return

            btn.set_symbol("X")

            if self.has_winner("X"):
                self.game_over = True
                self.x_wins += 1
                self.update_scoreboard()
                self.color_board_for_win("X")
                self.show_end_panel("You (X) win!")
                return

            if self.board_full():
                self.game_over = True
                self.ties += 1
                self.update_scoreboard()
                self.color_board_for_tie()
                self.show_end_panel("It's a tie!")
                return

            self.turn = False
            self.computer_move()

    def reset_board(self):
        self.game_over = False
        self.turn = True
        self.end_panel.grid_remove()
        for row in self.buttons:
            for btn in row:
                btn.set_symbol("")
                btn.reset_color()

    def no_more_play(self):
        self.destroy()
        global selected_mode, selected_difficulty
        selected_mode = None
        selected_difficulty = None
        ModeWindow().mainloop()
        if selected_mode == "ai":
            DifficultyWindow().mainloop()
        if selected_mode is not None:
            TicTacToe(selected_mode, selected_difficulty).mainloop()


# -------------------------
# CELL BUTTON
# -------------------------

class CellButton(ctk.CTkButton):
    def __init__(self, parent, game, row, col):
        super().__init__(parent)
        self.game = game
        self.row = row
        self.col = col
        self.text = ""
        self.default_color = self.cget("fg_color")

        self.configure(
            text="",
            command=self.click,
            font=ctk.CTkFont(size=80, weight="bold"),
            width=150,
            height=150
        )

    def set_symbol(self, symbol):
        self.text = symbol
        self.configure(text=symbol)

    def set_color(self, color):
        self.configure(fg_color=color)

    def reset_color(self):
        self.configure(fg_color=self.default_color)

    def click(self):
        self.game.handle_player_move(self)


# -------------------------
# STARTUP
# -------------------------

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    ModeWindow().mainloop()

    if selected_mode == "ai":
        DifficultyWindow().mainloop()

    if selected_mode is not None:
        TicTacToe(selected_mode, selected_difficulty).mainloop()
