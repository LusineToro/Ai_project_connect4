# Connect 4 AI Arena 🔴🟡

A Python-based simulation environment for **Connect 4**, featuring a comparison of various Artificial Intelligence search algorithms. This project implements a game engine and allows different AI agents—ranging from greedy heuristics to advanced search trees—to compete against one another to determine the most effective strategy.

## 📋 Features

* **Game Engine:** Complete implementation of Connect 4 logic (6x7 grid), including valid move detection, win checking (horizontal, vertical, diagonal), and draw conditions.
* **Heuristic Evaluation:** A robust scoring function that evaluates board states based on:
    * **Threat Detection:** Scores windows of 4 slots (e.g., 3-in-a-row with an empty slot).
    * **Center Bias:** Prioritizes controlling the center column.
    * **Differential Scoring:** Calculates `(Player Score - Opponent Score)`.
* **Multiple AI Agents:**
    1.  **Hill Climbing (Greedy):** Chooses the immediate best move based on static evaluation.
    2.  **Minimax with Alpha-Beta Pruning:** Recursive search to a fixed depth with branch pruning for efficiency.
    3.  **Iterative Deepening Search (IDS):** Time-bounded search that deepens the Minimax lookahead until a time limit is reached.
    4.  **Simulated Annealing:** Probabilistic local search that avoids local optima by accepting worse moves with a decreasing probability (Temperature).
* **Simulation Runner:** Tools to run single verbose games (for debugging/watching) or batch simulations to gather win/loss statistics.

## 🚀 Installation

This project relies only on Python's standard libraries (`math`, `random`, `time`, `sys`). No external dependencies are required.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/connect4-ai-arena.git](https://github.com/your-username/connect4-ai-arena.git)
    cd connect4-ai-arena
    ```

2.  **Run the script:**
    ```bash
    python connect4.py
    ```

## 🎮 Usage & Configuration

The simulation is configured in the `__main__` block at the bottom of `connect4.py`. You can match any two algorithms against each other.

### Configuring Agents
Modify the `DEMO_AI_CONFIG` dictionary to select agents for Player 1 (🔴) and Player 2 (🟡).

**Available Functions:**
* `hill_climbing_connect4`
* `minimax_connect4` (Requires `depth` param)
* `iterative_deepening_connect4` (Requires `max_time` param)
* `simulated_annealing_connect4`

**Example: IDS vs. Minimax**
```python
if __name__ == '__main__':
    DEMO_AI_CONFIG = {
        ConnectFourBoard.PLAYER_1: {
            'function': iterative_deepening_connect4, 
            'max_time': 2.0  # Search for 2 seconds per turn
        },
        ConnectFourBoard.PLAYER_2: {
            'function': minimax_connect4, 
            'depth': 4       # Look 4 moves ahead
        }
    }
    
    # Run 100 simulations
    run_multiple_simulations(n_simulations=100, AI_CONFIG=DEMO_AI_CONFIG)
