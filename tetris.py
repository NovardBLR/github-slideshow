# tetris.py

BOARD_WIDTH = 10
BOARD_HEIGHT = 20

def create_board():
    """Creates an empty game board."""
    return [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

def display_board(board, current_piece=None, piece_x=0, piece_y=0):
    """Displays the game board.

    Args:
        board: The game board (2D list).
        current_piece: The current falling Tetromino (list of (row, col) tuples).
        piece_x: The x-coordinate of the current piece's top-left corner.
        piece_y: The y-coordinate of the current piece's top-left corner.
    """
    # Create a temporary board to display the current piece
    display_board = [row[:] for row in board]

    if current_piece:
        for r_offset, c_offset in current_piece:
            r, c = piece_y + r_offset, piece_x + c_offset
            if 0 <= r < BOARD_HEIGHT and 0 <= c < BOARD_WIDTH:
                display_board[r][c] = 1 # Mark piece cells

    print("-" * (BOARD_WIDTH * 2 + 3))
    for r in range(BOARD_HEIGHT):
        print("|", end=" ")
        for c in range(BOARD_WIDTH):
            cell = display_board[r][c]
            if cell == 1: # Part of a Tetromino
                print("■", end=" ")
            elif cell == 2: # Part of a landed block
                 print("□", end=" ")
            else: # Empty cell
                print(".", end=" ")
        print("|")
    print("-" * (BOARD_WIDTH * 2 + 3))

if __name__ == '__main__':
    board = create_board()
    display_board(board)

# --- Tetromino Definitions ---
TETROMINOES = {
    'I': [[(0, 0), (1, 0), (2, 0), (3, 0)], [(0,0), (0,1), (0,2), (0,3)]], # Vertical and Horizontal
    'O': [[(0, 0), (0, 1), (1, 0), (1, 1)]], # Always the same
    'T': [[(0, 0), (0, 1), (0, 2), (1, 1)], # T shape
          [(0, 1), (1, 0), (1, 1), (2, 1)], # T rotated right
          [(0, 1), (1, 0), (1, 1), (1, 2)], # T upside down
          [(0, 0), (1, 0), (1, 1), (2, 0)]], # T rotated left
    'S': [[(0, 1), (0, 2), (1, 0), (1, 1)], # S shape
          [(0, 0), (1, 0), (1, 1), (2, 1)]], # S rotated
    'Z': [[(0, 0), (0, 1), (1, 1), (1, 2)], # Z shape
          [(0, 2), (1, 1), (1, 2), (2, 1)]], # Z rotated
    'J': [[(0, 0), (1, 0), (2, 0), (2, 1)], # J shape
          [(0, 0), (0, 1), (0, 2), (1, 0)], # J rotated right
          [(0, 0), (0, 1), (1, 1), (2, 1)], # J upside down
          [(0, 2), (1, 0), (1, 1), (1, 2)]], # J rotated left
    'L': [[(0, 1), (1, 1), (2, 1), (2, 0)], # L shape
          [(0, 0), (1, 0), (1, 1), (1, 2)], # L rotated right
          [(0, 0), (0, 1), (1, 0), (2, 0)], # L upside down
          [(0, 0), (0, 1), (0, 2), (1, 2)]]  # L rotated left
}

import random

# --- Collision Detection ---
def check_collision(board, piece, x, y):
    """Checks if the piece collides with board boundaries or other blocks.
    Args:
        board: The game board.
        piece: The Tetromino shape (list of (row, col) offsets).
        x: The x-coordinate of the piece's top-left on the board.
        y: The y-coordinate of the piece's top-left on the board.
    Returns:
        True if collision occurs, False otherwise.
    """
    for r_offset, c_offset in piece:
        r, c = y + r_offset, x + c_offset
        # Check board boundaries
        if not (0 <= r < BOARD_HEIGHT and 0 <= c < BOARD_WIDTH):
            return True
        # Check collision with existing blocks on the board
        if board[r][c] != 0: # 0 means empty
            return True
    return False

# --- Piece Movement ---
def move_piece(board, piece, x, y, dx, dy):
    """Attempts to move the piece by dx, dy.
    Returns new (x, y) if move is valid, else original (x, y).
    """
    new_x, new_y = x + dx, y + dy
    if not check_collision(board, piece, new_x, new_y):
        return new_x, new_y
    return x, y

def rotate_piece(board, piece_name, current_rotation, x, y):
    """Attempts to rotate the current piece.
    Returns the new piece shape and rotation index if valid, else original.
    """
    piece_rotations = TETROMINOES[piece_name]
    next_rotation_index = (current_rotation + 1) % len(piece_rotations)
    rotated_piece_shape = piece_rotations[next_rotation_index]

    # Try to fit the rotated piece, potentially "kicking" it
    # Basic kick: try original position, then one left, then one right
    for kick_dx in [0, -1, 1, -2, 2]: # Wall kick attempts
        if not check_collision(board, rotated_piece_shape, x + kick_dx, y):
            return rotated_piece_shape, next_rotation_index, x + kick_dx
    return TETROMINOES[piece_name][current_rotation], current_rotation, x # Return original if no kick works

# --- Game Logic ---
def lock_piece(board, piece, x, y):
    """Locks the piece onto the board."""
    for r_offset, c_offset in piece:
        r, c = y + r_offset, x + c_offset
        if 0 <= r < BOARD_HEIGHT and 0 <= c < BOARD_WIDTH: # Should always be true if no collision before locking
            board[r][c] = 2 # Mark as a landed block (using 2, 1 is for current piece)

def clear_lines(board):
    """Checks for and clears completed lines.
    Returns the number of lines cleared.
    """
    lines_cleared = 0
    new_board = [row for row in board if not all(cell == 2 for cell in row)] # Keep rows not full of 2s

    lines_cleared = BOARD_HEIGHT - len(new_board)

    # Add new empty lines at the top
    for _ in range(lines_cleared):
        new_board.insert(0, [0 for _ in range(BOARD_WIDTH)])

    # Update the original board (important!)
    for r in range(BOARD_HEIGHT):
        board[r] = new_board[r]

    return lines_cleared

# Score constants
SCORE_MAP = {
    1: 40,  # 1 line
    2: 100, # 2 lines
    3: 300, # 3 lines
    4: 1200 # 4 lines (Tetris)
}

def calculate_score(lines_cleared, current_score):
    """Calculates the score based on lines cleared."""
    if lines_cleared in SCORE_MAP:
        return current_score + SCORE_MAP[lines_cleared]
    return current_score

def get_random_tetromino():
    """Returns a random Tetromino shape and its name."""
    shape_name = random.choice(list(TETROMINOES.keys()))
    return TETROMINOES[shape_name], shape_name

def spawn_new_piece(board):
    """Spawns a new random Tetromino at the top-center of the board.
    Returns the piece, its x, y coordinates, its name and rotation state.
    Returns None if a new piece cannot be spawned (game over condition).
    """
    piece_shapes, piece_name = get_random_tetromino()
    current_piece = piece_shapes[0] # Default to the first rotation
    current_rotation = 0

    # Calculate spawn position (top-center)
    # For pieces like 'I', the pivot might not be the visual center.
    # We'll try to center the bounding box of the piece.
    min_col = min(c for r, c in current_piece)
    max_col = max(c for r, c in current_piece)
    piece_width = max_col - min_col + 1
    spawn_x = (BOARD_WIDTH - piece_width) // 2 - min_col

    spawn_y = 0 # Start at the very top

    # Check for immediate collision (game over condition)
    for r_offset, c_offset in current_piece:
        # Ensure the check is within bounds for newly spawned piece at the very top
        # This can happen if a piece spawns and immediately collides with existing blocks
        # from a previous piece that reached the top.
        check_r, check_c = spawn_y + r_offset, spawn_x + c_offset
        if not (0 <= check_r < BOARD_HEIGHT and 0 <= check_c < BOARD_WIDTH):
            # This case should ideally not happen if spawn logic is correct
            # and pieces are within typical Tetris piece dimensions (e.g. max 4 units high/wide)
            # However, adding a safeguard.
            return None, -1, -1, None, -1 # Game Over - out of bounds at spawn (should not occur)

        if board[check_r][check_c] != 0: # Collision with existing block
            return None, -1, -1, None, -1 # Game Over

    return current_piece, spawn_x, spawn_y, piece_name, current_rotation

if __name__ == '__main__':
    board = create_board()
    display_board(board)

    new_piece, px, py, pname, prot = spawn_new_piece(board)
    if new_piece:
        print(f"Spawning new piece: {pname}")
        display_board(board, new_piece, px, py)

        # Test movement
        print("Move Right:")
        px_new, py_new = move_piece(board, new_piece, px, py, 1, 0)
        if (px_new, py_new) != (px, py):
            px, py = px_new, py_new
            display_board(board, new_piece, px, py)
        else:
            print("Cannot move right.")

        print("Move Down:")
        px_new, py_new = move_piece(board, new_piece, px, py, 0, 1)
        if (px_new, py_new) != (px, py):
            px, py = px_new, py_new
            display_board(board, new_piece, px, py)
        else:
            print("Cannot move down (or collided).")

        print("Rotate:")
        rotated_shape, new_rot, px_new = rotate_piece(board, pname, prot, px, py)
        if rotated_shape != new_piece or px_new != px :
            new_piece = rotated_shape
            prot = new_rot
            px = px_new
            display_board(board, new_piece, px, py)
        else:
            print("Cannot rotate or no valid kick.")

        # Test locking and line clearing
        # Manually place a piece to form a line
        if new_piece and pname == 'I': # Test with an I piece for simplicity
            # Move it to the bottom
            while True:
                _, py_new = move_piece(board, new_piece, px, py, 0, 1)
                if py_new == py: # cannot move further down
                    break
                py = py_new

            lock_piece(board, new_piece, px, py)
            print("Locked I piece at bottom:")
            display_board(board)

            # Manually create a full line for testing clear_lines
            # This assumes 'I' is horizontal and px allows it to fill a line
            # This test is a bit contrived and depends on the 'I' piece and its spawn.
            # A more robust test would be in a dedicated test suite.
            if py + 0 < BOARD_HEIGHT : # Ensure the piece is on board
                for c_fill in range(BOARD_WIDTH):
                    can_fill = True
                    for r_off, c_off in new_piece:
                        if py + r_off >= BOARD_HEIGHT or px + c_off + c_fill >= BOARD_WIDTH :
                             # if any part of piece is out of bound with current c_fill, then cannot fill
                             if c_off + c_fill == c_fill : # check if the current cell is part of the piece we are trying to fill
                                 can_fill = False
                                 break
                    if can_fill:
                         # Check if this cell is part of the locked 'I' piece
                         is_part_of_locked_I = False
                         for r_offset, c_offset in new_piece:
                             if (py + r_offset == BOARD_HEIGHT -1) and (px + c_offset == c_fill):
                                 is_part_of_locked_I = True
                                 break
                         if not is_part_of_locked_I: # Don't overwrite the piece itself if it's making the line
                             # only fill cells that are not part of the locked piece
                             if not (any(r_fill == py + r_offset and c_fill == px + c_offset for r_offset,c_offset in new_piece)):
                                 board[BOARD_HEIGHT-1][c_fill] = 2


            linescleared = clear_lines(board)
            if linescleared > 0:
                print(f"Cleared {linescleared} lines.")
                display_board(board)
            # else: # No need for this else, test was specific
            #     print("No lines cleared (or test setup failed).")
            pass # End of specific test block

    else:
        print("Game Over - cannot spawn new piece from initial test.")

import time # Ensure time is imported at the top level

# --- Main Game Loop ---
def game_loop():
    board = create_board()
    score = 0
    game_over = False

    current_piece, piece_x, piece_y, piece_name, piece_rotation = spawn_new_piece(board)
    if current_piece is None:
        game_over = True

    last_fall_time = time.time()
    fall_interval = 0.8 # Seconds per fall step

    print("Starting Tetris! Controls: a (left), d (right), s (down), w (rotate), q (quit)")

    while not game_over:
        display_board(board, current_piece, piece_x, piece_y)
        print(f"Score: {score}")

        # --- Handle Input (simple for now, will need better input handling) ---
        # This is a placeholder for real input handling.
        # In a real game, this would be non-blocking.
        action = None
        # Simulate input for testing the loop structure
        # In a real game, you'd use libraries like `keyboard` or `curses`.
        # For now, we'll just let it auto-fall and then spawn a new piece.

        # For manual testing via terminal:
        # try:
        #     action = input("Move (a/d/s/w/q): ").lower()
        # except EOFError: # For automated test environments
        #     action = 's' # Default to move down if no input

        # --- Automatic Piece Falling ---
        current_time = time.time()
        if current_time - last_fall_time > fall_interval:
            last_fall_time = current_time
            action = 's' # Simulate gravity

        # --- Process Action ---
        if action == 'q':
            game_over = True
            print("Quitting game.")
            continue

        if current_piece is None: # Should not happen if game_over is managed correctly
             new_piece_data = spawn_new_piece(board)
             if new_piece_data[0] is None:
                 game_over = True
                 display_board(board)
                 print(f"Final Score: {score}")
                 print("GAME OVER!")
                 continue
             current_piece, piece_x, piece_y, piece_name, piece_rotation = new_piece_data


        next_x, next_y = piece_x, piece_y
        moved = False

        if action == 'a': # Move Left
            next_x, next_y = move_piece(board, current_piece, piece_x, piece_y, -1, 0)
            if next_x != piece_x: moved = True
        elif action == 'd': # Move Right
            next_x, next_y = move_piece(board, current_piece, piece_x, piece_y, 1, 0)
            if next_x != piece_x: moved = True
        elif action == 's': # Move Down
            next_x, next_y = move_piece(board, current_piece, piece_x, piece_y, 0, 1)
            if next_y != piece_y: moved = True
        elif action == 'w': # Rotate
            rotated_shape, new_rot, kick_x = rotate_piece(board, piece_name, piece_rotation, piece_x, piece_y)
            if rotated_shape != current_piece or kick_x != piece_x :
                current_piece = rotated_shape
                piece_rotation = new_rot
                piece_x = kick_x
                # No change in y for rotation typically, but collision check handles it.
                # We don't set 'moved' for rotation unless it also moved x due to kick.
                # The display will update anyway.
            action = None # Consume rotation action

        if moved:
            piece_x, piece_y = next_x, next_y
            action = None # Consume move action

        # --- Check for landing ---
        if action == 's' and next_y == piece_y and not moved : # Tried to move down but couldn't
            lock_piece(board, current_piece, piece_x, piece_y)
            lines_cleared = clear_lines(board)
            if lines_cleared > 0:
                score = calculate_score(lines_cleared, score)
                print(f"Cleared {lines_cleared} lines! Score: {score}")

            current_piece, piece_x, piece_y, piece_name, piece_rotation = spawn_new_piece(board)
            if current_piece is None:
                game_over = True
                display_board(board) # Show final board state
                print(f"Final Score: {score}")
                print("GAME OVER!")

        if not game_over: # brief pause for visibility
            time.sleep(0.05) # Small delay to make game playable in terminal

    if game_over:
        print("Exiting game loop.")


if __name__ == '__main__':
    import time # Make sure time is imported for the main block if not already global
    # The previous test code is now largely superseded by the game_loop
    # board = create_board()
    # display_board(board)
    # new_piece, px, py, pname, prot = spawn_new_piece(board)
    # ... (rest of old test code) ...
    game_loop()
