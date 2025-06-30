import unittest
import tetris # Import the main tetris game file

class TestTetrisGame(unittest.TestCase):

    def setUp(self):
        """Setup basic structures for testing."""
        tetris.BOARD_WIDTH = 10 # Ensure consistent board size for tests
        tetris.BOARD_HEIGHT = 20
        self.board = tetris.create_board()

    def test_create_board(self):
        self.assertEqual(len(self.board), tetris.BOARD_HEIGHT)
        self.assertEqual(len(self.board[0]), tetris.BOARD_WIDTH)
        self.assertTrue(all(cell == 0 for row in self.board for cell in row))

    def test_spawn_new_piece(self):
        piece, x, y, name, rotation = tetris.spawn_new_piece(self.board)
        self.assertIsNotNone(piece)
        self.assertIn(name, tetris.TETROMINOES)
        self.assertTrue(0 <= x < tetris.BOARD_WIDTH)
        self.assertEqual(y, 0) # Pieces should spawn at the top

        # Test game over on spawn if board is full at top
        full_board = [[2 for _ in range(tetris.BOARD_WIDTH)] for _ in range(tetris.BOARD_HEIGHT)]
        piece_game_over, _, _, _, _ = tetris.spawn_new_piece(full_board)
        self.assertIsNone(piece_game_over)

    def test_check_collision(self):
        # Test collision with boundaries
        o_piece = tetris.TETROMINOES['O'][0] # Simple 2x2 square
        self.assertTrue(tetris.check_collision(self.board, o_piece, -1, 0)) # Left boundary
        self.assertTrue(tetris.check_collision(self.board, o_piece, tetris.BOARD_WIDTH -1, 0)) # Right boundary (O is 2 wide)
        self.assertTrue(tetris.check_collision(self.board, o_piece, 0, tetris.BOARD_HEIGHT -1)) # Bottom boundary (O is 2 high)
        self.assertFalse(tetris.check_collision(self.board, o_piece, 0, 0)) # Valid position

        # Test collision with other blocks
        self.board[2][2] = 2 # Place a block
        # An 'O' piece at (1,1) has cells (1,1),(1,2),(2,1),(2,2). So (2,2) collides.
        self.assertTrue(tetris.check_collision(self.board, o_piece, 1, 1))
        self.assertFalse(tetris.check_collision(self.board, o_piece, 0, 0))


    def test_move_piece(self):
        i_piece = tetris.TETROMINOES['I'][0] # Vertical I piece (4 cells high)
        px, py = 3, 0 # Initial position

        # Move right
        new_px, new_py = tetris.move_piece(self.board, i_piece, px, py, 1, 0)
        self.assertEqual(new_px, px + 1)
        self.assertEqual(new_py, py)

        # Move left (blocked by boundary)
        # I piece is 1 wide (0,0),(1,0),(2,0),(3,0) relative. At x=0, it's fine.
        # If we try to move left from x=0, it should not move.
        new_px, new_py = tetris.move_piece(self.board, i_piece, 0, py, -1, 0)
        self.assertEqual(new_px, 0)

        # Move down
        new_px, new_py = tetris.move_piece(self.board, i_piece, px, py, 0, 1)
        self.assertEqual(new_px, px)
        self.assertEqual(new_py, py + 1)

        # Move down until collision (I piece is 4 units high, board is 20 high)
        # It can move down 20 - 4 = 16 times from y=0 to y=16.
        # At y=16, its lowest cell is 16+3 = 19. Next move to y=17 would collide.
        current_y = 0
        for _ in range(tetris.BOARD_HEIGHT - 4): # Max valid moves down
             _, current_y = tetris.move_piece(self.board, i_piece, px, current_y, 0, 1)
        self.assertEqual(current_y, tetris.BOARD_HEIGHT - 4)

        # Next move down should collide
        _, next_y_collide = tetris.move_piece(self.board, i_piece, px, current_y, 0, 1)
        self.assertEqual(next_y_collide, current_y) # Should not have moved

    def test_rotate_piece(self):
        # Test rotation for T piece (known rotations)
        # T piece: [[(0,0),(0,1),(0,2),(1,1)]]
        t_piece_name = 'T'
        initial_rotation = 0
        px, py = 3, 3

        # First rotation
        rotated_shape1, new_rot1, new_px1 = tetris.rotate_piece(self.board, t_piece_name, initial_rotation, px, py)
        self.assertEqual(new_rot1, 1)
        self.assertEqual(new_px1, px) # No kick expected in open space
        self.assertNotEqual(rotated_shape1, tetris.TETROMINOES[t_piece_name][initial_rotation])
        self.assertEqual(rotated_shape1, tetris.TETROMINOES[t_piece_name][1])

        # Test rotation with wall kick (simple case)
        # Place an 'I' piece vertically near left wall, try to rotate to horizontal
        i_piece_name = 'I'
        i_vertical = tetris.TETROMINOES[i_piece_name][0] # (0,0),(1,0),(2,0),(3,0)
        # Position it at x=0. Rotating to horizontal [(0,0),(0,1),(0,2),(0,3)] would normally fail.
        # With a kick, it might succeed if there's space.
        # Our basic kick tries 0, -1, 1, -2, 2.
        # If it's at x=0, original rotation fails. Kick -1 fails. Kick 1 might work.

        # For a vertical 'I' at (0,0), its cells are (0,0), (1,0), (2,0), (3,0)
        # Rotated horizontal 'I' cells relative to (0,0) are (0,0), (0,1), (0,2), (0,3)
        # If at board x=0, y=0:
        # Original rotation: cells (0,0), (0,1), (0,2), (0,3) - should be fine if space
        # Let's test a kick. Put it at x=0, y=0.
        # If we rotate it, it becomes horizontal. If board width is 10, it fits.
        # No kick needed if it just fits.
        rotated_shape_i, new_rot_i, new_px_i = tetris.rotate_piece(self.board, i_piece_name, 0, 0, 0) # 0 is vertical
        self.assertEqual(new_rot_i, 1) # Should rotate to horizontal
        self.assertEqual(new_px_i, 0) # No kick needed, it fits.
        self.assertEqual(rotated_shape_i, tetris.TETROMINOES[i_piece_name][1])

        # Test a case where a kick IS needed.
        # Place a T piece near the right wall such that normal rotation would go out of bounds.
        # T initial: (0,0),(0,1),(0,2),(1,1)
        # Rotated T: (0,1),(1,0),(1,1),(2,1)
        # If T is at x=W-2, y=3. Initial T cells: (3,W-2),(3,W-1),(3,W),(4,W-1) -> (3,W) is out of bounds if pivot is (0,1)
        # Let's use the defined T piece structure:
        # T[0] = [(0,0),(0,1),(0,2),(1,1)] (width 3, height 2)
        # T[1] = [(0,1),(1,0),(1,1),(2,1)] (width 2, height 3, pivot (0,1) relative to its shape)
        # Place T[0] at x = BOARD_WIDTH - 2, y = 5
        # Max x for T[0] is x + 2 = W-2+2 = W. This is out of bounds.
        # Let's try BOARD_WIDTH - 3 for x. Max x for T[0] is x+2 = W-3+2 = W-1. (Fits)
        # Rotated T[1] has max x relative to its own top-left as 1.
        # If rotated at x = W-3, its cells are (y, W-3+1), (y+1,W-3+0), (y+1,W-3+1), (y+2,W-3+1)
        # Max x is W-3+1 = W-2. (Fits) No kick needed here.

        # A better kick test: Put an 'I' piece horizontally at the bottom, try to rotate vertical.
        # I_horiz = [(0,0), (0,1), (0,2), (0,3)] (width 4)
        # Position at y = BOARD_HEIGHT - 1, x = 0.
        # Cells: (H-1,0), (H-1,1), (H-1,2), (H-1,3)
        # Rotate to I_vert = [(0,0),(1,0),(2,0),(3,0)] (height 4)
        # If rotated at (x=0, y=H-1), cells would be:
        # (H-1+0, 0), (H-1+1, 0), (H-1+2, 0), (H-1+3, 0)
        # (H-1,0), (H,0), (H+1,0), (H+2,0) -> Cells (H,0), (H+1,0), (H+2,0) are out of bounds.
        # It needs a kick upwards. Our current kick is only horizontal (dx).
        # This means this rotation should fail with current kick logic.
        self.board = tetris.create_board() # Fresh board
        # Place horizontal I at bottom: x=3, y=BH-1
        shape_i_horiz = tetris.TETROMINOES['I'][1]
        rot_i_horiz_idx = 1
        px_i_horiz, py_i_horiz = 3, tetris.BOARD_HEIGHT - 1

        # Try to rotate it. It should fail because vertical I is 4 high.
        # Original shape should be returned.
        rotated_s, new_r, new_px = tetris.rotate_piece(self.board, 'I', rot_i_horiz_idx, px_i_horiz, py_i_horiz)
        self.assertEqual(new_r, rot_i_horiz_idx) # Rotation should not change
        self.assertEqual(new_px, px_i_horiz)     # X should not change
        self.assertEqual(rotated_s, shape_i_horiz) # Shape should be the same


    def test_lock_piece(self):
        o_piece = tetris.TETROMINOES['O'][0]
        px, py = 1, 1
        tetris.lock_piece(self.board, o_piece, px, py)
        expected_coords = [(py+r, px+c) for r,c in o_piece]
        for r, c in expected_coords:
            self.assertEqual(self.board[r][c], 2) # 2 for locked piece

    def test_clear_lines(self):
        # Fill one line completely
        for c in range(tetris.BOARD_WIDTH):
            self.board[tetris.BOARD_HEIGHT - 1][c] = 2 # Fill bottom line

        lines_cleared = tetris.clear_lines(self.board)
        self.assertEqual(lines_cleared, 1)
        self.assertTrue(all(cell == 0 for cell in self.board[tetris.BOARD_HEIGHT - 1])) # Bottom line should be empty
        self.assertTrue(all(cell == 0 for cell in self.board[0])) # Top line should be new and empty

        # Fill two lines
        self.setUp() # Reset board
        for c in range(tetris.BOARD_WIDTH):
            self.board[tetris.BOARD_HEIGHT - 1][c] = 2
            self.board[tetris.BOARD_HEIGHT - 2][c] = 2

        # Add some blocks above that should fall
        self.board[tetris.BOARD_HEIGHT - 3][0] = 2
        self.board[tetris.BOARD_HEIGHT - 3][1] = 2

        lines_cleared = tetris.clear_lines(self.board)
        self.assertEqual(lines_cleared, 2)
        self.assertEqual(self.board[tetris.BOARD_HEIGHT - 1][0], 2) # Block from H-3 should fall to H-1
        self.assertEqual(self.board[tetris.BOARD_HEIGHT - 1][1], 2) # Block from H-3 should fall to H-1
        self.assertTrue(all(self.board[0][c] == 0 for c in range(tetris.BOARD_WIDTH))) # New top line
        self.assertTrue(all(self.board[1][c] == 0 for c in range(tetris.BOARD_WIDTH))) # New second top line


    def test_calculate_score(self):
        self.assertEqual(tetris.calculate_score(1, 0), tetris.SCORE_MAP[1])
        self.assertEqual(tetris.calculate_score(4, 100), 100 + tetris.SCORE_MAP[4])
        self.assertEqual(tetris.calculate_score(0, 50), 50) # No lines cleared
        self.assertEqual(tetris.calculate_score(5, 50), 50) # Invalid number of lines


if __name__ == '__main__':
    unittest.main()
