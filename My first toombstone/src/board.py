import numpy as np
from typing import List, Tuple, Set, Optional
from enum import IntEnum

class Color(IntEnum):
    EMPTY = 0
    RED = 1
    YELLOW = 2
    GREEN = 3
    BLUE = 4

class Formation:
    def __init__(self, cells: Set[Tuple[int, int]], score: int):
        self.cells = cells
        self.score = score

class Board:
    def __init__(self, rows: int = 11, cols: int = 11, predefined: Optional[np.ndarray] = None):
        self.rows = rows
        self.cols = cols
        if predefined is not None:
            self.grid = predefined.copy()
        else:
            self.grid = np.random.randint(1, 5, size=(rows, cols), dtype=np.int8)
    
    def is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def get_color(self, row: int, col: int) -> Color:
        if not self.is_valid_position(row, col):
            return Color.EMPTY
        return Color(self.grid[row, col])
    
    def find_line_formations(self) -> List[Formation]:
        formations = []
        # Check horizontal lines
        for row in range(self.rows):
            count = 1
            current_color = self.get_color(row, 0)
            cells = {(row, 0)}
            
            for col in range(1, self.cols):
                color = self.get_color(row, col)
                if color == current_color and color != Color.EMPTY:
                    count += 1
                    cells.add((row, col))
                else:
                    if count >= 3:
                        score = 5 if count == 3 else (10 if count == 4 else 50)
                        formations.append(Formation(cells, score))
                    count = 1
                    cells = {(row, col)}
                    current_color = color
                    
            if count >= 3 and current_color != Color.EMPTY:
                score = 5 if count == 3 else (10 if count == 4 else 50)
                formations.append(Formation(cells, score))
        
        # Check vertical lines
        for col in range(self.cols):
            count = 1
            current_color = self.get_color(0, col)
            cells = {(0, col)}
            
            for row in range(1, self.rows):
                color = self.get_color(row, col)
                if color == current_color and color != Color.EMPTY:
                    count += 1
                    cells.add((row, col))
                else:
                    if count >= 3:
                        score = 5 if count == 3 else (10 if count == 4 else 50)
                        formations.append(Formation(cells, score))
                    count = 1
                    cells = {(row, col)}
                    current_color = color
                    
            if count >= 3 and current_color != Color.EMPTY:
                score = 5 if count == 3 else (10 if count == 4 else 50)
                formations.append(Formation(cells, score))
        
        return formations
    
    def find_l_formations(self) -> List[Formation]:
        formations = []
        for row in range(self.rows - 2):
            for col in range(self.cols - 2):
                # Check L pattern in 4 orientations
                for orientation in range(4):
                    # Calculate orientation-specific offsets
                    vertical = orientation < 2  # True for ┗ and ┛, False for ┏ and ┓
                    right = orientation % 2 == 1  # True for ┛ and ┓
                    
                    color = self.get_color(row, col)
                    if color == Color.EMPTY:
                        continue
                    
                    cells = set()
                    valid = True
                    
                    # Check vertical part (3 cells)
                    for i in range(3):
                        r = row + (i if vertical else -i)
                        c = col + (0 if vertical else (2 if right else 0))
                        if not self.is_valid_position(r, c) or self.get_color(r, c) != color:
                            valid = False
                            break
                        cells.add((r, c))
                    
                    if not valid:
                        continue
                    
                    # Check horizontal part (3 cells)
                    for i in range(3):
                        r = row + (2 if vertical else 0)
                        c = col + (i if right else -i)
                        if not self.is_valid_position(r, c) or self.get_color(r, c) != color:
                            valid = False
                            break
                        cells.add((r, c))
                    
                    if valid:
                        # Only add if we haven't found this formation before
                        found = False
                        for existing in formations:
                            if existing.cells == cells:
                                found = True
                                break
                        if not found:
                            formations.append(Formation(cells, 20))
        
        return formations
    
    def find_t_formations(self) -> List[Formation]:
        formations = []
        # For each possible center of T
        for row in range(1, self.rows - 1):
            for col in range(1, self.cols - 1):
                color = self.get_color(row, col)
                if color == Color.EMPTY:
                    continue
                    
                # Check each of the 4 possible T orientations
                # orientation: 0=┳, 1=┻, 2=┫, 3=┣
                for orientation in range(4):
                    cells = {(row, col)}  # Center cell
                    valid = True
                    
                    # Check the vertical part (2 more cells)
                    if orientation < 2:  # Upright or downright T
                        dr = -1 if orientation == 0 else 1
                        for i in range(1, 3):
                            r = row + (dr * i)
                            if not self.is_valid_position(r, col) or self.get_color(r, col) != color:
                                valid = False
                                break
                            cells.add((r, col))
                            
                        # If vertical part is valid, check horizontal part
                        if valid:
                            for dc in [-1, 1]:  # Check both sides
                                if not self.is_valid_position(row, col + dc) or self.get_color(row, col + dc) != color:
                                    valid = False
                                    break
                                cells.add((row, col + dc))
                                
                    else:  # Leftward or rightward T
                        dc = -1 if orientation == 3 else 1
                        for i in range(1, 3):
                            c = col + (dc * i)
                            if not self.is_valid_position(row, c) or self.get_color(row, c) != color:
                                valid = False
                                break
                            cells.add((row, c))
                            
                        # If horizontal part is valid, check vertical part
                        if valid:
                            for dr in [-1, 1]:  # Check both up and down
                                if not self.is_valid_position(row + dr, col) or self.get_color(row + dr, col) != color:
                                    valid = False
                                    break
                                cells.add((row + dr, col))
                                
                    if valid:
                        # Only add if we haven't found this formation before
                        found = False
                        for existing in formations:
                            if existing.cells == cells:
                                found = True
                                break
                        if not found:
                            formations.append(Formation(cells, 30))
        
        return formations
    
    def apply_gravity(self) -> None:
        for col in range(self.cols):
            # Count empty cells and move candies down
            empty_count = 0
            for row in range(self.rows - 1, -1, -1):
                if self.grid[row, col] == Color.EMPTY:
                    empty_count += 1
                elif empty_count > 0:
                    self.grid[row + empty_count, col] = self.grid[row, col]
                    self.grid[row, col] = Color.EMPTY
    
    def refill_board(self) -> None:
        for col in range(self.cols):
            for row in range(self.rows):
                if self.grid[row, col] == Color.EMPTY:
                    self.grid[row, col] = np.random.randint(1, 5)
    
    def try_swap(self, row1: int, col1: int, row2: int, col2: int) -> bool:
        # Check if positions are adjacent
        if not (abs(row1 - row2) == 1 and col1 == col2 or 
                row1 == row2 and abs(col1 - col2) == 1):
            return False
            
        # Perform swap
        self.grid[row1, col1], self.grid[row2, col2] = \
            self.grid[row2, col2], self.grid[row1, col1]
            
        # Optimized check: a valid swap must create a formation that includes at least
        # one of the swapped cells. Check only local neighborhoods instead of full scan.
        created = self._swap_creates_formation(row1, col1, row2, col2)
        if not created:
            # Revert swap if no formations created
            self.grid[row1, col1], self.grid[row2, col2] = \
                self.grid[row2, col2], self.grid[row1, col1]
            return False

        return True

    # --- Optimized local checks for swaps ---
    def _run_length_horizontal(self, row: int, col: int) -> int:
        """Return total contiguous run length horizontally that includes (row,col)."""
        color = self.get_color(row, col)
        if color == Color.EMPTY:
            return 0
        length = 1
        # left
        c = col - 1
        while c >= 0 and self.get_color(row, c) == color:
            length += 1
            c -= 1
        # right
        c = col + 1
        while c < self.cols and self.get_color(row, c) == color:
            length += 1
            c += 1
        return length

    def _run_length_vertical(self, row: int, col: int) -> int:
        """Return total contiguous run length vertically that includes (row,col)."""
        color = self.get_color(row, col)
        if color == Color.EMPTY:
            return 0
        length = 1
        # up
        r = row - 1
        while r >= 0 and self.get_color(r, col) == color:
            length += 1
            r -= 1
        # down
        r = row + 1
        while r < self.rows and self.get_color(r, col) == color:
            length += 1
            r += 1
        return length

    def _check_L_at(self, row: int, col: int) -> bool:
        """Check if an L (3+3) exists that includes (row,col) as any of its cells."""
        color = self.get_color(row, col)
        if color == Color.EMPTY:
            return False
        # enumerate possible L shapes centered within 3x3 neighborhoods
        # For each corner of 3x3, check vertical length 3 and horizontal length 3 meeting at corner
        dirs = [(-2, -2), (-2, 0), (0, -2), (0, 0)]
        for dr, dc in dirs:
            base_r = row + dr
            base_c = col + dc
            # four corners relative to base
            # check each of the 4 L orientations anchored at base
            # vertical down + horizontal right
            try:
                cells = [(base_r + i, base_c) for i in range(3)] + [(base_r + 2, base_c + j) for j in range(3)]
            except Exception:
                cells = []
            if cells and all(self.is_valid_position(r, c) and self.get_color(r, c) == color for r, c in cells):
                return True
            # vertical down + horizontal left
            try:
                cells = [(base_r + i, base_c + 2) for i in range(3)] + [(base_r + 2, base_c + 2 - j) for j in range(3)]
            except Exception:
                cells = []
            if cells and all(self.is_valid_position(r, c) and self.get_color(r, c) == color for r, c in cells):
                return True
            # vertical up + horizontal right
            try:
                cells = [(base_r + 2 - i, base_c) for i in range(3)] + [(base_r, base_c + j) for j in range(3)]
            except Exception:
                cells = []
            if cells and all(self.is_valid_position(r, c) and self.get_color(r, c) == color for r, c in cells):
                return True
            # vertical up + horizontal left
            try:
                cells = [(base_r + 2 - i, base_c + 2) for i in range(3)] + [(base_r, base_c + 2 - j) for j in range(3)]
            except Exception:
                cells = []
            if cells and all(self.is_valid_position(r, c) and self.get_color(r, c) == color for r, c in cells):
                return True
        return False

    def _check_T_at(self, row: int, col: int) -> bool:
        """Check if a T (3+3+3) exists that includes (row,col) as any of its cells or center nearby."""
        color = self.get_color(row, col)
        if color == Color.EMPTY:
            return False
        # Check centers within a 3x3 neighborhood (T center must be an interior cell)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                r = row + dr
                c = col + dc
                if not self.is_valid_position(r, c):
                    continue
                center_color = self.get_color(r, c)
                if center_color == Color.EMPTY:
                    continue
                # vertical stem + horizontal crossbar
                # check upright/downright (vertical stem length 3 including center)
                # orientation up/down
                for orient in range(4):
                    valid = True
                    cells = {(r, c)}
                    if orient == 0:  # upright: stem up, crossbar at center row
                        # stem includes center and two above
                        for i in (1, 2):
                            nr = r - i
                            if not self.is_valid_position(nr, c) or self.get_color(nr, c) != center_color:
                                valid = False; break
                            cells.add((nr, c))
                        if not valid: continue
                        # crossbar left/right of center
                        for nc in (c - 1, c + 1):
                            if not self.is_valid_position(r, nc) or self.get_color(r, nc) != center_color:
                                valid = False; break
                            cells.add((r, nc))
                        if valid: return True
                    elif orient == 1:  # downright: stem down
                        for i in (1, 2):
                            nr = r + i
                            if not self.is_valid_position(nr, c) or self.get_color(nr, c) != center_color:
                                valid = False; break
                            cells.add((nr, c))
                        if not valid: continue
                        for nc in (c - 1, c + 1):
                            if not self.is_valid_position(r, nc) or self.get_color(r, nc) != center_color:
                                valid = False; break
                            cells.add((r, nc))
                        if valid: return True
                    elif orient == 2:  # rightwards: stem right
                        for i in (1, 2):
                            nc = c + i
                            if not self.is_valid_position(r, nc) or self.get_color(r, nc) != center_color:
                                valid = False; break
                            cells.add((r, nc))
                        if not valid: continue
                        for nr in (r - 1, r + 1):
                            if not self.is_valid_position(nr, c) or self.get_color(nr, c) != center_color:
                                valid = False; break
                            cells.add((nr, c))
                        if valid: return True
                    else:  # leftwards: stem left
                        for i in (1, 2):
                            nc = c - i
                            if not self.is_valid_position(r, nc) or self.get_color(r, nc) != center_color:
                                valid = False; break
                            cells.add((r, nc))
                        if not valid: continue
                        for nr in (r - 1, r + 1):
                            if not self.is_valid_position(nr, c) or self.get_color(nr, c) != center_color:
                                valid = False; break
                            cells.add((nr, c))
                        if valid: return True
        return False

    def _swap_creates_formation(self, r1: int, c1: int, r2: int, c2: int) -> bool:
        # After swap, check if either swapped cell is part of any formation (line >=3, L or T)
        # Check local neighbourhoods only
        if self._run_length_horizontal(r1, c1) >= 3 or self._run_length_vertical(r1, c1) >= 3:
            return True
        if self._run_length_horizontal(r2, c2) >= 3 or self._run_length_vertical(r2, c2) >= 3:
            return True
        # check for L or T around swapped cells
        if self._check_L_at(r1, c1) or self._check_T_at(r1, c1):
            return True
        if self._check_L_at(r2, c2) or self._check_T_at(r2, c2):
            return True
        return False

    def local_score_for_swap(self, r1: int, c1: int, r2: int, c2: int) -> int:
        """Estimate immediate score produced by swapping the two cells.
        This is a local-only calculation that avoids full-board formation detection.
        It returns the sum of formation scores that would include the swapped cells
        (lines, L, T) — this is used by the move-evaluator to rank swaps quickly.
        """
        # swap
        self.grid[r1, c1], self.grid[r2, c2] = self.grid[r2, c2], self.grid[r1, c1]
        score = 0

        # check around both swapped positions within a small neighborhood
        to_check = set()
        for (r, c) in ((r1, c1), (r2, c2)):
            for dr in (-2, -1, 0, 1, 2):
                for dc in (-2, -1, 0, 1, 2):
                    rr = r + dr
                    cc = c + dc
                    if 0 <= rr < self.rows and 0 <= cc < self.cols:
                        to_check.add((rr, cc))

        used_cells = set()
        # first detect lines centered at any of these cells
        for (r, c) in to_check:
            if (r, c) in used_cells:
                continue
            # horizontal
            hlen = self._run_length_horizontal(r, c)
            if hlen >= 3:
                # collect cell coordinates for the run
                left = c
                while left - 1 >= 0 and self.get_color(r, left - 1) == self.get_color(r, c):
                    left -= 1
                run_cells = {(r, cc) for cc in range(left, left + hlen)}
                new_cells = run_cells - used_cells
                if new_cells:
                    used_cells.update(new_cells)
                    if hlen == 3:
                        score += 5
                    elif hlen == 4:
                        score += 10
                    else:
                        score += 50
            # vertical
            vlen = self._run_length_vertical(r, c)
            if vlen >= 3:
                top = r
                while top - 1 >= 0 and self.get_color(top - 1, c) == self.get_color(r, c):
                    top -= 1
                run_cells = {(rr, c) for rr in range(top, top + vlen)}
                new_cells = run_cells - used_cells
                if new_cells:
                    used_cells.update(new_cells)
                    if vlen == 3:
                        score += 5
                    elif vlen == 4:
                        score += 10
                    else:
                        score += 50

        # L and T checks (local) — award their fixed scores if found and not overlapping
        for (r, c) in ((r1, c1), (r2, c2)):
            if (r, c) in used_cells:
                continue
            if self._check_L_at(r, c):
                # conservative: assume L uses up to 5 cells but fixed score 20
                # mark surrounding 3x3 as used to avoid double counting
                for dr in (-2, -1, 0, 1, 2):
                    for dc in (-2, -1, 0, 1, 2):
                        rr = r + dr; cc = c + dc
                        if 0 <= rr < self.rows and 0 <= cc < self.cols:
                            used_cells.add((rr, cc))
                score += 20
            elif self._check_T_at(r, c):
                for dr in (-2, -1, 0, 1, 2):
                    for dc in (-2, -1, 0, 1, 2):
                        rr = r + dr; cc = c + dc
                        if 0 <= rr < self.rows and 0 <= cc < self.cols:
                            used_cells.add((rr, cc))
                score += 30

        # revert swap
        self.grid[r1, c1], self.grid[r2, c2] = self.grid[r2, c2], self.grid[r1, c1]
        return score
    
    def find_all_formations(self) -> List[Formation]:
        all_formations = []
        all_formations.extend(self.find_line_formations())
        all_formations.extend(self.find_l_formations())
        all_formations.extend(self.find_t_formations())
        
        # Sort formations by score (highest first) to handle overlaps
        all_formations.sort(key=lambda f: f.score, reverse=True)
        
        # Handle overlaps - remove formations that share cells with higher scoring formations
        used_cells = set()
        final_formations = []
        
        for formation in all_formations:
            if not formation.cells & used_cells:  # No overlap with used cells
                final_formations.append(formation)
                used_cells.update(formation.cells)
        
        return final_formations
    
    def remove_formations(self, formations: List[Formation]) -> int:
        score = 0
        removed_cells = set()
        
        for formation in formations:
            # Only count score and remove cells that haven't been removed yet
            new_cells = formation.cells - removed_cells
            if new_cells:
                score += formation.score
                removed_cells.update(new_cells)
        
        # Set all removed cells to empty
        for row, col in removed_cells:
            self.grid[row, col] = Color.EMPTY
            
        return score
    
    def find_possible_moves(self) -> List[Tuple[int, int, int, int]]:
        moves = []
        # Check all possible swaps
        for row in range(self.rows):
            for col in range(self.cols):
                # Try right swap
                if col < self.cols - 1:
                    # perform swap and check locally
                    self.grid[row, col], self.grid[row, col + 1] = self.grid[row, col + 1], self.grid[row, col]
                    if self._swap_creates_formation(row, col, row, col + 1):
                        moves.append((row, col, row, col + 1))
                    # revert
                    self.grid[row, col], self.grid[row, col + 1] = self.grid[row, col + 1], self.grid[row, col]
                
                # Try down swap
                if row < self.rows - 1:
                    self.grid[row, col], self.grid[row + 1, col] = self.grid[row + 1, col], self.grid[row, col]
                    if self._swap_creates_formation(row, col, row + 1, col):
                        moves.append((row, col, row + 1, col))
                    self.grid[row, col], self.grid[row + 1, col] = self.grid[row + 1, col], self.grid[row, col]
        
        return moves