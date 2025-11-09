import numpy as np
import csv
import os
from typing import List, Optional
from dataclasses import asdict
from .game import GameManager, GameStats

class TournamentManager:
    def __init__(self, num_games: int = 100, rows: int = 11, cols: int = 11, 
                 target: int = 10000, input_predefined: bool = False, 
                 input_file: Optional[str] = None):
        self.num_games = num_games
        self.rows = rows
        self.cols = cols
        self.target = target
        self.input_predefined = input_predefined
        self.input_file = input_file
        self.stats: List[GameStats] = []
    
    def load_predefined_board(self, game_id: int) -> Optional[np.ndarray]:
        """Load a predefined board from file if available."""
        if not self.input_predefined or not self.input_file:
            return None
            
        try:
            # Assuming the input file contains multiple boards separated by empty lines
            with open(self.input_file, 'r') as f:
                boards_data = f.read().strip().split('\n\n')
                if game_id < len(boards_data):
                    board_lines = boards_data[game_id].strip().split('\n')
                    board = np.array([
                        [int(x) for x in line.strip().split()]
                        for line in board_lines
                    ], dtype=np.int8)
                    if board.shape == (self.rows, self.cols):
                        return board
        except Exception as e:
            print(f"Error loading predefined board: {e}")
        return None
    
    def run_tournament(self) -> None:
        """Run all games in the tournament."""
        for game_id in range(self.num_games):
            board = self.load_predefined_board(game_id)
            game = GameManager(self.rows, self.cols, self.target, board)
            stats = game.play_game()
            stats.game_id = game_id
            self.stats.append(stats)
    
    def save_results(self, output_file: str) -> None:
        """Save tournament results to CSV file."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'game_id', 'points', 'swaps', 'total_cascades',
                'reached_target', 'stopping_reason', 'moves_to_10000'
            ])
            writer.writeheader()
            for stats in self.stats:
                writer.writerow(asdict(stats))
    
    def print_summary(self) -> None:
        """Print tournament summary statistics."""
        if not self.stats:
            print("No games played yet!")
            return
        
        total_points = sum(s.points for s in self.stats)
        total_swaps = sum(s.swaps for s in self.stats)
        games_reached_target = sum(1 for s in self.stats if s.reached_target)
        moves_to_target = [s.moves_to_10000 for s in self.stats if s.moves_to_10000 is not None]
        
        print("\nTournament Summary:")
        print(f"Total games played: {len(self.stats)}")
        print(f"Average points per game: {total_points / len(self.stats):.2f}")
        print(f"Average swaps per game: {total_swaps / len(self.stats):.2f}")
        print(f"Games reaching target ({self.target}): {games_reached_target}")
        if moves_to_target:
            print(f"Average moves to reach target: {sum(moves_to_target) / len(moves_to_target):.2f}")