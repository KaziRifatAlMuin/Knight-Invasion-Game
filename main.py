# main.py

import random
from game.board import Board


# ---------------------------
# GLOBAL INPUT HANDLER (QUIT)
# ---------------------------

def get_input(prompt):
    user = input(prompt)

    if user.lower() == 'q':
        print("\nGame exited.")
        exit()

    return user


# ---------------------------
# DIFFICULTY
# ---------------------------

def choose_fire_pairs():
    print("Select Difficulty:")
    print("1. Easy")
    print("2. Medium")
    print("3. Hard")

    while True:
        choice = get_input("Enter choice: ")

        if choice == '1':
            return random.choice([3, 4, 5])   # 6–10 fires
        elif choice == '2':
            return random.choice([8, 9, 10, 11])  # 16–22 fires
        elif choice == '3':
            return random.choice([14, 15, 16, 17])  # 28–34 fires
        else:
            print("Invalid choice.")


# ---------------------------
# INPUT HELPERS
# ---------------------------

def input_move():
    try:
        user = get_input("Enter move (row col): ")
        r, c = map(int, user.split())
        return (r - 1, c - 1)
    except:
        return None


def input_cell(prompt):
    try:
        user = get_input(prompt)
        r, c = map(int, user.split())
        return (r - 1, c - 1)
    except:
        return None


def show_cells(cells):
    return [(r+1, c+1) for r, c in cells]


def get_all_empty_cells(state):
    cells = []
    for r in range(9):
        for c in range(9):
            if (
                (r, c) not in state.blocks and
                (r, c) not in state.fires and
                (r, c) != state.p1 and
                (r, c) != state.p2
            ):
                cells.append((r, c))
    return cells


# ---------------------------
# GAME LOOP
# ---------------------------

def play():
    fire_pairs = choose_fire_pairs()
    board = Board(fire_pairs)
    state = board.state

    player = 1

    print("\n🔥 Knight Invasion Game Started!")
    print("Player 1 (Blue): Top → Bottom")
    print("Player 2 (Red): Bottom → Top")
    print("Type 'q' anytime to quit the game.\n")

    while True:
        board.display()

        # Winner check
        winner = state.check_winner()
        if winner:
            print(f"🎉 Player {winner} wins!")
            break

        print(f"\nPlayer {player}'s turn")

        moves = state.get_moves(player)

        # ----------------------------------
        # MUST MOVE (FIRE RULE)
        # ----------------------------------
        if state.must_move(player):
            print("⚠ Near fire → MUST MOVE")
            print("Available moves:", show_cells(moves))

            while True:
                move = input_move()
                if move in moves:
                    state.apply_move(player, move)
                    break
                print("Invalid move. Try again.")

        # ----------------------------------
        # NORMAL TURN
        # ----------------------------------
        else:
            print("1. Move")
            print("2. Block")

            # If no valid block → force move
            if not state.block_possible():
                print("⚠ No valid block → MUST MOVE")
                print("Available moves:", show_cells(moves))

                while True:
                    move = input_move()
                    if move in moves:
                        state.apply_move(player, move)
                        break
                    print("Invalid move. Try again.")

            else:
                choice = get_input("Choose action (1/2): ")

                # ---------- MOVE ----------
                if choice == '1':
                    print("Available moves:", show_cells(moves))

                    while True:
                        move = input_move()
                        if move in moves:
                            state.apply_move(player, move)
                            break
                        print("Invalid move. Try again.")

                # ---------- BLOCK ----------
                elif choice == '2':
                    empty_cells = get_all_empty_cells(state)
                    print("Available cells:", show_cells(empty_cells))

                    # First cell
                    while True:
                        c1 = input_cell("Select first cell: ")
                        if c1 in empty_cells:
                            break
                        print("Invalid cell. Try again.")

                    # Valid second cells
                    valid_second = [
                        c for c in empty_cells
                        if c != c1 and state.can_block(player, c1, c)
                    ]

                    if not valid_second:
                        print("⚠ No valid second cell → must move")
                        continue

                    print("Valid second cells:", show_cells(valid_second))

                    while True:
                        c2 = input_cell("Select second cell: ")
                        if c2 in valid_second:
                            state.apply_block(player, c1, c2)
                            break
                        print("Invalid second cell. Try again.")

                else:
                    print("Invalid choice.")
                    continue

        # Switch player
        player = 2 if player == 1 else 1


# ---------------------------
# RUN
# ---------------------------

if __name__ == "__main__":
    play()