from dataclasses import dataclass
from enum import Enum
import numpy as np
from typing import Optional, List, Tuple
from .board import Board

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
    
    def process_formations(self) -> int:
        """Process all formations and return the score earned."""
        score = 0
        while True:
            formations = self.board.find_all_formations()
            if not formations:
                break
                
            score += self.board.remove_formations(formations)
            self.board.apply_gravity()
            self.board.refill_board()
            self.total_cascades += 1
            
        return score
    
    def make_move(self, row1: int, col1: int, row2: int, col2: int) -> bool:
        """Attempt to make a move and return whether it was successful."""
        if self.board.try_swap(row1, col1, row2, col2):
            self.swaps += 1
            points = self.process_formations()
            self.score += points
            
            # Check if we've just crossed the 10000 point threshold
            if self.moves_to_10000 is None and self.score >= 10000:
                self.moves_to_10000 = self.swaps
                
            return True
        return False
    
    def find_best_move(self) -> Optional[Tuple[int, int, int, int]]:
        """Find the best possible move based on immediate score potential."""
        possible_moves = self.board.find_possible_moves()
        if not possible_moves:
            return None
            
        best_move = None
        best_score = -1
        # Use the board's local scoring estimator (much faster than full-board detection)
        for move in possible_moves:
            row1, col1, row2, col2 = move
            score = self.board.local_score_for_swap(row1, col1, row2, col2)
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def play_game(self) -> GameStats:
        """Play a complete game and return the statistics."""
        # Process any initial formations
        self.score = self.process_formations()
        
        while True:
            # Check winning condition
            if self.score >= self.target:
                return GameStats(
                    game_id=0,  # Will be set by the tournament manager
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
                    game_id=0,  # Will be set by the tournament manager
                    points=self.score,
                    swaps=self.swaps,
                    total_cascades=self.total_cascades,
                    reached_target=False,
                    stopping_reason=StoppingReason.NO_MOVES,
                    moves_to_10000=self.moves_to_10000
                )
            
            self.make_move(*best_move)