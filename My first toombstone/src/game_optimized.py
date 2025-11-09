from dataclasses import dataclass
from enum import Enum
import numpy as np
from typing import Optional, List, Tuple, Dict
from .board_optimized import Board

class StoppingReason(str, Enum):
    REACHED_TARGET = "REACHED_TARGET"
    NO_MOVES = "NO_MOVES"

@dataclass
class GameStats:
    game_id: int
    points: int
    swaps: int
    total_cascades: int
    reached_target: bool
    stopping_reason: StoppingReason
    moves_to_10000: Optional[int]

class GameManager:
    def __init__(self, rows: int = 11, cols: int = 11, target: int = 10000, predefined_board: Optional[np.ndarray] = None):
        self.rows = rows
        self.cols = cols
        self.target = target
        self.board = Board(rows, cols, predefined_board)
        self.score = 0
        self.swaps = 0
        self.total_cascades = 0
        self.moves_to_10000 = None
        
        # Cache to avoid move repetition
        self.move_history: Dict[Tuple[int, int, int, int], int] = {}
    
    def process_formations(self) -> int:
        """Process formations in batches for better performance."""
        score = 0
        
        # Process formations in batches for better performance
        formations = self.board.find_all_formations()
        while formations:
            batch_score = self.board.remove_formations(formations)
            self.board.apply_gravity()
            self.board.refill_board()
            score += batch_score
            self.total_cascades += 1
            formations = self.board.find_all_formations()
            
            # Early exit if no valid formations
            if not formations:
                break
                
        return score
    
    def make_move(self, row1: int, col1: int, row2: int, col2: int) -> bool:
        """Attempt move with cascade processing."""
        # Skip invalid moves
        if not self.board.try_swap(row1, col1, row2, col2):
            return False
            
        # Move was valid
        self.swaps += 1
        move = (row1, col1, row2, col2)
        self.move_history[move] = self.move_history.get(move, 0) + 1
        
        # Process formations and cascades
        points = self.process_formations()
        self.score += points
        
        # Check 10k milestone
        if self.moves_to_10000 is None and self.score >= 10000:
            self.moves_to_10000 = self.swaps
            
        return True
    
    def find_best_move(self) -> Optional[Tuple[int, int, int, int]]:
        """Find best move using move history and fast local scoring."""
        possible_moves = self.board.find_possible_moves()
        if not possible_moves:
            return None
            
        # Score moves with history consideration
        scored_moves = []
        for move in possible_moves:
            row1, col1, row2, col2 = move
            base_score = self.board.local_score_for_swap(row1, col1, row2, col2)
            
            # Penalize repeated moves
            if move in self.move_history:
                base_score *= 0.8  # 20% penalty for repeated moves
                
            # Bonus for moves that could create cascades
            cascade_potential = self._estimate_cascade_potential(row1, col1, row2, col2)
            total_score = base_score * (1 + 0.2 * cascade_potential)  # Up to 20% bonus
            
            scored_moves.append((move, total_score))
            
        # Sort by score and take best
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        
        if scored_moves:
            best_move = scored_moves[0][0]
            # Update history
            self.move_history[best_move] = self.move_history.get(best_move, 0) + 1
            return best_move
            
        return None
        
    def _estimate_cascade_potential(self, row1: int, col1: int, row2: int, col2: int) -> float:
        """Estimate likelihood of cascades after a move."""
        # Look for almost-complete formations above the affected cells
        potential = 0.0
        
        for row, col in [(row1, col1), (row2, col2)]:
            # Check vertical potential (cells above that might fall)
            if row > 0:
                for r in range(max(0, row-3), row):
                    # Two same colors with one gap could form a line
                    window = self.board.grid[r:r+3, col]
                    if len(window) >= 3:
                        values, counts = np.unique(window, return_counts=True)
                        if len(values) == 2 and Color.EMPTY in values:
                            color_count = counts[values != Color.EMPTY][0]
                            if color_count == 2:
                                potential += 0.5  # Potential line of 3
                                
            # Check horizontal potential
            window = self.board.grid[row, max(0, col-2):col+3]
            if len(window) >= 3:
                values, counts = np.unique(window, return_counts=True)
                if len(values) == 2 and Color.EMPTY in values:
                    color_count = counts[values != Color.EMPTY][0]
                    if color_count == 2:
                        potential += 0.5  # Potential line of 3
                        
        return min(potential, 2.0)  # Cap at 200% bonus
    
    def play_game(self) -> GameStats:
        """Play a complete game with optimized move selection."""
        # Process any initial formations
        self.score = self.process_formations()
        
        # Clear move history for fresh game
        self.move_history.clear()
        
        while True:
            # Early exit check
            if self.score >= self.target:
                return GameStats(
                    game_id=0,  # Will be set by tournament manager
                    points=self.score,
                    swaps=self.swaps,
                    total_cascades=self.total_cascades,
                    reached_target=True,
                    stopping_reason=StoppingReason.REACHED_TARGET,
                    moves_to_10000=self.moves_to_10000
                )
            
            # Find and make best move
            best_move = self.find_best_move()
            if best_move is None:
                return GameStats(
                    game_id=0,  # Will be set by tournament manager
                    points=self.score,
                    swaps=self.swaps,
                    total_cascades=self.total_cascades,
                    reached_target=False,
                    stopping_reason=StoppingReason.NO_MOVES,
                    moves_to_10000=self.moves_to_10000
                )
            
            self.make_move(*best_move)