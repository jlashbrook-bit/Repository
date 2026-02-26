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
# MODE & DIFFICULTY WINDOWS
# -------------------------

selected_mode = None       # "pvp" or "ai"
selected_difficulty = None # "easy", "medium", "unbeatable" or None


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
        self.minsize(800, 600)
        self.maxsize(800, 600)

        self.mode = mode              # "pvp" or "ai"
        self.difficulty = difficulty  # None, "easy", "medium", "unbeatable"
        self.turn = True              # True = X, False = O (or AI)
        self.game_over = False

        # Scoreboard
        self.x_wins = 0
        self.o_wins = 0
        self.ties = 0

        # Layout: left = board, right = sidebar
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Board frame
        self.board_frame = ctk.CTkFrame(self)
        self.board_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        for i in range(3):
            self.board_frame.columnconfigure(i, weight=1)
            self.board_frame.rowconfigure(i, weight=1)

        # Sidebar frame
        self.sidebar = ctk.CTkFrame(self)
        self.sidebar.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.sidebar.rowconfigure(0, weight=0)
        self.sidebar.rowconfigure(1, weight=0)
        self.sidebar.rowconfigure(2, weight=1)

        # Scoreboard UI
        title = ctk.CTkLabel(self.sidebar, text="SCOREBOARD", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, pady=(10, 5), padx=10, sticky="n")

        self.score_x_label = ctk.CTkLabel(self.sidebar, text="X Wins: 0", font=ctk.CTkFont(size=16))
        self.score_o_label = ctk.CTkLabel(self.sidebar, text="O Wins: 0", font=ctk.CTkFont(size=16))
        self.score_ties_label = ctk.CTkLabel(self.sidebar, text="Ties: 0", font=ctk.CTkFont(size=16))

        self.score_x_label.grid(row=1, column=0, sticky="n", pady=(5, 0))
        self.score_o_label.grid(row=1, column=0, sticky="n", pady=(30, 0))
        self.score_ties_label.grid(row=1, column=0, sticky="n", pady=(55, 0))

        # End-of-game prompt panel (under scoreboard)
        self.end_panel = ctk.CTkFrame(self.sidebar)
        self.end_panel.grid(row=2, column=0, sticky="n", pady=(40, 0), padx=10)
        self.end_panel.grid_remove()  # hidden initially

        self.end_label = ctk.CTkLabel(self.end_panel, text="", font=ctk.CTkFont(size=16))
        self.end_label.pack(pady=(10, 10))

        btn_frame = ctk.CTkFrame(self.end_panel, fg_color="transparent")
        btn_frame.pack(pady=(0, 10))

        self.yes_button = ctk.CTkButton(btn_frame, text="Yes", width=70, command=self.reset_board)
        self.no_button = ctk.CTkButton(btn_frame, text="No", width=70, command=self.no_more_play)

        self.yes_button.pack(side="left", padx=5)
        self.no_button.pack(side="left", padx=5)

        # Create buttons
        self.buttons = []
        for row in range(3):
            row_buttons = []
            for col in range(3):
                btn = CellButton(self.board_frame, self, row, col)
                btn.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    # -------------------------
    # SCOREBOARD
    # -------------------------

    def update_scoreboard(self):
        self.score_x_label.configure(text=f"X Wins: {self.x_wins}")
        self.score_o_label.configure(text=f"O Wins: {self.o_wins}")
        self.score_ties_label.configure(text=f"Ties: {self.ties}")

    # -------------------------
    # BOARD / WIN LOGIC
    # -------------------------

    def board_full(self):
        for row in self.buttons:
            for btn in row:
                if btn.text == "":
                    return False
        return True

    def has_winner(self, symbol):
        b = self.buttons

        # Rows
        for r in range(3):
            if b[r][0].text == symbol and b[r][1].text == symbol and b[r][2].text == symbol:
                return True

        # Columns
        for c in range(3):
            if b[0][c].text == symbol and b[1][c].text == symbol and b[2][c].text == symbol:
                return True

        # Diagonals
        if b[0][0].text == symbol and b[1][1].text == symbol and b[2][2].text == symbol:
            return True
        if b[0][2].text == symbol and b[1][1].text == symbol and b[2][0].text == symbol:
            return True

        return False

    def get_winning_line(self, symbol):
        b = self.buttons

        # Rows
        for r in range(3):
            if b[r][0].text == symbol and b[r][1].text == symbol and b[r][2].text == symbol:
                return [b[r][0], b[r][1], b[r][2]]

        # Columns
        for c in range(3):
            if b[0][c].text == symbol and b[1][c].text == symbol and b[2][c].text == symbol:
                return [b[0][c], b[1][c], b[2][c]]

        # Diagonals
        if b[0][0].text == symbol and b[1][1].text == symbol and b[2][2].text == symbol:
            return [b[0][0], b[1][1], b[2][2]]
        if b[0][2].text == symbol and b[1][1].text == symbol and b[2][0].text == symbol:
            return [b[0][2], b[1][1], b[2][0]]

        return None

    def show_end_panel(self, message):
        self.end_label.configure(text=message + "\nPlay again?")
        self.end_panel.grid()  # show panel

    def color_board_for_win(self, winner_symbol):
        winning_line = self.get_winning_line(winner_symbol)
        for row in self.buttons:
            for btn in row:
                if winning_line and btn in winning_line:
                    btn.set_color("green")
                else:
                    btn.set_color("red")

    def color_board_for_tie(self):
        for row in self.buttons:
            for btn in row:
                btn.set_color("red")

    # -------------------------
    # AI LOGIC
    # -------------------------

    def find_winning_move(self, symbol):
        """Return a button that lets 'symbol' win, or None."""
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

    def minimax(self, is_maximizing):
        if self.has_winner("O"):
            return 1
        if self.has_winner("X"):
            return -1
        if self.board_full():
            return 0

        if is_maximizing:
            best_score = -999
            for r in range(3):
                for c in range(3):
                    btn = self.buttons[r][c]
                    if btn.text == "":
                        btn.text = "O"
                        score = self.minimax(False)
                        btn.text = ""
                        best_score = max(best_score, score)
            return best_score
        else:
            best_score = 999
            for r in range(3):
                for c in range(3):
                    btn = self.buttons[r][c]
                    if btn.text == "":
                        btn.text = "X"
                        score = self.minimax(True)
                        btn.text = ""
                        best_score = min(best_score, score)
            return best_score

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

        # EASY: random
        if self.difficulty == "easy":
            empty = [btn for row in self.buttons for btn in row if btn.text == ""]
            if empty:
                choice = random.choice(empty)
                choice.set_symbol("O")

        # MEDIUM: win → block → random
        elif self.difficulty == "medium":
            win_btn = self.find_winning_move("O")
            if win_btn:
                win_btn.set_symbol("O")
            else:
                block_btn = self.find_winning_move("X")
                if block_btn:
                    block_btn.set_symbol("O")
                else:
                    empty = [btn for row in self.buttons for btn in row if btn.text == ""]
                    if empty:
                        random.choice(empty).set_symbol("O")

        # UNBEATABLE: minimax
        elif self.difficulty == "unbeatable":
            best_btn = self.best_move_minimax()
            if best_btn:
                best_btn.set_symbol("O")

        # After AI move, check game state
        if self.has_winner("O"):
            self.game_over = True
            self.o_wins += 1
            self.update_scoreboard()
            self.color_board_for_win("O")
            self.show_end_panel("Computer (O) wins!")
            return

        if self.board_full():
            self.game_over = True
            self.ties += 1
            self.update_scoreboard()
            self.color_board_for_tie()
            self.show_end_panel("It's a tie!")
            return

        self.turn = True  # back to player

    # -------------------------
    # GAME FLOW
    # -------------------------

    def handle_player_move(self, btn):
        if self.game_over or btn.text != "":
            return

        # PVP mode: alternate X and O
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

        # AI mode: player is always X
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
        # Close game and go back to mode selection
        self.destroy()
        # Restart mode selection flow
        global selected_mode, selected_difficulty
        selected_mode = None
        selected_difficulty = None
        ModeWindow().mainloop()
        if selected_mode == "ai":
            DifficultyWindow().mainloop()
        if selected_mode is not None:
            TicTacToe(selected_mode, selected_difficulty).mainloop()


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
