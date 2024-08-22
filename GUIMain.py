import sys
from Assets.Button import Button
from Assets.Dropdown import DropDown
from BoardGUI import BoardGUI
import pygame
import easygui

import chess
from ChessAI import ChessAI
from Engine import Engine


engine = Engine()
pygame.init()

SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Chess Menu")
BACKGROUND = pygame.image.load("assets/Background.png")

BUTTON_COLOUR = "White"
BUTTON_HOVER_COLOR = "Yellow"


def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)


def setup_camera_menu():
    SCREEN.fill("black")
    SCREEN.blit(BACKGROUND, (0, 0))

    MENU_TEXT = get_font(45).render("SETUP CAMERA", True, "White")
    MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

    GUIDE_TEXT_1 = get_font(15).render("Select the camera using the dropdown menu. Once selected,", True, "White")
    GUIDE_TEXT_2 = get_font(15).render(" click the button to setup the board position by either", True, "White")
    GUIDE_TEXT_3 = get_font(15).render(" manually or automatically detecting the board corners", True, "White")
    GUIDE_TEXT_4 = get_font(15).render(" and rotating the image", True, "White")
    GUIDE_RECT_1 = GUIDE_TEXT_1.get_rect(center=(640, 150))
    GUIDE_RECT_2 = GUIDE_TEXT_2.get_rect(center=(640, 170))
    GUIDE_RECT_3 = GUIDE_TEXT_3.get_rect(center=(640, 190))
    GUIDE_RECT_4 = GUIDE_TEXT_4.get_rect(center=(640, 210))


    SCREEN.blit(MENU_TEXT, MENU_RECT)
    SCREEN.blit(GUIDE_TEXT_1, GUIDE_RECT_1)
    SCREEN.blit(GUIDE_TEXT_2, GUIDE_RECT_2)
    SCREEN.blit(GUIDE_TEXT_3, GUIDE_RECT_3)
    SCREEN.blit(GUIDE_TEXT_4, GUIDE_RECT_4)

    BACK_BUTTON = Button(image=None, pos=(640, 660),
                              text_input="BACK", font=get_font(40), base_color=BUTTON_COLOUR, hovering_color=BUTTON_HOVER_COLOR)


    buttons = [BACK_BUTTON]


    AUTO_BUTTON = Button(image=None, pos=(640, 550),
                         text_input="Auto", font=get_font(20), base_color=BUTTON_COLOUR,
                         hovering_color=BUTTON_HOVER_COLOR)

    MANUAL_BUTTON = Button(image=None, pos=(760, 550),
                         text_input="Manual", font=get_font(20), base_color=BUTTON_COLOUR,
                         hovering_color=BUTTON_HOVER_COLOR)

    ROTATION_BUTTON = Button(image=None, pos=(900, 550),
                         text_input="Rotate", font=get_font(20), base_color=BUTTON_COLOUR,
                         hovering_color=BUTTON_HOVER_COLOR)

    CONFIRM_BUTTON = Button(image=None, pos=(1050, 550),
                              text_input="Confirm", font=get_font(20), base_color=BUTTON_COLOUR, hovering_color=BUTTON_HOVER_COLOR)

    CORNER_BUTTONS = [MANUAL_BUTTON, AUTO_BUTTON, ROTATION_BUTTON, CONFIRM_BUTTON]

    camera_dict = engine.get_camera(console=False)
    cameras = []

    for camera in camera_dict:
        cameras.append(str(camera_dict[camera]))
    print(cameras)
    selected_camera = -1


    CAMERA_DROPDOWN = DropDown([BUTTON_COLOUR, BUTTON_HOVER_COLOR],
                               [BUTTON_COLOUR, BUTTON_HOVER_COLOR],
                               300, 230, 200, 50,
                               get_font(10),
                               "Select Camera", cameras)


    while True:
        MOUSE_POS = pygame.mouse.get_pos()

        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MOUSE_POS):
                    main_menu()
                elif(selected_camera > -1):
                    if AUTO_BUTTON.checkForInput(MOUSE_POS):
                        try:
                            engine.automatically_detect_board_corners(show=False)
                            frame = engine.camera.capture_colored_frame_from_camera()
                        except Exception:
                            easygui.msgbox("Could not accurately identify the board corners, please manually select them", "Camera Error")
                    elif MANUAL_BUTTON.checkForInput(MOUSE_POS):
                        try:
                            easygui.msgbox(
                                "Click the four corners of the board. You can click a already identified corner to remove it",
                                "How to Guide")
                            engine.manually_get_chessboard_corners(show=False)
                            frame = engine.camera.capture_colored_frame_from_camera()
                        except Exception:
                            easygui.msgbox("Could not find the camera", "Camera Error")

                    elif ROTATION_BUTTON.checkForInput(MOUSE_POS):
                        try:
                            if(engine.chessboard_corners.chessboard_corners == [(0,0), (0,0), (0,0), (0,0)]):
                                easygui.msgbox(
                                    "Please label the corners of the board first", "Board error")
                            else:
                                easygui.msgbox(
                                    "Rotate by clicking on the image. Put white on the bottom of the board. Press enter once done.",
                                    "How to Guide")
                                engine.setup_camera_rotations()
                        except Exception as e:
                            easygui.msgbox("Could not find the camera or the board has not had its corners properly labelled", "Camera Error")
                            engine.camera.rotation = 0
                    elif CONFIRM_BUTTON.checkForInput(MOUSE_POS):
                        if (engine.chessboard_corners.chessboard_corners == [(0,0), (0,0), (0,0), (0,0)]):
                            easygui.msgbox(
                                "Please label the corners of the board first and rotate the image", "Board error")
                        else:
                            engine.show_images([engine.get_rotated_warped_board_image()])
                            choice = easygui.ynbox("Confirm you have setup the camera such that the board is warped and rotated correctly"
                                          " such that white is on the bottom of the board", "Confirm", ("Yes","No"))
                            if(choice == 1):
                                select_gamemode(camera=True)





        selected_option = CAMERA_DROPDOWN.update(event_list)

        if selected_option >= 0:
            engine.chessboard_corners.chessboard_corners = [(0, 0), (0, 0), (0, 0), (0, 0)]
            CAMERA_DROPDOWN.main = CAMERA_DROPDOWN.options[selected_option]
            engine.camera.camera = selected_option
            print("Updated selected camera to option: ", selected_option)
            selected_camera = selected_option
            try:
                frame = engine.camera.capture_colored_frame_from_camera()
                py_frame = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1], "RGB")
                py_trans_frame = pygame.transform.scale(py_frame, (480, 270))
                SCREEN.blit(py_trans_frame, (600, 260))

            except Exception:
                selected_camera = -1
                engine.camera.camera = -1
                easygui.msgbox("Camera could not be found, please select a new camera", "Camera Error")


        SCREEN.fill("black")
        SCREEN.blit(BACKGROUND, (0, 0))

        for button in buttons:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)

        SCREEN.blit(MENU_TEXT, MENU_RECT)
        SCREEN.blit(GUIDE_TEXT_1, GUIDE_RECT_1)
        SCREEN.blit(GUIDE_TEXT_2, GUIDE_RECT_2)
        SCREEN.blit(GUIDE_TEXT_3, GUIDE_RECT_3)
        SCREEN.blit(GUIDE_TEXT_4, GUIDE_RECT_4)
        if(selected_camera>-1):
            for button in CORNER_BUTTONS:
                button.changeColor(MOUSE_POS)
                button.update(SCREEN)

            if (engine.chessboard_corners.chessboard_corners != [(0, 0), (0, 0), (0, 0), (0, 0)]):
                corner_frame = engine.chessboard_corners.apply_int_points(frame, engine.chessboard_corners.chessboard_corners)
                corner_py_frame = pygame.image.frombuffer(corner_frame.tostring(), frame.shape[1::-1], "RGB")
                corner_py_trans_frame = pygame.transform.scale(corner_py_frame, (480, 270))
                SCREEN.blit(corner_py_trans_frame, (600, 260))
            else:
                SCREEN.blit(py_trans_frame, (600, 260))




        CAMERA_DROPDOWN.draw(SCREEN)

        pygame.display.update()


def setup_camera_game_from_image(ai):
    board = chess.Board()
    gui_board = BoardGUI(board)

    try:
        frame = engine.get_coloured_rotated_warped_board_image()
        py_frame = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1], "RGB")
        py_trans_frame = pygame.transform.scale(py_frame, (400, 400))
    except Exception as e:
        print(repr(e))
        easygui.msgbox("Could not find the camera. Please plug the camera back in and try again", "Camera Error")
        setup_camera_menu()

    BACK_BUTTON = Button(image=None, pos=(970, 660),
                         text_input="BACK TO SELECT", font=get_font(40), base_color=BUTTON_COLOUR,
                         hovering_color=BUTTON_HOVER_COLOR)

    SETUP_BUTTON = Button(image=None, pos=(930, 480),
                         text_input="Setup", font=get_font(20), base_color=BUTTON_COLOUR,
                         hovering_color=BUTTON_HOVER_COLOR)

    CONFIRM_BUTTON = Button(image=None, pos=(1100, 480),
                          text_input="Start Game", font=get_font(20), base_color=BUTTON_COLOUR,
                          hovering_color=BUTTON_HOVER_COLOR)

    PLAYER_DROPDOWN = DropDown([BUTTON_COLOUR, BUTTON_HOVER_COLOR],
                               [BUTTON_COLOUR, BUTTON_HOVER_COLOR],
                               755, 465, 100, 30,
                               get_font(15),
                               "Turn", ["White", "Black"])

    player_to_move = None

    easygui.msgbox("To start the process, pick the player who starts. You can manually change the board by left clicking "
                   "to change the piece, or right click to change the colour. Or you can choose to setup from the camera. Once you"
                   "are done click complete.", "Guide")



    while True:
        MOUSE_POS = pygame.mouse.get_pos()

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if(gui_board.check_for_input(MOUSE_POS)):
                    if(player_to_move is None): easygui.msgbox("Select the player to move first.", "Error")
                    elif event.button == 1:
                        board = gui_board.update_piece_board(MOUSE_POS, fen_info=(player_to_move, "KQkq", "-", "0", "0"))
                    elif event.button == 3:
                        board = gui_board.update_piece_color(MOUSE_POS, fen_info=(player_to_move, "KQkq", "-", "0", "0"))

                if BACK_BUTTON.checkForInput(MOUSE_POS):
                    menu_opt = easygui.ynbox("Are you sure wou want to go back to the selection menu", "Selection Menu")
                    if (menu_opt):
                        setup_game(ai=ai, camera=True)
                elif SETUP_BUTTON.checkForInput(MOUSE_POS):
                    if(player_to_move is None): easygui.msgbox("Select the player to move first.", "Error")
                    else:
                        try:
                            _, board = engine.get_start_game_from_image_GUI(
                                fen_information=(player_to_move, "KQkq", "-", "0", "0"))
                            frame = engine.get_coloured_rotated_warped_board_image()
                            py_frame = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1], "RGB")
                            py_trans_frame = pygame.transform.scale(py_frame, (400, 400))
                        except Exception:
                            easygui.msgbox("Error in getting the position. The camera could be at fault. Either try again or go back to the camera menu.", "Error")

                elif CONFIRM_BUTTON.checkForInput(MOUSE_POS):
                    if (gui_board.is_board_valid()):
                        if (board.is_game_over()):
                            easygui.msgbox(
                                "The board is not valid, the game is setup such that the game will end once started")
                        else:
                            choice = easygui.ynbox("Confirm you have set the board up properly and are ready to continue")
                            if (choice):
                                play_camera_game(board, ai)

        selected_option = PLAYER_DROPDOWN.update(events)
        if(selected_option > -1):
            PLAYER_DROPDOWN.main = PLAYER_DROPDOWN.options[selected_option]
            player_to_move = "w" if selected_option == 0 else "b"


        SCREEN.fill("black")
        SCREEN.blit(BACKGROUND, (0, 0))
        SCREEN.blit(py_trans_frame, (770, 60))

        for button in [BACK_BUTTON, SETUP_BUTTON, CONFIRM_BUTTON]:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)

        PLAYER_DROPDOWN.draw(SCREEN)
        gui_board.get_board_background(screen=SCREEN, board=board)

        pygame.display.update()

def play_camera_game(board, ai=False):
    occ_board = engine.legal_move_detector.calculate_occ_board_from_game_board(board)
    gui_board = BoardGUI(board)

    if(ai):
        ai = ChessAI(board)


    try:

        frame = engine.get_coloured_rotated_warped_board_image()
        py_frame = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1], "RGB")
        py_trans_frame = pygame.transform.scale(py_frame, (400, 400))
    except Exception as e:
        print(repr(e))
        easygui.msgbox("Could not find the camera. Please plug the camera back in and try again", "Camera Error")
        setup_camera_menu()

    BACK_BUTTON = Button(image=None, pos=(970, 660),
                         text_input="BACK TO MENU", font=get_font(40), base_color=BUTTON_COLOUR,
                         hovering_color=BUTTON_HOVER_COLOR)

    while True:
        MOUSE_POS = pygame.mouse.get_pos()

        if(board.is_game_over()):
            message = get_game_over_status(board)
            easygui.msgbox(message)
            main_menu()

        if(not board.turn and ai):
            ai_move, score = ai.get_ai_move()
            board.push(ai_move)
            occ_board = engine.legal_move_detector.calculate_occ_board_from_game_board(board)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MOUSE_POS):
                    menu_opt = easygui.ynbox("Are you sure wou want to go back to the main menu", "Main Menu")
                    if(menu_opt):
                        main_menu()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    try:
                        frame = engine.get_coloured_rotated_warped_board_image()
                        py_frame = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1], "RGB")
                        py_trans_frame = pygame.transform.scale(py_frame, (400, 400))
                    except Exception as e:
                        print(repr(e))
                        easygui.msgbox("Could not find the camera. Please plug the camera back in and try again",
                                       "Camera Error")
                        setup_camera_menu()
                    try:
                        board, occ_board = engine.play_move(board, occ_board, console_version=False)
                    except Exception:
                        easygui.msgbox("Illegal move played, please try again")


        SCREEN.fill("black")
        SCREEN.blit(BACKGROUND, (0, 0))
        SCREEN.blit(py_trans_frame, (770, 60))

        player_turn = "White" if board.turn else "Black"
        player_turn_text = player_turn + " to move"
        PLAYER_TEXT = get_font(20).render(player_turn_text, True, "White")
        PLAYER_RECT = PLAYER_TEXT.get_rect(center=(970, 480))

        MOVE_TEXT = get_font(15).render("Press \"Space\" to play a move", True, "White")
        MOVE_RECT = MOVE_TEXT.get_rect(center=(970, 520))

        SCREEN.blit(PLAYER_TEXT, PLAYER_RECT)
        SCREEN.blit(MOVE_TEXT, MOVE_RECT)
        for button in [BACK_BUTTON]:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)

        gui_board.get_board_background(screen=SCREEN)

        pygame.display.update()

def setup_normal_game(ai):
    board = chess.Board()
    gui_board = BoardGUI(board)


    BACK_BUTTON = Button(image=None, pos=(970, 660),
                         text_input="BACK TO MENU", font=get_font(40), base_color=BUTTON_COLOUR,
                         hovering_color=BUTTON_HOVER_COLOR)

    CONFIRM_BUTTON = Button(image=None, pos=(1100, 480),
                          text_input="Start Game", font=get_font(20), base_color=BUTTON_COLOUR,
                          hovering_color=BUTTON_HOVER_COLOR)

    PLAYER_DROPDOWN = DropDown([BUTTON_COLOUR, BUTTON_HOVER_COLOR],
                               [BUTTON_COLOUR, BUTTON_HOVER_COLOR],
                               755, 465, 100, 30,
                               get_font(15),
                               "Turn", ["White", "Black"])

    player_to_move = None

    easygui.msgbox("To start the process, pick the player who starts. Manually change the board by left clicking "
                   "to change the piece, or right click to change the colour. Once you"
                   " are done click complete.", "Guide")



    while True:
        MOUSE_POS = pygame.mouse.get_pos()

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if(gui_board.check_for_input(MOUSE_POS)):
                    if(player_to_move is None): easygui.msgbox("Select the player to move first.", "Error")
                    elif event.button == 1:
                        board = gui_board.update_piece_board(MOUSE_POS, fen_info=(player_to_move, "KQkq", "-", "0", "0"))
                    elif event.button == 3:
                        board = gui_board.update_piece_color(MOUSE_POS, fen_info=(player_to_move, "KQkq", "-", "0", "0"))

                if BACK_BUTTON.checkForInput(MOUSE_POS):
                    menu_opt = easygui.ynbox("Are you sure wou want to go back to the main menu", "Main Menu")
                    if (menu_opt):
                        main_menu()

                elif CONFIRM_BUTTON.checkForInput(MOUSE_POS):
                    if (gui_board.is_board_valid()):
                        if(board.is_game_over()):
                            easygui.msgbox("The board is not valid, the game is setup such that the game will end once started")
                        else:
                            choice = easygui.ynbox("Confirm you have set the board up properly and are ready to continue")
                            if (choice):
                                play_normal_game(board, ai)

        selected_option = PLAYER_DROPDOWN.update(events)
        if(selected_option > -1):
            PLAYER_DROPDOWN.main = PLAYER_DROPDOWN.options[selected_option]
            player_to_move = "w" if selected_option == 0 else "b"


        SCREEN.fill("black")
        SCREEN.blit(BACKGROUND, (0, 0))

        for button in [BACK_BUTTON, CONFIRM_BUTTON]:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)

        PLAYER_DROPDOWN.draw(SCREEN)
        gui_board.get_board_background(screen=SCREEN, board=board)

        pygame.display.update()

def play_normal_game(board, ai):
    gui_board = BoardGUI(board)

    if (ai):
        ai = ChessAI(board)


    BACK_BUTTON = Button(image=None, pos=(970, 660),
                         text_input="BACK TO MENU", font=get_font(40), base_color=BUTTON_COLOUR,
                         hovering_color=BUTTON_HOVER_COLOR)

    while True:
        MOUSE_POS = pygame.mouse.get_pos()

        if (board.is_game_over()):
            message = get_game_over_status(board)
            easygui.msgbox(message)
            main_menu()

        if (not board.turn and ai):
            ai_move, score = ai.get_ai_move()
            board.push(ai_move)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MOUSE_POS):
                    menu_opt = easygui.ynbox("Are you sure wou want to go back to the main menu", "Main Menu")
                    if (menu_opt):
                        main_menu()
                if(gui_board.check_for_input(MOUSE_POS)):
                    _, _, piece = gui_board.get_piece_on_board(MOUSE_POS)
                    if piece is not None:
                        gui_board.update_selected_piece(MOUSE_POS, piece)

            elif event.type == pygame.MOUSEBUTTONUP:
                gui_board.try_play_move(MOUSE_POS)
                gui_board.remove_selected_piece()

        SCREEN.fill("black")
        SCREEN.blit(BACKGROUND, (0, 0))

        player_turn = "White" if board.turn else "Black"
        player_turn_text = player_turn + " to move"
        PLAYER_TEXT = get_font(20).render(player_turn_text, True, "White")
        PLAYER_RECT = PLAYER_TEXT.get_rect(center=(970, 480))
        SCREEN.blit(PLAYER_TEXT, PLAYER_RECT)
        for button in [BACK_BUTTON]:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)

        gui_board.get_board_background(screen=SCREEN)
        gui_board.draw_dragged_piece(SCREEN, MOUSE_POS)

        pygame.display.update()

def setup_game(ai=False, camera=True):
    MENU_TEXT = get_font(70).render("SELECT START", True, "#b68f40")
    MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

    PLAY_NORMAL_BUTTON = Button(image=None, pos=(640, 300),
                                text_input="START A DEFAULT GAME", font=get_font(40), base_color=BUTTON_COLOUR,
                                hovering_color=BUTTON_HOVER_COLOR)
    PLAY_SETUP_BUTTON = Button(image=None, pos=(640, 400),
                            text_input="SETUP GAME FROM POSITION", font=get_font(40), base_color=BUTTON_COLOUR,
                            hovering_color=BUTTON_HOVER_COLOR)

    BACK_BUTTON = Button(image=None, pos=(640, 660),
                         text_input="BACK", font=get_font(40), base_color=BUTTON_COLOUR,
                         hovering_color=BUTTON_HOVER_COLOR)

    buttons = [PLAY_NORMAL_BUTTON, PLAY_SETUP_BUTTON, BACK_BUTTON]

    while True:
        MOUSE_POS = pygame.mouse.get_pos()

        for button in [PLAY_NORMAL_BUTTON, PLAY_SETUP_BUTTON, BACK_BUTTON]:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_NORMAL_BUTTON.checkForInput(MOUSE_POS):
                    board = chess.Board()
                    if(camera):
                        play_camera_game(board, ai)
                    else:
                        play_normal_game(board, ai)
                if PLAY_SETUP_BUTTON.checkForInput(MOUSE_POS):
                    if(camera):
                        setup_camera_game_from_image(ai)
                    else:
                        setup_normal_game(ai)

                if BACK_BUTTON.checkForInput(MOUSE_POS):
                    select_gamemode(camera)

        SCREEN.fill("black")
        SCREEN.blit(BACKGROUND, (0, 0))
        SCREEN.blit(MENU_TEXT, MENU_RECT)
        for button in buttons:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)
        pygame.display.update()

def select_gamemode(camera=False):
    MENU_TEXT = get_font(70).render("SELECT GAMEMODE", True, "#b68f40")
    MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

    PLAY_NORMAL_BUTTON = Button(image=None, pos=(640, 300),
                                text_input="PLAY AGAINST OPPONENT", font=get_font(40), base_color=BUTTON_COLOUR,
                                hovering_color=BUTTON_HOVER_COLOR)
    PLAY_AI_BUTTON = Button(image=None, pos=(640, 400),
                                   text_input="PLAY AGAINST AI", font=get_font(40), base_color=BUTTON_COLOUR,
                                   hovering_color=BUTTON_HOVER_COLOR)

    BACK_BUTTON = Button(image=None, pos=(640, 660),
                         text_input="BACK", font=get_font(40), base_color=BUTTON_COLOUR,
                         hovering_color=BUTTON_HOVER_COLOR)

    buttons = [PLAY_NORMAL_BUTTON, PLAY_AI_BUTTON, BACK_BUTTON]

    while True:
        MOUSE_POS = pygame.mouse.get_pos()

        for button in [PLAY_NORMAL_BUTTON, PLAY_AI_BUTTON, BACK_BUTTON]:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_NORMAL_BUTTON.checkForInput(MOUSE_POS):
                    setup_game(ai=False, camera=camera)
                if PLAY_AI_BUTTON.checkForInput(MOUSE_POS):
                    setup_game(ai=True, camera=camera)
                if BACK_BUTTON.checkForInput(MOUSE_POS):
                    if camera:
                        setup_camera_menu()
                    else:
                        main_menu()

        SCREEN.fill("black")
        SCREEN.blit(BACKGROUND, (0, 0))
        SCREEN.blit(MENU_TEXT, MENU_RECT)
        for button in buttons:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)
        pygame.display.update()


def main_menu():
    MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
    MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

    PLAY_CAMERA_BUTTON = Button(image=None, pos=(640, 300),
                                text_input="PLAY WITH CAMERA", font=get_font(40), base_color=BUTTON_COLOUR,
                                hovering_color=BUTTON_HOVER_COLOR)
    PLAY_NONCAMERA_BUTTON = Button(image=None, pos=(640, 400),
                                   text_input="PLAY WITHOUT CAMERA", font=get_font(40), base_color=BUTTON_COLOUR,
                                   hovering_color=BUTTON_HOVER_COLOR)
    QUIT_BUTTON = Button(image=None, pos=(640, 660),
                         text_input="QUIT", font=get_font(40), base_color=BUTTON_COLOUR,
                         hovering_color=BUTTON_HOVER_COLOR)

    while True:
        SCREEN.blit(BACKGROUND, (0, 0))
        MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_CAMERA_BUTTON, PLAY_NONCAMERA_BUTTON, QUIT_BUTTON]:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_CAMERA_BUTTON.checkForInput(MOUSE_POS):
                    setup_camera_menu()
                if PLAY_NONCAMERA_BUTTON.checkForInput(MOUSE_POS):
                    select_gamemode(camera=False)
                if QUIT_BUTTON.checkForInput(MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

def get_game_over_status(board):
    possible_winner = "White" if board.turn else "Black"

    if(board.is_checkmate()):
        return "Game Over. "+possible_winner+" wins by checkmate. Returning to main menu"

    if(board.is_stalemate()):
        return "Game Over. Game is drawn by stalemate. Returning to main menu"

    if(board.is_insufficient_material()):
        return "Game Over. Game is drawn by insufficient material. Returning to main menu"

    if(board.is_fifty_moves()):
        return "Game Over. Game is drawn by 75 move rule. Returning to main menu"

    if(board.can_claim_threefold_repetition()):
        return "Game Over. Game is drawn by fivefold repetition. Returning to main menu"




if __name__ == "__main__":
    main_menu()


#TODO MUST:
# - Improve piece / occ CNN

#TODO LIKELY:
# - Record games to games folder

#TODO: Unlikely to do:
# - Multithread camera
# - Multithread AI
# - Multiplayer?
# - Stockfish
# - Create a GUI