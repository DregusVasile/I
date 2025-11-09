import unittest
import numpy as np
from src.board import Board, Color, Formation

class TestBoard(unittest.TestCase):
    def setUp(self):
        # Create a test board with known patterns
        self.test_board = np.array([
            [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4],
            [2, 2, 2, 3, 3, 3, 4, 4, 4, 1, 1],
            [3, 3, 3, 4, 4, 4, 1, 1, 1, 2, 2],
            [4, 4, 4, 1, 1, 1, 2, 2, 2, 3, 3],
            [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3],
            [2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4],
            [3, 4, 1, 2, 3, 4, 1, 2, 3, 4, 1],
            [4, 1, 2, 3, 4, 1, 2, 3, 4, 1, 2],
            [1, 1, 1, 2, 3, 4, 1, 2, 3, 4, 1],
            [2, 2, 2, 3, 4, 1, 2, 3, 4, 1, 2],
            [3, 3, 3, 4, 1, 2, 3, 4, 1, 2, 3]
        ], dtype=np.int8)
        self.board = Board(predefined=self.test_board)
    
    def test_line_formations(self):
        # Test horizontal lines of 3
        formations = self.board.find_line_formations()
        horizontal_3s = [f for f in formations if len(f.cells) == 3]
        self.assertGreater(len(horizontal_3s), 0)
        
        # Verify score is correct
        for formation in horizontal_3s:
            self.assertEqual(formation.score, 5)
    
    def test_l_formations(self):
        # Create a board with an L pattern
        l_pattern = np.zeros((11, 11), dtype=np.int8)
        l_pattern[0:3, 0] = 1  # Vertical part
        l_pattern[2, 0:3] = 1  # Horizontal part
        board = Board(predefined=l_pattern)
        
        formations = board.find_l_formations()
        self.assertEqual(len(formations), 1)
        self.assertEqual(formations[0].score, 20)
    
    def test_t_formations(self):
        # Create a board with a T pattern
        t_pattern = np.zeros((11, 11), dtype=np.int8)
        # Create an upright T
        t_pattern[1:4, 1] = 1  # Vertical stem (3 cells)
        t_pattern[1, 0:3] = 1  # Horizontal crossbar (3 cells)
        board = Board(predefined=t_pattern)
        
        print("\nT pattern board:")
        for row in range(5):
            print(" ".join(str(board.get_color(row, col)) for col in range(5)))
        
        formations = board.find_t_formations()
        print(f"\nFound {len(formations)} T formations")
        for f in formations:
            print(f"Formation with {len(f.cells)} cells at positions {sorted(f.cells)}")
        
        self.assertEqual(len(formations), 1)
        self.assertEqual(formations[0].score, 30)
    
    def test_gravity(self):
        # Create a board with gaps
        test_board = np.ones((11, 11), dtype=np.int8)
        test_board[5, 5] = 0  # Create a gap
        board = Board(predefined=test_board)
        
        board.apply_gravity()
        # Check that the gap has moved to the top
        self.assertEqual(board.get_color(0, 5), Color.EMPTY)
        self.assertEqual(board.get_color(5, 5), Color.RED)
    
    def test_valid_swap(self):
        # Create a board where a swap would create a formation
        test_board = np.ones((11, 11), dtype=np.int8)
        test_board[5, 5] = 2
        board = Board(predefined=test_board)
        
        # Swap to create a line of 3
        result = board.try_swap(5, 5, 5, 4)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()