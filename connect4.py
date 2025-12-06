import math
import random
import time
import sys

# Increase recursion limit for deeper minimax/IDS searches
sys.setrecursionlimit(3000)


# --- ConnectFourBoard Class ---
class ConnectFourBoard:
    """
    Represents the Connect 4 board and handles game logic.
    """
    ROWS = 6
    COLS = 7
    EMPTY = 0
    PLAYER_1 = 1  # General identifier for player 1 (🔴)
    PLAYER_2 = 2  # General identifier for player 2 (🟡)

    def __init__(self, board=None):
        # Initialize an empty board or clone an existing one
        if board is None:
            self.grid = [[self.EMPTY] * self.COLS for _ in range(self.ROWS)]
        else:
            # Deep copy the grid to prevent state corruption
            self.grid = [row[:] for row in board]

    def is_valid_location(self, col):
        """Checks if a piece can be dropped in the given column."""
        return 0 <= col < self.COLS and self.grid[self.ROWS - 1][col] == self.EMPTY

    def get_next_open_row(self, col):
        """Finds the lowest empty row in a column."""
        for r in range(self.ROWS):
            if self.grid[r][col] == self.EMPTY:
                return r
        return -1

    def drop_piece(self, row, col, piece):
        """Places the piece on the board."""
        self.grid[row][col] = piece

    def check_win(self, piece):
        """Checks all directions for a 4-in-a-row for the given piece."""

        # 1. Check horizontal
        for c in range(self.COLS - 3):
            for r in range(self.ROWS):
                if all(self.grid[r][c + i] == piece for i in range(4)):
                    return True

        # 2. Check vertical
        for c in range(self.COLS):
            for r in range(self.ROWS - 3):
                if all(self.grid[r + i][c] == piece for i in range(4)):
                    return True

        # 3. Check positively sloped diagonals (bottom-left to top-right)
        for c in range(self.COLS - 3):
            for r in range(self.ROWS - 3):
                if all(self.grid[r + i][c + i] == piece for i in range(4)):
                    return True

        # 4. Check negatively sloped diagonals (top-left to bottom-right)
        for c in range(self.COLS - 3):
            for r in range(3, self.ROWS):
                if all(self.grid[r - i][c + i] == piece for i in range(4)):
                    return True

        return False

    def get_valid_moves(self):
        """Returns a list of columns where a piece can be dropped."""
        return [c for c in range(self.COLS) if self.is_valid_location(c)]

    def is_full(self):
        """Checks if the board is completely full (resulting in a draw)."""
        return not any(self.is_valid_location(c) for c in range(self.COLS))

    def __repr__(self):
        """Simple string representation for printing the board."""
        output = ""
        # Print top-down for readability
        for r in range(self.ROWS - 1, -1, -1):
            # Replace piece codes with symbols for better visual output
            row_str = ' | '.join(
                '🔴' if self.grid[r][c] == self.PLAYER_1 else
                '🟡' if self.grid[r][c] == self.PLAYER_2 else
                ' ' for c in range(self.COLS)
            )
            output += '| ' + row_str + ' |\n'

        output += '  ' + '---' * self.COLS + '\n'
        output += '  ' + '  '.join(str(c) for c in range(self.COLS)) + '\n'
        return output


# --- Heuristic Scoring (Evaluation Function) ---

def get_threat_score(window, piece):
    """Assigns a score to a 4-slot window based on potential for the given piece."""

    piece_count = window.count(piece)
    empty_count = window.count(ConnectFourBoard.EMPTY)

    # Use significantly weighted values for threats
    if piece_count == 4:
        return 100000000  # Immediate Win (Highest Priority)
    elif piece_count == 3 and empty_count == 1:
        return 100000  # Critical Threat
    elif piece_count == 2 and empty_count == 2:
        return 1000  # Medium Potential
    elif piece_count == 1 and empty_count == 3:
        return 10  # Minor Potential

    return 0


def calculate_energy(board_obj, player_piece):
    """
    Calculates the total board score (Energy) for the current player relative
    to the opponent using differential scoring: (Player Score - Opponent Score).
    This serves as the Heuristic/Evaluation Function for all AIs.
    A higher score is better for the current player.
    """

    opponent_piece = ConnectFourBoard.PLAYER_1 if player_piece == ConnectFourBoard.PLAYER_2 else ConnectFourBoard.PLAYER_2

    player_total_score = 0
    opponent_total_score = 0
    R = ConnectFourBoard.ROWS
    C = ConnectFourBoard.COLS

    # 1. Center Column Bias
    center_array = [board_obj.grid[r][C // 2] for r in range(R)]
    player_total_score += center_array.count(player_piece) * 5
    opponent_total_score += center_array.count(opponent_piece) * 5

    def score_all_windows(board, scorer_piece):
        score = 0
        # Horizontal, Vertical, and Diagonals

        # Horizontal
        for r in range(R):
            row_array = board[r]
            for c in range(C - 3):
                score += get_threat_score(row_array[c:c + 4], scorer_piece)

        # Vertical
        for c in range(C):
            col_array = [board[r][c] for r in range(R)]
            for r in range(R - 3):
                score += get_threat_score(col_array[r:r + 4], scorer_piece)

        # Positive Diagonals
        for r in range(R - 3):
            for c in range(C - 3):
                window = [board[r + i][c + i] for i in range(4)]
                score += get_threat_score(window, scorer_piece)

        # Negative Diagonals
        for r in range(3, R):
            for c in range(C - 3):
                window = [board[r - i][c + i] for i in range(4)]
                score += get_threat_score(window, scorer_piece)
        return score

    # Calculate scores for both sides
    player_total_score += score_all_windows(board_obj.grid, player_piece)
    opponent_total_score += score_all_windows(board_obj.grid, opponent_piece)

    # Differential Scoring: Maximize player's score relative to the opponent's
    return player_total_score - opponent_total_score


# --- AI Algorithm 1: Hill Climbing (HC) ---

def hill_climbing_connect4(initial_board, current_player, verbose=False, **kwargs):
    """
    Hill Climbing (Greedy Search): Selects the move that leads to the highest
    immediate static board score for the current player.
    """
    start_time = time.time()

    valid_moves = initial_board.get_valid_moves()
    if not valid_moves:
        return -1

    best_move = valid_moves[0]
    best_energy = -math.inf

    # Check all possible next states (neighbors)
    for col in valid_moves:
        temp_board = ConnectFourBoard(initial_board.grid)
        row = temp_board.get_next_open_row(col)
        temp_board.drop_piece(row, col, current_player)

        current_energy = calculate_energy(temp_board, current_player)

        if current_energy > best_energy:
            best_energy = current_energy
            best_move = col

    end_time = time.time()

    if verbose:
        print(f"  HC decided on column {best_move} (Energy: {best_energy}) in {end_time - start_time:.6f}s")

    return best_move


# --- AI Algorithm 2: Minimax Core (Used by IDS) ---

def is_terminal_node(board, current_player, opponent_player):
    """Checks if the game is won, lost, or drawn."""
    return board.check_win(current_player) or board.check_win(opponent_player) or board.is_full()


def minimax(board, depth, alpha, beta, maximizing_player_piece, original_player_piece):
    """
    Minimax function with Alpha-Beta Pruning.
    Returns (best_column, best_score)
    """

    valid_moves = board.get_valid_moves()
    is_terminal = is_terminal_node(board, ConnectFourBoard.PLAYER_1, ConnectFourBoard.PLAYER_2)

    if depth == 0 or is_terminal:
        if is_terminal:
            # Assign extremely high/low scores for terminal states to force win/loss
            if board.check_win(original_player_piece):
                return (None, 1000000000000)
            elif board.check_win(
                    ConnectFourBoard.PLAYER_1 if original_player_piece == ConnectFourBoard.PLAYER_2 else ConnectFourBoard.PLAYER_2):
                return (None, -1000000000000)
            else:  # Game is a draw
                return (None, 0)
        else:  # Depth is zero, use the heuristic score
            return (None, calculate_energy(board, original_player_piece))

    is_maximizing = (maximizing_player_piece == original_player_piece)

    if is_maximizing:
        value = -math.inf
        best_col = valid_moves[0] if valid_moves else -1

        for col in valid_moves:
            temp_board = ConnectFourBoard(board.grid)
            row = temp_board.get_next_open_row(col)
            temp_board.drop_piece(row, col, maximizing_player_piece)

            next_player = ConnectFourBoard.PLAYER_1 if maximizing_player_piece == ConnectFourBoard.PLAYER_2 else ConnectFourBoard.PLAYER_2

            # Recursive call
            new_score = minimax(temp_board, depth - 1, alpha, beta, next_player, original_player_piece)[1]

            if new_score > value:
                value = new_score
                best_col = col

            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value

    else:  # Minimizing player
        value = math.inf
        best_col = valid_moves[0] if valid_moves else -1

        for col in valid_moves:
            temp_board = ConnectFourBoard(board.grid)
            row = temp_board.get_next_open_row(col)
            temp_board.drop_piece(row, col, maximizing_player_piece)

            next_player = original_player_piece  # Next turn is the maximizer

            # Recursive call
            new_score = minimax(temp_board, depth - 1, alpha, beta, next_player, original_player_piece)[1]

            if new_score < value:
                value = new_score
                best_col = col

            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value


# --- AI Algorithm 3: Pure Minimax (Wrapper for fixed depth) ---

def minimax_connect4(initial_board, current_player, depth=5, verbose=False, **kwargs):
    """
    Wrapper for Minimax with Alpha-Beta Pruning, run to a fixed depth limit.
    """
    start_time = time.time()

    best_col, best_score = minimax(
        board=initial_board,
        depth=depth,
        alpha=-math.inf,
        beta=math.inf,
        maximizing_player_piece=current_player,
        original_player_piece=current_player
    )

    end_time = time.time()

    if verbose:
        print(
            f"  Minimax (D={depth}) decided on column {best_col} (Score: {best_score}) in {end_time - start_time:.6f}s")

    return best_col


# --- AI Algorithm 4: Iterative Deepening Search (IDS) ---

def iterative_deepening_connect4(initial_board, current_player, max_time=2.0, verbose=False, **kwargs):
    """
    Iterative Deepening Search using Minimax: Increases search depth until the
    time limit is exceeded. Returns the best move found at the deepest completed depth.
    """

    start_time = time.time()

    valid_moves = initial_board.get_valid_moves()
    if not valid_moves:
        return -1

    best_move_at_deepest_level = valid_moves[0]
    current_depth = 1

    while True:
        time_elapsed = time.time() - start_time
        # Use a buffer to safely stop before the time limit hits
        if time_elapsed + 0.1 > max_time:
            if verbose:
                print(f"  IDS Time limit reached ({time_elapsed:.2f}s). Stopping search.")
            break

        # Check if we're near the maximum recursion depth for stability
        if current_depth > 12:
            if verbose:
                print(f"  IDS Stopping at depth {current_depth} to prevent excessive recursion.")
            break

        try:
            # Run Minimax at the current depth
            depth_start_time = time.time()
            best_col, best_score = minimax(
                board=initial_board,
                depth=current_depth,
                alpha=-math.inf,
                beta=math.inf,
                maximizing_player_piece=current_player,
                original_player_piece=current_player
            )
            depth_time = time.time() - depth_start_time

            # If the search completed within the time limit, store the result
            best_move_at_deepest_level = best_col

            if verbose:
                print(
                    f"  IDS completed Depth {current_depth} (Move: {best_col}, Score: {best_score}) in {depth_time:.3f}s. Total time: {time.time() - start_time:.2f}s")

            # Increment depth for the next iteration
            current_depth += 1

        except Exception as e:
            # Catches unexpected errors or forced termination
            if verbose:
                print(f"  IDS stopped unexpectedly at depth {current_depth}. Error: {e}")
            break

    total_time = time.time() - start_time
    if verbose:
        print(f"  IDS final move: Column {best_move_at_deepest_level}. Total thinking time: {total_time:.3f}s")

    return best_move_at_deepest_level


# --- AI Algorithm 5: Simulated Annealing (SA) ---

def simulated_annealing_connect4(initial_board, current_player, initial_temp=100.0, cooling_rate=0.99, iterations=500,
                                 verbose=False, **kwargs):
    """
    Simulated Annealing: Uses a random walk that accepts worse states
    (lower energy) with a probability that decreases over time (temperature).
    """

    start_time = time.time()

    valid_moves = initial_board.get_valid_moves()
    if not valid_moves:
        return -1

    # Start with a random valid move
    current_move_col = random.choice(valid_moves)

    def get_board_after_move(board, col, piece):
        """Helper to return the new board state after a move."""
        temp_board = ConnectFourBoard(board.grid)
        row = temp_board.get_next_open_row(col)
        if row != -1:
            temp_board.drop_piece(row, col, piece)
        return temp_board

    # Calculate initial energy
    current_board = get_board_after_move(initial_board, current_move_col, current_player)
    current_energy = calculate_energy(current_board, current_player)

    best_move_col = current_move_col
    best_energy = current_energy

    temperature = initial_temp

    for i in range(iterations):
        if temperature < 1e-4:  # Cooling stop condition
            break

            # 1. Select a random neighbor (a different valid move)
        neighbor_move_col = random.choice(valid_moves)
        neighbor_board = get_board_after_move(initial_board, neighbor_move_col, current_player)
        neighbor_energy = calculate_energy(neighbor_board, current_player)

        # 2. Check if the neighbor is better
        energy_change = neighbor_energy - current_energy

        if energy_change > 0:
            # Accept better move
            current_move_col = neighbor_move_col
            current_energy = neighbor_energy
        else:
            # Accept worse move with probability P
            acceptance_probability = math.exp(energy_change / temperature)
            if random.random() < acceptance_probability:
                current_move_col = neighbor_move_col
                current_energy = neighbor_energy

        # 3. Update the best recorded move
        if current_energy > best_energy:
            best_energy = current_energy
            best_move_col = current_move_col

        # 4. Cool down the temperature
        temperature *= cooling_rate

    end_time = time.time()

    if verbose:
        print(
            f"  SA decided on column {best_move_col} (Energy: {best_energy}) in {end_time - start_time:.6f}s (Iters: {i + 1})")

    return best_move_col


# --- Game Loop Functions ---

# Mapping of AI function to a readable name for printouts
AI_NAMES = {
    hill_climbing_connect4: 'HC (Greedy)',
    minimax_connect4: 'Minimax (Fixed Depth)',
    iterative_deepening_connect4: 'IDS (Time-bound)',
    simulated_annealing_connect4: 'SA (Local Search)'
}


def run_single_game(AI_CONFIG, verbose=False):
    """
    Runs one full game between two AIs using configurations from AI_CONFIG.
    Returns: (duration, winner_piece) where winner_piece is 1, 2, or 0 (for draw).
    """

    game = ConnectFourBoard()
    current_player = ConnectFourBoard.PLAYER_1
    game_over = False
    turn_count = 0
    winner = 0  # 0 for draw, 1 or 2 for winner

    start_game_time = time.time()

    # Helper to get the AI name (now dynamic based on the function)
    def get_ai_name(piece):
        func = AI_CONFIG[piece]['function']
        name = AI_NAMES.get(func, func.__name__)

        # Add depth/time detail if available
        if 'depth' in AI_CONFIG[piece]:
            name += f" D={AI_CONFIG[piece]['depth']}"
        elif 'max_time' in AI_CONFIG[piece]:
            name += f" T={AI_CONFIG[piece]['max_time']}s"

        return name

    if verbose:
        print("--- Connect 4 Comparison Simulation ---")
        print(f"Player 1 (🔴) AI: {get_ai_name(ConnectFourBoard.PLAYER_1)}")
        print(f"Player 2 (🟡) AI: {get_ai_name(ConnectFourBoard.PLAYER_2)}")
        print("\nInitial Board:")
        print(game)

    while not game_over:
        turn_count += 1
        piece = current_player
        player_char = '🔴' if piece == ConnectFourBoard.PLAYER_1 else '🟡'

        config = AI_CONFIG[piece]
        ai_function = config['function']
        ai_name = get_ai_name(piece)

        # Filter the config to only include valid parameters for the AI function
        params_to_pass = {k: v for k, v in config.items() if k != 'function'}

        if verbose:
            print(f"\n======================================")
            print(f"TURN {turn_count}: Player {piece} ({player_char}) using {ai_name}")
            print(f"======================================")

        # Get the move from the respective AI, passing only relevant keyword arguments
        start_move_time = time.time()
        move_col = ai_function(game, piece, verbose=verbose, **params_to_pass)
        end_move_time = time.time()

        if verbose:
            print(f"  Move execution complete in {end_move_time - start_move_time:.3f} seconds")

        if move_col == -1:
            if verbose: print("No valid moves. It's a DRAW!")
            game_over = True
            break

        # Execute the move
        row = game.get_next_open_row(move_col)
        game.drop_piece(row, move_col, piece)

        if verbose:
            print(f"\nBoard after Player {piece}'s move (Column {move_col}):")
            print(game)

        # Check for termination conditions
        if game.check_win(piece):
            winner = piece
            if verbose: print(f"--- GAME OVER: Player {piece} ({player_char}) WINS! ({ai_name}) ---")
            game_over = True
        elif game.is_full():
            winner = 0  # Draw
            if verbose: print("--- GAME OVER: The board is full. It's a DRAW! ---")
            game_over = True

        # Switch turn
        if not game_over:
            current_player = ConnectFourBoard.PLAYER_1 if current_player == ConnectFourBoard.PLAYER_2 else ConnectFourBoard.PLAYER_2

    end_game_time = time.time()
    return end_game_time - start_game_time, winner


def run_multiple_simulations(n_simulations=10, AI_CONFIG=None):
    """Runs N games, tracks time, and prints statistics for the configured AIs."""

    # Default configuration: HC vs IDS, as requested by the user
    if AI_CONFIG is None:
        AI_CONFIG = {
            ConnectFourBoard.PLAYER_1: {'function': hill_climbing_connect4},
            ConnectFourBoard.PLAYER_2: {'function': iterative_deepening_connect4, 'max_time': 2.0}
        }

    p1_name = AI_NAMES.get(AI_CONFIG[1]['function'])
    p2_name = AI_NAMES.get(AI_CONFIG[2]['function'])

    total_duration = 0
    win_counts = {1: 0, 2: 0, 0: 0}  # 0 for draw

    print("\n" + "=" * 70)
    print(f"Starting {n_simulations} AI Comparison Simulations")
    print(f"P1 (🔴): {p1_name} | P2 (🟡): {p2_name}")
    print("=" * 70)

    start_time = time.time()

    for i in range(1, n_simulations + 1):
        # Run in silent mode (verbose=False)
        duration, winner = run_single_game(AI_CONFIG, verbose=False)

        total_duration += duration
        win_counts[winner] += 1

        if i % 1 == 0:
            print(f"Completed {i}/{n_simulations} games. Game Time: {duration:.2f}s")

    end_time = time.time()

    # Calculate statistics
    average_duration = total_duration / n_simulations
    total_elapsed = end_time - start_time

    # Print results
    print("\n" + "#" * 70)
    print(f"      SIMULATION RESULTS: P1 ({p1_name}) vs P2 ({p2_name})      ")
    print("#" * 70)
    print(f"Total Games Played: {n_simulations}")
    print(f"Total Time Taken: {total_elapsed:.2f} seconds")
    print(f"Average Game Duration: {average_duration:.4f} seconds/game")
    print("-" * 70)
    print(f"Player 1 (🔴) Wins: {win_counts[1]} ({win_counts[1] / n_simulations:.1%})")
    print(f"Player 2 (🟡) Wins: {win_counts[2]} ({win_counts[2] / n_simulations:.1%})")
    print(f"Draws:                     {win_counts[0]} ({win_counts[0] / n_simulations:.1%})")
    print("#" * 70)


# Execute the game loop
if __name__ == '__main__':
    # Configuration for the verbose demo run (HC vs IDS, as requested)
    DEMO_AI_CONFIG = {
        ConnectFourBoard.PLAYER_1: {'function': simulated_annealing_connect4},
        ConnectFourBoard.PLAYER_2: {'function': random}
    }

    print("--- DEMO RUN: Showing a single IDS vs IDS game in verbose mode ---")
    run_single_game(DEMO_AI_CONFIG, verbose=True)

    # Run the comparison simulation (N=10)
    run_multiple_simulations(n_simulations=5, AI_CONFIG=DEMO_AI_CONFIG)