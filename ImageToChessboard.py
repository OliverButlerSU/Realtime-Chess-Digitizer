from itertools import chain
import cv2
import numpy as np
from ChessImageClassifier import ChessImageClassifier
import operator as op


class ImageToChessboard:

    chess_image_classifier = None

    def __init__(self):
        self.chess_image_classifier = ChessImageClassifier()

    # |--------------------------------------------|
    # |CONVERTING IMAGE TO A PIECE/OCCUPATION BOARD|
    # |--------------------------------------------|

    # Get the initial state of a game using an image
    def get_initial_state_of_game(self, initial_image):
        # Divide into 8x8 blocks and get the piece images
        piece_images = self.divide_img_blocks(initial_image)
        piece_images = list(chain.from_iterable(piece_images))

        # Get the occupations and pieces
        occupations = self.chess_image_classifier.classify_occupation(piece_images)
        pieces = self.chess_image_classifier.classify_pieces(piece_images, occupations.copy())

        # Convert a 64 length 1d array into a 8x8 2d array
        return (self.convert_board_to_2d(occupations), self.convert_board_to_2d(pieces))

    # Divide an image into 8x8 blocks
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

    # |-----------|
    # |BOARD RULES|
    # |-----------|

    # Calculate if the board setup is valid
    def is_board_valid(self, occ_board, piece_board):
        # Get number of pieces and other stats
        num_pieces = self.get_occurance_of_piece('0', occ_board)
        num_black, num_white = self.get_occurance_of_piece_colour(piece_board)
        (num_b_king, num_w_king, num_b_bishop, num_w_bishop, num_b_queen, num_w_queen,
         num_b_knight, num_w_knight, num_b_pawn, num_w_pawn, num_b_rook, num_w_rook) \
            = self.get_number_of_all_pieces(piece_board)

        # There can not be more than 32 pieces on a chessboard
        if (num_pieces > 32):
            return False

        # There can be a maximum of 16 pieces for a color
        if (num_black > 16 or num_white > 16):
            return False

        # At all times we need one king of each color on the board
        if (num_b_king != 1 or num_w_king != 1):
            return False

        # For each color, the total number of pawns and queen can not exceed nine
        if (num_b_pawn + num_b_queen > 9 or num_w_pawn + num_w_queen > 9):
            return False

        # For each color, the total number of pawns and pieces except queen or king can not exceed ten
        if (num_w_pawn + num_w_rook > 10 or num_w_pawn + num_w_bishop > 10 or num_w_pawn + num_w_knight > 10 or
                num_b_pawn + num_b_rook > 10 or num_b_pawn + num_b_bishop > 10 or num_w_pawn + num_b_knight > 10):
            return False

        # You can not have pawns in the back rank (first and last row on a chessboard)
        if (not self.check_if_pawns_are_on_valid_ranks(piece_board)):
            return False

        return True

    # Get the occurrence of a piece from a board
    def get_occurance_of_piece(self, piecename, board):
        return sum(list(map(lambda row: op.countOf(row, piecename), board)))

    # Get the occurrence of a piece color from a board
    def get_occurance_of_piece_colour(self, board):
        black = 0
        white = 0
        for row in range(8):
            for col in range(8):
                if (board[row][col].isupper()):
                    white += 1
                elif (board[row][col] != '.'):
                    black += 1
        return (black, white)

    # Check if the pawns are on a valid rank
    def check_if_pawns_are_on_valid_ranks(self, board):
        for col in range(8):
            # Pawns cannot be on the 1st or 8th rank
            if (board[0][col].lower() == 'p'):
                return False
            elif (board[7][col].lower() == 'p'):
                return False
        return True

    # Get the number of all pieces
    def get_number_of_all_pieces(self, board):
        num_b_king = self.get_occurance_of_piece('k', board)
        num_w_king = self.get_occurance_of_piece('K', board)
        num_b_bishop = self.get_occurance_of_piece('b', board)
        num_w_bishop = self.get_occurance_of_piece('B', board)
        num_b_queen = self.get_occurance_of_piece('q', board)
        num_w_queen = self.get_occurance_of_piece('Q', board)
        num_b_knight = self.get_occurance_of_piece('n', board)
        num_w_knight = self.get_occurance_of_piece('N', board)
        num_b_pawn = self.get_occurance_of_piece('p', board)
        num_w_pawn = self.get_occurance_of_piece('P', board)
        num_b_rook = self.get_occurance_of_piece('r', board)
        num_w_rook = self.get_occurance_of_piece('R', board)
        return (num_b_king, num_w_king, num_b_bishop, num_w_bishop, num_b_queen, num_w_queen, num_b_knight,
                num_w_knight, num_b_pawn, num_w_pawn, num_b_rook, num_w_rook)

    # |-------------|
    # |FEN GENERATOR|
    # |-------------|

    # Convert a board to FEN, description of FEN can be found in report
    def convert_board_to_fen(self, board, next_player, castles, en_passant, move_rule, full_move):
        fen = ""
        for row in range(8):
            space_between_pieces = 0
            for col in range(8):
                piece = board[row][col]
                if (piece == '.'):
                    space_between_pieces += 1
                else:
                    if (space_between_pieces == 0):
                        fen += piece
                    else:
                        fen += str(space_between_pieces)
                        space_between_pieces = 0
                        fen += piece
            if (space_between_pieces != 0):
                fen += str(space_between_pieces)
            fen += "/"
        fen = fen[:-1]

        fen += " " + next_player + " " + castles + " " + en_passant + " " + move_rule + " " + full_move

        return fen
