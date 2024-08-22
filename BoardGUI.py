import easygui
import pygame
import chess
import operator as op

class BoardGUI:

    selected_piece = None
    is_dragging = False
    selected_piece_location = 0
    selected_piece_row = -1
    selected_piece_col = -1

    def __init__(self, board):
        self.board = board
        self.load_piece_images()

    def update_selected_piece(self, mouse_pos, piece):
        x, y = mouse_pos
        square_size = 75
        square_offset = 60

        row = (y - square_offset) // square_size
        col = (x - square_offset) // square_size

        if(piece.color != self.board.turn): return

        self.selected_piece_location = ((7 - row) * 8 + col)
        self.is_dragging = True
        self.selected_piece = piece
        self.selected_piece_row = row
        self.selected_piece_col = col

    def draw_dragged_piece(self, screen, mouse_pos):
        if(self.is_dragging):
            piece_image = self.get_piece_from_image(self.selected_piece)
            piece_rect = piece_image.get_rect(center=mouse_pos)
            screen.blit(piece_image, piece_rect)

    def remove_selected_piece(self):
        self.is_dragging = False
        self.selected_piece = None
        self.selected_piece_location = 0
        self.selected_piece_row = -1
        self.selected_piece_col = -1

    def try_play_move(self, mouse_pos):
        try:
            if (self.is_dragging):
                x, y = mouse_pos
                square_size = 75
                square_offset = 60

                row = (y - square_offset) // square_size
                col = (x - square_offset) // square_size

                original_square = self.selected_piece_location
                new_square = ((7 - row) * 8 + col)


                if ((self.board.piece_at(original_square).symbol() == "P" or self.board.piece_at(original_square).symbol() == "p") and (row == 0 or row == 7)):
                    piece_choice = easygui.choicebox("Click the promoted piece type:", "Promotion pieces",
                                                     ["Knight", "Bishop", "Rook", "Queen"])
                    promotion = {"Knight": chess.KNIGHT, "Bishop": chess.BISHOP, "Rook": chess.ROOK, "Queen": chess.QUEEN}[piece_choice]

                    move = self.board.find_move(original_square, new_square, promotion)

                    if(move in self.board.legal_moves): self.board.push(move)
                else:
                    move = self.board.find_move(original_square, new_square)
                    if (move in self.board.legal_moves): self.board.push(move)
        except Exception:
            pass




    def load_piece_images(self):
        black_pawn = pygame.image.load(r"Assets/Chess Pieces/Chess_pdt60.png")
        black_knight = pygame.image.load(r"Assets/Chess Pieces/Chess_ndt60.png")
        black_bishop = pygame.image.load(r"Assets/Chess Pieces/Chess_bdt60.png")
        black_rook = pygame.image.load(r"Assets/Chess Pieces/Chess_rdt60.png")
        black_queen = pygame.image.load(r"Assets/Chess Pieces/Chess_qdt60.png")
        black_king = pygame.image.load(r"Assets/Chess Pieces/Chess_kdt60.png")
        white_pawn = pygame.image.load(r"Assets/Chess Pieces/Chess_plt60.png")
        white_knight = pygame.image.load(r"Assets/Chess Pieces/Chess_nlt60.png")
        white_bishop = pygame.image.load(r"Assets/Chess Pieces/Chess_blt60.png")
        white_rook = pygame.image.load(r"Assets/Chess Pieces/Chess_rlt60.png")
        white_queen = pygame.image.load(r"Assets/Chess Pieces/Chess_qlt60.png")
        white_king = pygame.image.load(r"Assets/Chess Pieces/Chess_klt60.png")

        self.piece_images = {
            # Piece, Color (True=White, False=Black)
            (chess.PAWN, True): white_pawn,
            (chess.PAWN, False): black_pawn,
            (chess.KNIGHT, True): white_knight,
            (chess.KNIGHT, False): black_knight,
            (chess.BISHOP, True): white_bishop,
            (chess.BISHOP, False): black_bishop,
            (chess.ROOK, True): white_rook,
            (chess.ROOK, False): black_rook,
            (chess.QUEEN, True): white_queen,
            (chess.QUEEN, False): black_queen,
            (chess.KING, True): white_king,
            (chess.KING, False): black_king,
        }

    def get_piece_from_image(self, piece):
        return self.piece_images[(piece.piece_type, piece.color)]


    def get_board_background(self, screen, board = None):
        if board is not None: self.board = board

        square_size = 75
        square_offset = 60

        for row in range(8):
            for col in range(8):
                if ((row+col) % 2 == 0):
                    square_color = (236,219,180)
                else:
                    square_color = (180,140,100)

                square = (col * square_size + square_offset, row * square_size + square_offset, square_size, square_size)

                pygame.draw.rect(screen, square_color, square)

                piece = self.board.piece_at((7 - row) * 8 + col)
                if piece is not None and not (self.selected_piece_row == row and self.selected_piece_col == col):
                    piece_image = self.get_piece_from_image(piece)
                    piece_rect = piece_image.get_rect(center=(col * square_size + square_offset + (square_size/2), row * square_size + square_offset + (square_size/2)))
                    screen.blit(piece_image, piece_rect)

    def check_for_input(self, mouse_pos):
        x, y = mouse_pos
        square_size = 75
        square_offset = 60

        return (x > square_offset and x <=8*square_size + square_offset and y > square_offset and y <= 8*square_size + square_offset)

    def get_piece_on_board(self, mouse_pos):
        x, y = mouse_pos
        square_size = 75
        square_offset = 60

        row = (y - square_offset) // square_size
        col = (x - square_offset) // square_size

        return row, col, self.board.piece_at((7-row) *8 + col)

    def update_piece_board(self, mouse_pos, fen_info = ("w", "KQkq", "-", "0", "0")):
        row, col, piece = self.get_piece_on_board(mouse_pos)

        piece_board = self.get_piece_board_from_game_board()

        piece_pos = piece_board[row][col]

        piece_color = piece_pos.isupper()

        piece_alloc = {
            ".": "p",
            "p": "n",
            "n": "b",
            "b": "r",
            "r": "q",
            "q": "k",
            "k": ".",
        }

        new_piece = piece_alloc[piece_pos.lower()].upper() if piece_color else piece_alloc[piece_pos.lower()]
        piece_board[row][col] = new_piece

        next_player, castles, en_passant, move_rule, full_move = fen_info

        fen = self.convert_board_to_fen(piece_board, next_player, castles, en_passant, move_rule, full_move)

        self.board = chess.Board(fen)
        return self.board



    def update_piece_color(self, mouse_pos, fen_info = ("w", "KQkq", "-", "0", "0")):
        row, col, piece = self.get_piece_on_board(mouse_pos)

        if(piece is None):
            return self.board

        piece_board = self.get_piece_board_from_game_board()

        piece_pos = piece_board[row][col]

        piece_board[row][col] = piece_pos.lower() if piece_pos.isupper() else piece_pos.upper()
        next_player, castles, en_passant, move_rule, full_move = fen_info

        fen = self.convert_board_to_fen(piece_board, next_player, castles, en_passant, move_rule, full_move)

        self.board = chess.Board(fen)
        return self.board


    def get_piece_board_from_game_board(self):
        pieces = [["."] * 8 for _ in range(8)]
        for row in range(8):
            for col in range(8):
                piece = self.board.piece_at((7-row)*8 + col)
                if(piece is not None):
                    pieces[row][col] = piece.symbol()
        return pieces

    def get_occ_board_from_game_board(self):
        pieces = [["."] * 8 for _ in range(8)]
        for row in range(8):
            for col in range(8):
                piece = self.board.piece_at((7 - row) * 8 + col)
                if (piece is not None):
                    pieces[row][col] = "0"
        return pieces


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

        # Calculate if the board setup is valid

    def is_board_valid(self):
        occ_board = self.get_occ_board_from_game_board()
        piece_board = self.get_piece_board_from_game_board()

        # Get number of pieces and other stats
        num_pieces = self.get_occurance_of_piece('0', occ_board)
        num_black, num_white = self.get_occurance_of_piece_colour(piece_board)
        (num_b_king, num_w_king, num_b_bishop, num_w_bishop, num_b_queen, num_w_queen,
         num_b_knight, num_w_knight, num_b_pawn, num_w_pawn, num_b_rook, num_w_rook) \
            = self.get_number_of_all_pieces(piece_board)

        # There can not be more than 32 pieces on a chessboard
        if (num_pieces > 32):
            easygui.msgbox("The board in invalid. You can only have 32 pieces on a board.", "Board Error")
            return False

        # There can be a maximum of 16 pieces for a color
        if (num_black > 16 or num_white > 16):
            easygui.msgbox("The board in invalid. You can only have 16 pieces per player.", "Board Error")
            return False

        # At all times we need one king of each color on the board
        if (num_b_king != 1 or num_w_king != 1):
            easygui.msgbox("The board in invalid. You can only have 1 king per player.", "Board Error")
            return False

        # For each color, the total number of pawns cannot exceed 8
        if(num_b_pawn > 8 or num_w_pawn > 8):
            easygui.msgbox("The board in invalid. You cant have the total number of pawns exceeding nine.",
                           "Board Error")

        # For each color, the total number of pawns and queen can not exceed nine
        if (num_b_pawn + num_b_queen > 9 or num_w_pawn + num_w_queen > 9):
            easygui.msgbox("The board in invalid. You cant have the total number of pawns and queens exceed nine.", "Board Error")
            return False

        # For each color, the total number of pawns and pieces except queen or king can not exceed ten
        if (num_w_pawn + num_w_rook > 10 or num_w_pawn + num_w_bishop > 10 or num_w_pawn + num_w_knight > 10 or
                num_b_pawn + num_b_rook > 10 or num_b_pawn + num_b_bishop > 10 or num_w_pawn + num_b_knight > 10):
            easygui.msgbox("The board in invalid. You cant have the total number of pawns and piece besides the queen and king exceed ten.", "Board Error")
            return False

        # You can not have pawns in the back rank (first and last row on a chessboard)
        if (not self.check_if_pawns_are_on_valid_ranks(piece_board)):
            easygui.msgbox("The board in invalid. You can't have pawns on the back rank.", "Board Error")
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


