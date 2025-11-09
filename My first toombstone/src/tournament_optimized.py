from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from .game_optimized import GameManager, GameStats
from statistics import mean, median

@dataclass
class TournamentStats:
    games: List[GameStats]
    time_taken: float  # seconds
    avg_points: float
    median_points: float
    avg_swaps: float
    median_swaps: float
    success_rate: float  # percent of games reaching target
    avg_cascades: float
    median_cascades: float
    avg_moves_to_10000: Optional[float]
    median_moves_to_10000: Optional[float]

class TournamentManager:
    def __init__(self, num_games: int = 100, target: int = 10000, rows: int = 11, cols: int = 11):
        self.num_games = num_games
        self.target = target
        self.rows = rows
        self.cols = cols
        
    def _play_single_game(self, game_id: int) -> GameStats:
        """Play a single game in a separate process."""
        game = GameManager(rows=self.rows, cols=self.cols, target=self.target)
        stats = game.play_game()
        stats.game_id = game_id
        return stats
    
    def run_tournament(self) -> TournamentStats:
        """Run tournament using parallel processing."""
        # Use process pool for parallel execution
        with ProcessPoolExecutor() as executor:
            # Submit all games to the pool
            futures = [
                executor.submit(self._play_single_game, game_id)
                for game_id in range(self.num_games)
            ]
            
            # Collect results as they complete
            game_stats = []
            for future in futures:
                game_stats.append(future.result())
        
        # Calculate tournament statistics
        points = [stats.points for stats in game_stats]
        swaps = [stats.swaps for stats in game_stats]
        cascades = [stats.total_cascades for stats in game_stats]
        moves_to_10k = [stats.moves_to_10000 for stats in game_stats if stats.moves_to_10000]
        
        # Success rate calculation
        success_count = sum(1 for stats in game_stats if stats.reached_target)
        success_rate = (success_count / self.num_games) * 100
        
        # Handle case where no games reached 10,000 points
        avg_moves_to_10k = mean(moves_to_10k) if moves_to_10k else None
        median_moves_to_10k = median(moves_to_10k) if moves_to_10k else None
        
        return TournamentStats(
            games=game_stats,
            time_taken=0.0,  # Set by wrapper
            avg_points=mean(points),
            median_points=median(points),
            avg_swaps=mean(swaps),
            median_swaps=median(swaps),
            success_rate=success_rate,
            avg_cascades=mean(cascades),
            median_cascades=median(cascades),
            avg_moves_to_10000=avg_moves_to_10k,
            median_moves_to_10000=median_moves_to_10k
        )