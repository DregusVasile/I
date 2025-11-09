# Candy Crush Automation Project

This project implements an automated player for a Candy Crush style match-3 game on an 11×11 grid.

## Requirements

- Python 3.7 or higher
- NumPy 1.21.0 or higher

Install dependencies:
```bash
pip install -r requirements.txt
```

## Game Rules

- Board: 11×11 grid
- Colors: Red (1), Yellow (2), Green (3), Blue (4), Empty (0)
- Formations:
  - Line of 3: 5 points
  - Line of 4: 10 points
  - Line of 5: 50 points
  - L shape (3+3): 20 points
  - T shape (3+3+3): 30 points

## Usage

Run the game with default settings (100 games, 11×11 grid, target score 10000):
```bash
python play_candycrush.py
```

Run with custom parameters (PowerShell-friendly example):
```powershell
& "C:/Users/asus/Desktop/My first toombstone/.venv/Scripts/python.exe" play_candycrush.py `
  --games 100 `
  --rows 11 `
  --cols 11 `
  --target 10000 `
  --input_predefined `
  --input_file data/predefined_boards.txt `
  --out results/summary.csv
```

### Parameters

- `--games`: Number of games to play (default: 100)
- `--rows`: Number of rows in the grid (default: 11)
- `--cols`: Number of columns in the grid (default: 11)
- `--target`: Target score to reach (default: 10000)
-- `--input_predefined`: If present, load predefined boards from `--input_file` (flag; default: False)
- `--input_file`: File containing predefined boards
- `--out`: Output CSV file path (default: results/summary.csv)

## Output Format

The program generates a CSV file with the following columns:

- `game_id`: Game number (0-based)
- `points`: Total points scored
- `swaps`: Number of moves made
- `total_cascades`: Number of cascade events
- `reached_target`: Whether the target score was reached (True/False)
- `stopping_reason`: Why the game ended (REACHED_TARGET or NO_MOVES)
- `moves_to_10000`: Number of moves to reach 10000 points (if achieved)

## Game Mechanics

### Swap Definition
A swap is a single move that exchanges two adjacent candies (orthogonally, not diagonally). A swap is only valid if it creates at least one valid formation. Invalid swaps are reverted and don't count towards the total swaps.

### Score Calculation
- Each cell can only contribute to one formation per cascade
- When multiple formations overlap, priority is given to higher-scoring formations
- Cascades occur automatically after formations are cleared

### Strategy
The current implementation uses a greedy approach:
1. Identifies all possible valid swaps
2. Evaluates the immediate score potential of each swap
3. Chooses the swap that yields the highest immediate score

## Project Structure

```
/
├── src/
│   ├── __init__.py
│   ├── board.py       # Board representation and mechanics
│   ├── game.py        # Game logic and state management
│   └── tournament.py  # Multi-game management and statistics
├── tests/            # Unit tests
├── results/          # Output CSV files
├── docs/            # Documentation
├── data/            # Predefined board configurations
├── play_candycrush.py  # Main entry point
├── requirements.txt  # Dependencies
└── README.md        # This file
```