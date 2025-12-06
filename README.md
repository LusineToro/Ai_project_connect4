Connect 4 AI Arena 🔴🟡A Python-based simulation environment for Connect 4, featuring a comparison of various Artificial Intelligence search algorithms. This project implements a game engine and allows different AI agents—ranging from greedy heuristics to advanced search trees—to compete against one another to determine the most effective strategy.📋 FeaturesGame Engine: Complete implementation of Connect 4 logic (6x7 grid), including valid move detection, win checking (horizontal, vertical, diagonal), and draw conditions.Heuristic Evaluation: A robust scoring function that evaluates board states based on:Threat Detection: Scores windows of 4 slots (e.g., 3-in-a-row with an empty slot).Center Bias: Prioritizes controlling the center column.Differential Scoring: Calculates (Player Score - Opponent Score).Multiple AI Agents:Hill Climbing (Greedy): Chooses the immediate best move based on static evaluation.Minimax with Alpha-Beta Pruning: Recursive search to a fixed depth with branch pruning for efficiency.Iterative Deepening Search (IDS): Time-bounded search that deepens the Minimax lookahead until a time limit is reached.Simulated Annealing: Probabilistic local search that avoids local optima by accepting worse moves with a decreasing probability (Temperature).Simulation Runner: Tools to run single verbose games (for debugging/watching) or batch simulations to gather win/loss statistics.🚀 InstallationThis project relies only on Python's standard libraries (math, random, time, sys). No external dependencies are required.Clone the repository:Bashgit clone https://github.com/your-username/connect4-ai-arena.git
cd connect4-ai-arena
Run the script:Bashpython connect4.py
🎮 Usage & ConfigurationThe simulation is configured in the __main__ block at the bottom of connect4.py. You can match any two algorithms against each other.Configuring AgentsModify the DEMO_AI_CONFIG dictionary to select agents for Player 1 (🔴) and Player 2 (🟡).Available Functions:hill_climbing_connect4minimax_connect4 (Requires depth param)iterative_deepening_connect4 (Requires max_time param)simulated_annealing_connect4Example: IDS vs. MinimaxPythonif __name__ == '__main__':
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
🧠 Algorithms Explained1. Hill Climbing (HC)Type: Local Search (Greedy).Logic: It looks only 1 ply (move) ahead. It generates all legal moves, evaluates the resulting board state, and picks the one with the highest immediate score.Pros/Cons: Extremely fast, but very short-sighted. It will miss traps set by opponents 2+ moves ahead.2. Minimax (Fixed Depth)Type: Adversarial Search.Logic: Builds a game tree to a specified depth. It assumes the opponent plays optimally (minimizing your score).Optimization: Uses Alpha-Beta Pruning to stop evaluating branches that cannot possibly influence the final decision, significantly speeding up the search.3. Iterative Deepening Search (IDS)Type: Time-Bounded Adversarial Search.Logic: This is the most robust agent for production. It runs Minimax at depth 1, then depth 2, then depth 3, etc.Constraint: It checks the clock after every depth iteration. If the max_time (e.g., 2 seconds) is almost up, it stops and returns the best move found at the deepest completed level. This ensures the AI never crashes due to taking too long.4. Simulated Annealing (SA)Type: Stochastic Local Search.Logic: Starts with a random move. It iteratively checks "neighbor" moves.If a neighbor is better, it switches to it.If a neighbor is worse, it might still switch to it based on a probability calculated by $P = e^{\Delta E / T}$.The "Temperature" ($T$) cools down over time, making the AI less likely to accept bad moves as the search progresses.Goal: To escape "local maxima" where a Hill Climber would get stuck.📊 Sample OutputWhen running the script, you will see a verbose output for the first game, followed by a statistical summary of the batch simulation.Plaintext--- Connect 4 Comparison Simulation ---
Player 1 (🔴) AI: SA (Local Search)
Player 2 (🟡) AI: Random

... (Game moves printed here) ...

######################################################################
      SIMULATION RESULTS: P1 (SA (Local Search)) vs P2 (Random)      
######################################################################
Total Games Played: 5
Total Time Taken: 0.15 seconds
Average Game Duration: 0.0305 seconds/game
----------------------------------------------------------------------
Player 1 (🔴) Wins: 5 (100.0%)
Player 2 (🟡) Wins: 0 (0.0%)
Draws:                     0 (0.0%)
######################################################################
