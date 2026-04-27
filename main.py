# main.py

from game.board import Board


# ---------------------------
# INPUT HELPERS
# ---------------------------

def input_move():
    try:
        r, c = map(int, input("Enter move (row col): ").split())
        return (r - 1, c - 1)
    except:
        return None


def input_block():
    try:
        print("Enter two cells to block:")
        r1, c1 = map(int, input("Cell 1 (row col): ").split())
        r2, c2 = map(int, input("Cell 2 (row col): ").split())
        return (r1 - 1, c1 - 1), (r2 - 1, c2 - 1)
    except:
        return None, None


# ---------------------------
# GAME LOOP
# ---------------------------

def play():
    board = Board()
    state = board.state

    player = 1  # 1 = Blue, 2 = Red

    print("Knight Invasion Game Started!")
    print("Player 1 (Blue): Top → Bottom")
    print("Player 2 (Red): Bottom → Top")

    while True:
        board.display()

        # Check winner
        winner = state.check_winner()
        if winner:
            print(f"🎉 Player {winner} wins!")
            break

        print(f"\nPlayer {player}'s turn")

        moves = state.get_moves(player)

        # ----------------------------------
        # MUST MOVE (Fire Rule)
        # ----------------------------------
        if state.must_move(player):
            print("⚠ You are near fire! You MUST move.")
            print("Available moves:", [(r+1, c+1) for r, c in moves])

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

            # If no block possible → force move
            if not state.block_possible():
                print("⚠ No valid block possible → You must move")
                print("Available moves:", [(r+1, c+1) for r, c in moves])

                while True:
                    move = input_move()
                    if move in moves:
                        state.apply_move(player, move)
                        break
                    print("Invalid move. Try again.")

            else:
                choice = input("Choose action (1/2): ")

                # ---------- MOVE ----------
                if choice == '1':
                    print("Available moves:", [(r+1, c+1) for r, c in moves])

                    while True:
                        move = input_move()
                        if move in moves:
                            state.apply_move(player, move)
                            break
                        print("Invalid move. Try again.")

                # ---------- BLOCK ----------
                elif choice == '2':
                    while True:
                        c1, c2 = input_block()

                        if c1 is None:
                            print("Invalid input. Try again.")
                            continue

                        if state.apply_block(player, c1, c2):
                            break
                        else:
                            print("Invalid block (violates rules). Try again.")

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