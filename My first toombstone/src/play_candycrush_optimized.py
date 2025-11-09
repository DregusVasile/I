from __future__ import annotations
import time
from src.tournament_optimized import TournamentManager, TournamentStats

def run_tournament(num_games: int = 100, target: int = 10000) -> TournamentStats:
    """Run a tournament with timing measurement."""
    tournament = TournamentManager(num_games=num_games, target=target)
    
    # Time the tournament
    start_time = time.perf_counter()
    stats = tournament.run_tournament()
    end_time = time.perf_counter()
    
    # Add timing information
    stats.time_taken = end_time - start_time
    return stats
    
if __name__ == "__main__":
    stats = run_tournament()
    print(f"\nTournament Results:")
    print(f"Time taken: {stats.time_taken:.2f} seconds")
    print(f"Games played: {len(stats.games)}")
    print(f"Average points: {stats.avg_points:.1f}")
    print(f"Median points: {stats.median_points:.1f}")
    print(f"Success rate: {stats.success_rate:.1f}%")
    print(f"Average moves to 10k: {stats.avg_moves_to_10000:.1f}" if stats.avg_moves_to_10000 else "No games reached 10k")