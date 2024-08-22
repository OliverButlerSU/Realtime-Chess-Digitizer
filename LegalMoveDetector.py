import chess
import cv2
import easygui
import numpy as np
from itertools import chain
from ChessImageClassifier import ChessImageClassifier
import ChessConstants


class LegalMoveDetector:
    image_classifier = ChessImageClassifier()

    def __init__(self):
        self.image_classifier = ChessImageClassifier()

    # Calculate the difference in the old and new occupation board
    def calculate_difference_in_occ_boards(self, old_occ_board, new_occ_board):
        old_occupying_space = []
        new_occupying_space = []
        for row in range(8):
            for col in range(8):
                if (old_occ_board[row][col] != new_occ_board[row][col]):
                    if (old_occ_board[row][col] == '0'):
                        old_occupying_space.append((row, col))
                    else:
                        new_occupying_space.append((row, col))

        return (old_occupying_space, new_occupying_space)

    # Get the occupations and piece images from the board image
    def get_occupations_and_piece_images_from_image(self, image):
        # Divide the image into 8x8
        piece_images = self.divide_img_blocks(image)

        # Get the piece images and occupations
        piece_images = list(chain.from_iterable(piece_images))
        occupations = self.image_classifier.classify_occupation(piece_images)

        return (self.convert_board_to_2d(occupations), self.convert_board_to_2d(piece_images))

    def calculate_occ_board_from_game_board(self, board):
        occ_board = [['.']*8 for i in range(8)]

        for i in range(0, 64):
            if(board.piece_at(i) is not None):
                row = 7 - (i // 8)
                col = (i % 8)
                occ_board[row][col] = "0"

        return occ_board

    # Calculate the move played from an image
    def calculate_move(self, board, old_occ_board, new_occ_board, piece_images, console_version = True):
        # Move are in UCI format (originalsquare)(newSquare)(promotion?)
        # e.g. e2e4 or d7d8q promotes to queen
        # https://page.mi.fu-berlin.de/block/uci.htm

        row_to_char = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

        # Getting the difference in squares to see what moved
        old_occ_squares, new_occ_squares = self.calculate_difference_in_occ_boards(old_occ_board, new_occ_board)

        # No move was played
        if(len(old_occ_squares) == 0 and len(new_occ_squares) == 0):
            return

        # Standard Move (only 1 square moved to a new square meaning it just moved to a new spot)
        if (len(old_occ_squares) == 1 and len(new_occ_squares) == 1):
            original_square = row_to_char[old_occ_squares[0][1]] + str(8 - old_occ_squares[0][0])
            new_square = row_to_char[new_occ_squares[0][1]] + str(8 - new_occ_squares[0][0])

            promotion = self.check_for_promotion(board, old_occ_squares, new_occ_squares, piece_images, console_version)
            if (promotion is None): return None

            return original_square + new_square + promotion

        # Piece was taken (the old square moved to an already occupied square taking a piece)
        elif (len(old_occ_squares) == 1 and len(new_occ_squares) == 0):
            new_occ_squares = self.find_new_square_for_attacking_piece(board, old_occ_squares, piece_images)
            if (new_occ_squares is None): return None

            original_square = row_to_char[old_occ_squares[0][1]] + str(8 - old_occ_squares[0][0])
            new_square = row_to_char[new_occ_squares[0][1]] + str(8 - new_occ_squares[0][0])

            promotion = self.check_for_promotion(board, old_occ_squares, new_occ_squares, piece_images, console_version)
            if(promotion is None): return None

            return original_square + new_square + promotion

        # En Passant
        elif (len(old_occ_squares) == 2 and len(new_occ_squares) == 1):
            enpassant_move = self.check_for_enpassant(old_occ_squares, new_occ_squares)

            return enpassant_move

        # Castling (two squares moved in original and two in last)
        elif (len(old_occ_squares) == 2 and len(new_occ_squares) == 2):
            return self.check_castle_move(old_occ_squares, new_occ_squares)

        # No legal move was found, therefore return None
        return None

    # Check if enpassant was played
    def check_for_enpassant(self, old_occ_squares, new_occ_squares):
        row_to_char = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

        row_old_1, col_old_1 = old_occ_squares[0] # Either two pieces for old are the piece moving
        row_old_2, col_old_2 = old_occ_squares[1] # need to determine which is which

        row_new, col_new = new_occ_squares[0] # We know this will be the new position of the pawn

        if(abs(row_old_1 - row_new) == 1 and abs(col_old_1 - col_new) == 1):
            # The first piece was the piece that moved
            return row_to_char[col_old_1] + str(8-row_old_1) + row_to_char[col_new] + str(8-row_new)
        elif(abs(row_old_2 - row_new) == 1 and abs(col_old_2 - col_new) == 1):
            # The second piece was the piece that moved
            return row_to_char[col_old_2] + str(8-row_old_2) + row_to_char[col_new] + str(8-row_new)

        return None

    # Check if the move contains a promotion
    def check_for_promotion(self, board, old_occ_squares, new_occ_squares, piece_images, console_version = True):
        row_old, col_old = old_occ_squares[0]
        row_new, col_new = new_occ_squares[0]

        # If the piece moved was a pawn near either end of the board
        if (board.piece_at(8 * (7 - row_old) + col_old).piece_type == chess.PAWN and ((row_old == 1 and row_new == 0) or (row_old == 6 and row_new == 7))):
            piece = "k"

            while(piece == "p" or piece == "k"):
                # Classify the piece
                piece = self.image_classifier.classify_piece_image(piece_images[row_new][col_new]).lower()
                if (console_version):
                    print("Detected promoted piece as:", ChessConstants.piece_to_name[piece])
                    piece = self.verify_correct_piece(piece)

                else:
                    message = "Detected promoted piece as a: " + ChessConstants.piece_to_name[piece] + ". Is this correct? "
                    choice = easygui.ynbox(message, "Promotion Check")
                    if not choice:
                        piece_choice = easygui.choicebox("Click the promoted piece type:", "Promotion pieces",
                                                         ["Knight", "Bishop", "Rook", "Queen"])
                        piece = {"Knight":"n", "Bishop":"b", "Rook":"r", "Queen":"q"}[piece_choice]

                # If the piece is a king or pawn, it is not legal
                if (piece == "p" or piece == "k"):
                    if (console_version):
                        input("The promoted piece cannot be a king or pawn please input a new piece. Press enter once"
                              " you correctly update the piece")
                    else:
                        easygui.msgbox("Invalid piece promotion piece. Please try again", "Invalid promotion piece")

                else:
                    return piece

        else:
            return ""

    def verify_correct_piece(self, piece):
        while True:
            try:
                new_piece = input("Was the piece correctly identified, either press enter to confirm, or type the piece symbol wanted").strip()
                if (new_piece == "p" or new_piece == "q" or new_piece == "k" or new_piece == "n" or new_piece == "b" or new_piece == "r"):
                    return new_piece
                elif (new_piece == ""):
                    return piece
                else:
                    print("Invalid input please try again\n")
            except Exception:
                print("Invalid input please try again\n")



    # Find a square which a piece attacked
    def find_new_square_for_attacking_piece(self, board, old_occ_board, piece_images):
        attack_squares = []

        # Get the original piece
        row = old_occ_board[0][0]
        col = old_occ_board[0][1]
        original_piece = board.piece_at(8 * (7 - row) + col)

        # Get all the squares which the piece attacks
        attacks = list(board.attacks(8 * (7 - row) + col))

        # For all squares it is attacking
        for attack in attacks:
            # If the square is occupied by a piece with a difference colour
            if (board.piece_at(attack) is not None):
                possible_attack_piece = board.piece_at(attack)
                if (original_piece.color != possible_attack_piece.color):
                    attack_row = 7 - (attack // 8)
                    attack_col = (attack % 8)

                    # Get the possible piece
                    possible_piece = self.image_classifier.classify_piece_image(piece_images[attack_row][attack_col])

                    # If the new location is the same colour (we use colour as piece CNN is lower accuracy)
                    # then it is probably the piece that moved there. So add it to the array
                    if (self.is_same_colour(possible_piece, original_piece)):
                        attack_squares.append((attack_row, attack_col))

        # If more than one piece was identified as having moved to the location, there was likely an error
        # in calculating or an invalid move was performed
        if (len(attack_squares) != 1):
            return None
        return attack_squares

    # Calculate if two pieces are the same colour
    def is_same_colour(self, possible_piece, possible_attack_piece):
        return (possible_attack_piece.color and possible_piece.isupper()) or (
                (not possible_attack_piece.color) and possible_piece.islower())

    # Check for KQkq castle in that order, else return null for an invalid move
    def check_castle_move(self, old_occ_squares, new_occ_squares):
        if (old_occ_squares == [(7, 4), (7, 7)] and new_occ_squares == [(7, 5), (7, 6)]): return "e1g1"
        if (old_occ_squares == [(7, 0), (7, 4)] and new_occ_squares == [(7, 2), (7, 3)]): return "e1c1"
        if (old_occ_squares == [(0, 4), (0, 7)] and new_occ_squares == [(0, 5), (0, 6)]): return "e8g8"
        if (old_occ_squares == [(0, 0), (0, 4)] and new_occ_squares == [(0, 2), (0, 3)]): return "e8c8"
        return None

    # Split an image into 8x8 blocks
    # credit: https://stackoverflow.com/questions/5953373/how-to-split-image-into-multiple-pieces-in-python
    def divide_img_blocks(self, img, n_blocks=(8, 8)):
        # Resize the image to 998x998 so each image is around 125x125
        img = cv2.resize(img, (998, 998))

        # Split images into 8x8
        horizontal = np.array_split(img, n_blocks[0])
        splitted_img = [np.array_split(block, n_blocks[1], axis=1) for block in horizontal]
        return np.asarray(splitted_img, dtype=np.ndarray).reshape(n_blocks)

    # Convert a 64 length 1d array into a 8x8 2d array
    def convert_board_to_2d(self, board):
        board2d = []
        row = []
        for i in range(len(board)):
            row.append(board[i])
            if ((i + 1) % 8 == 0):
                board2d.append(row)
                row = []
        return board2d
