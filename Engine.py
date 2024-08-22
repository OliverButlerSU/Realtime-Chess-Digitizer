from ImageToChessboard import ImageToChessboard
from ChessBoardCorners import ChessBoardCorners
from LegalMoveDetector import LegalMoveDetector
from Camera import Camera
import chess
import numpy as np
import cv2


class Engine:

    chessboard_converter = ImageToChessboard()
    chessboard_corners = ChessBoardCorners()
    legal_move_detector = LegalMoveDetector()
    camera = Camera()

    def __init__(self):
        self.chessboard_converter = ImageToChessboard()
        self.chessboard_corners = ChessBoardCorners()
        self.legal_move_detector = LegalMoveDetector()
        self.Camera = Camera()

    # Set up the initial board corners of the chess board
    def automatically_detect_board_corners(self, show = False):
        try:
            board_image = self.camera.capture_frame_from_camera()

            # Get all hough transform lines from the image
            lines = self.chessboard_corners.hough_transform_lines(board_image)

            # Unify lines twice (just ensures all lines are properly unified on a second pass)
            unified_lines = self.chessboard_corners.unify_lines(lines, rho_threshold=30, theta_threshold=np.pi / 180 * 15)
            unified_lines = self.chessboard_corners.unify_lines(unified_lines, rho_threshold=30, theta_threshold=np.pi / 180 * 15)

            # Get all horizontal / vertical lines
            line_a, line_b = self.chessboard_corners.segment_lines_by_angle(unified_lines, theta_threshold=np.pi / 180 * 10)

            # Get all intersections of those hoz/vert lines
            int_points = self.chessboard_corners.get_intersections_of_hoz_vert_lines(line_a, line_b, board_image)

            # Get all outer corner points of the image
            p1, p2, p3, p4 = self.chessboard_corners.get_chessboard_corner_points(int_points)
            p1 = (p1[0], p1[1])
            p2 = (p2[0], p2[1])
            p3 = (p3[0], p3[1])
            p4 = (p4[0], p4[1])

            self.chessboard_corners.chessboard_corners = [p1, p2, p3, p4]

            self.show_images([self.chessboard_corners.apply_int_points(
                self.chessboard_corners.apply_hoz_vert_lines(board_image, line_a, line_b)
                , [p1, p2, p3, p4])])


            if(show):
                # Images below
                adaptive_image = self.chessboard_corners.apply_adaptive_threshold(board_image)
                hough_transform_image = self.chessboard_corners.apply_lines(board_image, lines)
                unified_lines_image = self.chessboard_corners.apply_lines(board_image, unified_lines)
                hoz_vert_image = self.chessboard_corners.apply_hoz_vert_lines(board_image, line_a, line_b)
                points_image = self.chessboard_corners.apply_int_points(hoz_vert_image, int_points)
                chess_corners_image = self.chessboard_corners.apply_int_points(board_image, [p1,p2,p3,p4])

                images = [adaptive_image, board_image, hough_transform_image, unified_lines_image, hoz_vert_image, points_image, chess_corners_image]

                self.show_images(images)


        except Exception:
            raise Exception("The corners of the image could not be identified. It is likely the board was not present"
                            "in the image, or an error occurred in calculation")

    # Set up an initial board using a starting image of the board. The FEN information must be inputted by the
    # user, but defaults to white playing the start of a game.
    def get_start_game_from_image(self, fen_information=("w", "KQkq", "-", "0", "0")):
        try:
            warped_image = self.get_rotated_warped_board_image()

            # Get the occupation and piece types
            occupations, pieces = self.chessboard_converter.get_initial_state_of_game(warped_image)

            # next_player: must be w or b
            # castles: could include k q K Q or be "-"
            # en_passant: square which en passant could be possible (e.g. e3) "-" if none
            # move_rule: number between 0-99 representing 50 move rule
            # full_move: number of "full moves" incrementing on black

            print("The board was recognised as: \n")
            self.print_board(pieces)

            if(not self.chessboard_converter.is_board_valid(occupations, pieces)):
                raise Exception("The board supplied is likely not a valid setup")


            next_player, castles, en_passant, move_rule, full_move = fen_information
            fen = self.chessboard_converter.convert_board_to_fen(pieces, next_player, castles, en_passant, move_rule,
                                                                 full_move)


            board = chess.Board(fen)

            return occupations, board
        except Exception as e:
            raise Exception("Unable to get a game from the image given")

        # Set up an initial board using a starting image of the board. The FEN information must be inputted by the
        # user, but defaults to white playing the start of a game.
    def get_start_game_from_image_GUI(self, fen_information=("w", "KQkq", "-", "0", "0")):
        try:
            warped_image = self.get_rotated_warped_board_image()

            # Get the occupation and piece types
            occupations, pieces = self.chessboard_converter.get_initial_state_of_game(warped_image)

            # next_player: must be w or b
            # castles: could include k q K Q or be "-"
            # en_passant: square which en passant could be possible (e.g. e3) "-" if none
            # move_rule: number between 0-99 representing 50 move rule
            # full_move: number of "full moves" incrementing on black

            print("The board was recognised as: \n")
            self.print_board(pieces)

            next_player, castles, en_passant, move_rule, full_move = fen_information
            fen = self.chessboard_converter.convert_board_to_fen(pieces, next_player, castles, en_passant,
                                                                 move_rule,
                                                                 full_move)

            board = chess.Board(fen)

            return occupations, board
        except Exception as e:
            raise Exception("Unable to get a game from the image given")


    def get_start_game_from_default(self):
        board = chess.Board()
        occ_board = self.legal_move_detector.calculate_occ_board_from_game_board(board)
        return (board, occ_board)


    # Play a move using a new image of a new move
    def play_move(self, board, old_occ_board, console_version = True):

        warped_image = self.get_rotated_warped_board_image()
        # Calculate the new occupations and store the piece images as well. Calculate the move that was played
        (new_occ_board, piece_images) = self.legal_move_detector.get_occupations_and_piece_images_from_image(warped_image)


        move = self.legal_move_detector.calculate_move(board, old_occ_board, new_occ_board, piece_images, console_version)


        # If the move is invalid, throw an exception
        if move is None:
            print("The move played could not be calculated, below is the occupation boards to debug:")
            self.print_board(old_occ_board)
            self.print_board(new_occ_board)
            raise Exception(
                "The move was unable to be calculated. The move is either illegal, or was not correctly classified")

        print("Detected move as: " + move)


        # If the move is valid, and legal, play the move, else throw an exception
        if self.is_move_legal(board, move):
            board.push(chess.Move.from_uci(move))
            return board, new_occ_board

        print("Error: The move was illegal to play")
        raise Exception("That move played was not legal")

    # Calculate if a move is legal to play
    def is_move_legal(self, board, move):
        return chess.Move.from_uci(move) in board.legal_moves

    def print_board(self, board):
        for i in range(len(board)):
            print(board[i])

    def get_rotated_warped_board_image(self):
        board_image = self.camera.capture_frame_from_camera()
        # Warp the board image using the initial corner points
        corner_points = self.chessboard_corners.chessboard_corners
        warped_image = self.chessboard_corners.warp_image(board_image, corner_points)
        rotated_image = self.camera.rotate_image(warped_image)

        return rotated_image

    def get_coloured_rotated_warped_board_image(self):
        board_image = self.camera.capture_colored_frame_from_camera()
        # Warp the board image using the initial corner points
        corner_points = self.chessboard_corners.chessboard_corners
        warped_image = self.chessboard_corners.warp_image(board_image, corner_points)
        rotated_image = self.camera.rotate_image(warped_image)
        return rotated_image

    def get_camera(self, console=True):
        cameras = self.camera.get_all_cameras()
        if console:
            print(cameras)
            while True:
                try:
                    inp = int(input("Input which camera device you would like:\n"))
                    if(inp >= 0 and len(cameras) - inp - 1 >= 0):
                        break
                    print("Invalid camera please input a new camera device")
                except ValueError:
                    print("Invalid camera please input a new camera device")
            return inp
        else:
            return cameras

    def manually_get_chessboard_corners(self, show=False):
        points, board_image = self.camera.get_four_corners_camera()

        if(show):
            # Images below
            chess_corners_image = self.chessboard_corners.apply_int_points(board_image, points)
            warped_image = self.chessboard_corners.warp_image(board_image, points)
            self.show_images([chess_corners_image, warped_image])

        self.chessboard_corners.chessboard_corners=points

    def show_images(self, images):
        for image in images:
            cv2.imshow("Board Image", image)
            cv2.setWindowProperty("Board Image", cv2.WND_PROP_TOPMOST, 1)
            cv2.waitKey(0)
            cv2.destroyWindow("Board Image")

    def setup_camera_rotations(self):
        board_image = self.camera.capture_frame_from_camera()
        corner_points = self.chessboard_corners.chessboard_corners

        func = (lambda x : self.chessboard_corners.warp_image(x, corner_points))

        self.camera.setup_rotations(func)








