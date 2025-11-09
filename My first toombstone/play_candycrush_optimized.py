import argparse
from src.tournament_optimized import TournamentManager
import time

def main():
    parser = argparse.ArgumentParser(description='Play Candy Crush automation games')
    parser.add_argument('--games', type=int, default=100,
                      help='Number of games to play (default: 100)')
    parser.add_argument('--rows', type=int, default=11,
                      help='Number of rows in the grid (default: 11)')
    parser.add_argument('--cols', type=int, default=11,
                      help='Number of columns in the grid (default: 11)')
    parser.add_argument('--target', type=int, default=10000,
                      help='Target score to reach (default: 10000)')
    parser.add_argument('--input_predefined', action='store_true',
                      help='Load predefined boards from --input_file when present')
    parser.add_argument('--input_file', type=str,
                      help='File containing predefined boards')
    parser.add_argument('--out', type=str, default='results/summary.csv',
                      help='Output CSV file path (default: results/summary.csv)')
    
    args = parser.parse_args()
    
    # Create and run tournament with timing
    start_time = time.time()
    
    tournament = TournamentManager(
        num_games=args.games,
        rows=args.rows,
        cols=args.cols,
        target=args.target,
        input_predefined=args.input_predefined,
        input_file=args.input_file
    )
    
    tournament.run_tournament()
    tournament.save_results(args.out)
    tournament.print_summary()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\nPerformance Summary:")
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"Average time per game: {total_time / args.games:.2f} seconds")

if __name__ == '__main__':
    main()