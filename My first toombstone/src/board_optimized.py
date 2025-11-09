from __future__ import annotations
from enum import IntEnum
import numpy as np
from typing import List, Tuple, Set, Optional

class Color(IntEnum):
    """Enum for candy colors."""
    EMPTY = 0  # Used for empty cells
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    ORANGE = 5
    PURPLE = 6

class Board:
    """Optimized board class using NumPy operations."""
    def __init__(self, rows: int = 11, cols: int = 11, predefined_board: Optional[np.ndarray] = None):
        self.rows = rows
        self.cols = cols
        
        if predefined_board is not None:
            self.grid = predefined_board.copy()
        else:
            self.grid = np.random.randint(1, 7, size=(rows, cols), dtype=np.int8)
            
            # Clear any initial formations
            while self.find_all_formations():
                self.refill_board()
                
        # Pre-compute pattern matrices for L and T shapes
        self._init_pattern_matrices()
        
    def _init_pattern_matrices(self):
        """Initialize pattern matrices for formation detection."""
        # L-shape patterns (horizontal base)
        self.l_patterns_h = np.array([
            [[1, 1, 1],  # Base
             [1, 0, 0]], # Vertical part
             
            [[1, 1, 1],
             [0, 0, 1]],
             
            [[1, 1, 1],
             [0, 1, 0]]
        ], dtype=bool)
        
        # L-shape patterns (vertical base)
        self.l_patterns_v = np.array([
            [[1, 1],     # Vertical part with horizontal extension
             [1, 0],
             [1, 0]],
             
            [[1, 0],
             [1, 0],
             [1, 1]],
             
            [[0, 1],
             [1, 1],
             [0, 1]]
        ], dtype=bool)
        
    def is_valid_pos(self, row: int, col: int) -> bool:
        """Check if position is within grid bounds."""
        return 0 <= row < self.rows and 0 <= col < self.cols
        
    def try_swap(self, row1: int, col1: int, row2: int, col2: int) -> bool:
        """Attempt to swap two cells."""
        # Validate positions
        if not (self.is_valid_pos(row1, col1) and self.is_valid_pos(row2, col2)):
            return False
            
        # Only allow adjacent swaps
        if abs(row1 - row2) + abs(col1 - col2) != 1:
            return False
            
        # Temporarily swap
        self.grid[row1, col1], self.grid[row2, col2] = \
            self.grid[row2, col2], self.grid[row1, col1]
            
        # Check if swap creates any formations
        formations = self.find_all_formations()
        
        if not formations:
            # Revert invalid swap
            self.grid[row1, col1], self.grid[row2, col2] = \
                self.grid[row2, col2], self.grid[row1, col1]
            return False
            
        return True
        
    def find_horizontal_lines(self) -> Set[Tuple[int, int]]:
        """Find horizontal lines of 3 or more using NumPy operations."""
        cells = set()
        
        # Use rolling window approach
        for row in range(self.rows):
            # Get current row
            current_row = self.grid[row]
            
            # Find runs of same color
            change_points = np.where(current_row[1:] != current_row[:-1])[0] + 1
            run_starts = np.r_[0, change_points]
            run_ends = np.r_[change_points, len(current_row)]
            
            # Check each run
            for start, end in zip(run_starts, run_ends):
                if end - start >= 3 and current_row[start] != Color.EMPTY:
                    # Add all cells in the run
                    cells.update((row, col) for col in range(start, end))
                    
        return cells
        
    def find_vertical_lines(self) -> Set[Tuple[int, int]]:
        """Find vertical lines of 3 or more using NumPy operations."""
        # Transpose grid and use horizontal line detection
        transposed = self.grid.T
        cells = set()
        
        for col in range(self.cols):
            current_col = transposed[col]
            
            change_points = np.where(current_col[1:] != current_col[:-1])[0] + 1
            run_starts = np.r_[0, change_points]
            run_ends = np.r_[change_points, len(current_col)]
            
            for start, end in zip(run_starts, run_ends):
                if end - start >= 3 and current_col[start] != Color.EMPTY:
                    cells.update((row, col) for row in range(start, end))
                    
        return cells
        
    def find_l_shapes(self) -> Set[Tuple[int, int]]:
        """Find L-shaped formations using pre-computed patterns."""
        cells = set()
        
        # Scan for each color
        for color in range(1, 7):  # Skip EMPTY
            color_mask = (self.grid == color)
            
            # Check horizontal base L patterns
            for pattern in self.l_patterns_h:
                for i in range(self.rows - 1):
                    for j in range(self.cols - 2):
                        window = color_mask[i:i+2, j:j+3]
                        if window.shape == pattern.shape and np.all(window == pattern):
                            cells.update((r + i, c + j) 
                                      for r, c in zip(*np.where(pattern)))
                            
            # Check vertical base L patterns
            for pattern in self.l_patterns_v:
                for i in range(self.rows - 2):
                    for j in range(self.cols - 1):
                        window = color_mask[i:i+3, j:j+2]
                        if window.shape == pattern.shape and np.all(window == pattern):
                            cells.update((r + i, c + j) 
                                      for r, c in zip(*np.where(pattern)))
                            
        return cells
        
    def find_all_formations(self) -> Set[Tuple[int, int]]:
        """Find all valid formations on the board."""
        formations = set()
        
        # Collect cells from different formation types
        formations.update(self.find_horizontal_lines())
        formations.update(self.find_vertical_lines())
        formations.update(self.find_l_shapes())
        
        return formations
        
    def remove_formations(self, formations: Set[Tuple[int, int]]) -> int:
        """Remove formations and return points earned."""
        if not formations:
            return 0
            
        # Set cells to empty
        for row, col in formations:
            self.grid[row, col] = Color.EMPTY
            
        return len(formations) * 100
        
    def apply_gravity(self):
        """Apply gravity to make candies fall."""
        # Process each column
        for col in range(self.cols):
            # Find non-empty cells in column
            column = self.grid[:, col]
            non_empty = column[column != Color.EMPTY]
            
            # Pad with empty cells at top
            new_column = np.pad(
                non_empty,
                (self.rows - len(non_empty), 0),
                mode='constant',
                constant_values=Color.EMPTY
            )
            
            # Update column
            self.grid[:, col] = new_column
            
    def refill_board(self):
        """Fill empty cells with random new candies."""
        empty_mask = (self.grid == Color.EMPTY)
        num_empty = np.sum(empty_mask)
        
        if num_empty > 0:
            # Generate random colors for empty cells
            new_colors = np.random.randint(1, 7, size=num_empty, dtype=np.int8)
            self.grid[empty_mask] = new_colors
            
    def find_possible_moves(self) -> List[Tuple[int, int, int, int]]:
        """Find all possible moves that would create formations."""
        moves = []
        
        # Check horizontal swaps
        for row in range(self.rows):
            for col in range(self.cols - 1):
                # Try swap
                self.grid[row, [col, col+1]] = self.grid[row, [col+1, col]]
                
                # Keep if creates formation
                if self.find_all_formations():
                    moves.append((row, col, row, col+1))
                    
                # Revert swap
                self.grid[row, [col, col+1]] = self.grid[row, [col+1, col]]
                
        # Check vertical swaps
        for row in range(self.rows - 1):
            for col in range(self.cols):
                # Try swap
                self.grid[[row, row+1], col] = self.grid[[row+1, row], col]
                
                # Keep if creates formation
                if self.find_all_formations():
                    moves.append((row, col, row+1, col))
                    
                # Revert swap
                self.grid[[row, row+1], col] = self.grid[[row+1, row], col]
                
        return moves
        
    def local_score_for_swap(self, row1: int, col1: int, row2: int, col2: int) -> float:
        """Estimate score potential for a swap using local patterns."""
        score = 0.0
        
        # Save original state
        orig_val1 = self.grid[row1, col1]
        orig_val2 = self.grid[row2, col2]
        
        # Try swap
        self.grid[row1, col1] = orig_val2
        self.grid[row2, col2] = orig_val1
        
        # Check formations
        formations = self.find_all_formations()
        if formations:
            # Base score from formation size
            score = len(formations) * 100
            
            # Bonus for L shapes (more complex, likely to trigger cascades)
            l_shapes = self.find_l_shapes()
            score *= (1 + 0.2 * len(l_shapes))
            
        # Restore original state
        self.grid[row1, col1] = orig_val1
        self.grid[row2, col2] = orig_val2
        
        return score