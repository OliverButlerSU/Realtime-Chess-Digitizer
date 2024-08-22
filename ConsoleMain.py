import chess

from ChessAI import ChessAI
from Engine import Engine


engine = Engine()

def main_menu():
    print("Welcome to the chess recognition program. To start, please select what mode you would like to play with.")

    user_input = get_user_menu_input("1. Play a game using a camera \n"
                                     "2. Play a game in the console \n", 2)

    if (user_input == 1):
        camera_games()
    else:
        manual_games()


def get_user_menu_input(message, numbers):
    while True:
        try:
            print(message)
            user_input = int(input())
            if(user_input > 0 and user_input <= numbers):
                return user_input
        except Exception:
            print("That was an invalid input, please try again\n")


def camera_games():
    engine = Engine()
    engine = setup_camera_menu(engine)

    print("Would you either like to:")
    user_input = get_user_menu_input("1. Start a game from default \n"
                                     "2. Start a game using the camera \n"
                                     "3. Return to main menu", 3)

    if(user_input == 1):
        board, occ_board = engine.get_start_game_from_default()
    elif(user_input==3):
        main_menu()
    else:
        while (True):
            print("Who's turn is next: ")
            user_input = get_user_menu_input("1. White \n2. Black", 2)

            if(user_input == 1):
                player_to_move = "w"
            else:
                player_to_move = "b"

            print("Press enter once you setup the board:")
            try:
                board, occ_board = engine.get_start_game_from_image(fen_information=(player_to_move, "KQkq", "-", "0", "0"))
            except Exception:
                print("The board could not be translated or was not a valid starting position, would you like to: ")
                user_input_2 = get_user_menu_input("1. Try again \n"
                                                   "2. Start a default game \n"
                                                   "3. Go to main menu", 3)
                if(user_input_2 == 2):
                    board, occ_board = engine.get_start_game_from_default()
                    break


    print("Select the mode to play:")
    user_input_2  = get_user_menu_input("1. Against an IRL opponent \n"
                                     "2. Against an AI\n"
                                     "3. Return to main menu", 3)

    if(user_input_2 == 1):
        while (not board.is_game_over()):
            board, occ_board = get_camera_player_move(engine, board, occ_board)
    elif(user_input_2 == 3):
        main_menu()
    else:
        chess_ai = ChessAI(board)
        while(not board.is_game_over()):
            if(board.turn):
                board, occ_board = get_camera_player_move(engine, board, occ_board)
            else:
                board, occ_board = get_ai_player_move(engine, board, chess_ai)

    display_board(board)
    print(get_game_outcome(board))
    print("Returning to main menu:")
    main_menu()


def setup_camera_menu(engine):
    engine.camera.camera = engine.get_camera()


    print("\nNext setup the board position relative to the camera. Either:")

    while True:

        user_input = get_user_menu_input("1. Manually select the four corners of the board "
                                     "\n2. Automatically detect the corners of the board\n", 2)

        if (user_input == 1):
            engine.manually_get_chessboard_corners(show=False)
            engine.show_images([engine.get_rotated_warped_board_image()])
        else:
            engine.automatically_detect_board_corners(show=False)
            engine.show_images([engine.get_rotated_warped_board_image()])

        user_input = get_user_menu_input("\nConfirm the corners were correctly identified:"
                                         "\n1. Yes "
                                         "\n2. No \n", 2)
        if (user_input == 1):
            break
        else:
            print("\nPlease reselect the option you would like to use. If the automatic detection did not work,"
                  "you will likely need to manually select the corners\n")
            engine.camera.rotation = 0



    print("Now rotate the image by clicking on the image to rotate such that white is on the bottom "
          "(a1 being on the bottom left corner). Press \"Enter\" to exit once you rotate appropriately.")

    while True:
        engine.setup_camera_rotations()

        print("\nConfirm the camera was correctly rotated:")
        user_input = get_user_menu_input("1. Yes "
                                         "\n2. No \n", 2)
        if (user_input == 1):
            break
        else:
            print("\nPlease rotate the camera correctly, ensuring the a1 square is ath the bottom left corner."
                  "Press \"Enter\" to exit once you rotate appropriately.")
    return engine


def get_camera_player_move(engine, board, occ_board):
    player_turn = "White" if board.turn else "Black"

    while(True):
        try:
            display_board(board)
            move = input(player_turn + " to move, press enter once you play your move, or type exit to go back to main menu:").strip()
            if(move == "exit"): main_menu()
            board, occ_board = engine.play_move(board, occ_board)
            return board, occ_board
        except Exception:
            print("\n")
            print("Could not accurately detect the board move. It was either the move was illegal or the program "
                  "could not detect the move played. Please try again")


def get_ai_player_move(engine, board, chess_ai):

    print("Calculating AI move:")
    move, score = chess_ai.get_ai_move()

    print("The AI chose to play", move)

    board.push(move)

    occ_board = engine.legal_move_detector.calculate_occ_board_from_game_board(board)

    return board, occ_board


def manual_games():
    print("\nSelect the mode to play:")
    user_input = get_user_menu_input("1. Against an IRL opponent \n"
                                     "2. Against an AI\n"
                                     "3. Return to main menu", 3)

    board = chess.Board()

    if(user_input == 3):
        main_menu()
    elif(user_input == 1):
        while(not board.is_game_over()):
            display_board(board)
            move = get_user_move(board)
            if(move == "exit"): main_menu()
            board.push(move)
    else:
        chess_ai = ChessAI(board)
        while(not board.is_game_over()):
            display_board(board)
            player_turn = "White" if board.turn else "Black"
            if(player_turn == "White"):
                move = get_user_move(board)
                if (move == "exit"): main_menu()
            else:
                print("Calculating AI move:")
                move, score = chess_ai.get_ai_move()
                print("Playing: ", move)
            board.push(move)
    display_board(board)
    print(get_game_outcome(board))
    print("Returning to main menu:")
    main_menu()


def get_user_move(board):
    player_turn = "White" if board.turn else "Black"
    print(player_turn, "to move, input your move below, or type exit to go to main menu:")

    while True:
        try:
            move = input().lower().strip()
            if(move == "exit"): return move
            move = chess.Move.from_uci(move)
            if(move in board.legal_moves):
                return move
            else:
                print("Illegal move performed, please input again:")
        except Exception:
            print("The move could not be parsed. Please try again")


def get_game_outcome(board):
    turn = "Black" if board.turn else "White"
    if (board.is_checkmate()):
        return "Game over. " + turn + " wins by checkmate"
    else:
        return "Game over due to draw"


def display_board(board):
    print("")
    i = 0
    for i in range(8):
        string = str(8 - i)
        for j in range(8):
            string+= " "
            piece = board.piece_at((7-i) * 8 + j)
            if(piece != None):
                string+= str(piece.symbol())
            else:
                string += "."
        print(string)
    print("  a b c d e f g h")
    print("\n")


if __name__ == "__main__":
    main_menu()


#TODO LIKELY:
# - Record games to games folder

#TODO: Unlikely to do:
# - Multithread camera
# - Multithread AI
# - Multiplayer?
# - Stockfish