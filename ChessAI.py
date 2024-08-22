import chess
from chess import polyglot
import time
import ChessConstants


class ChessAI:
    board = None
    amount_of_moves = 1
    transposition_table = None
    length_of_table = None

    best_iter_score = None
    best_iter_move = None
    best_move = None
    best_score = None

    hit_true = 1
    hit_false = 1

    min_depth = 4
    max_depth = 20
    time_limit = 10
    current_depth_search = 0
    extra_time = 3

    stop_iteration = False
    start_time = time.time()

    # credit: https://stackoverflow.com/questions/23532449/maximum-size-of-a-dictionary-in-python
    def __init__(self, board, length_of_table=67_108_859, min_depth=4, max_depth=20, time_limit=5, extra_time=3):
        self.board = board
        self.length_of_table = length_of_table
        self.transposition_table = {}
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.extra_time = extra_time

    # |----------------|
    # |SEARCH FUNCTIONS|
    # |----------------|

    def get_opening_move(self):
        # Try to find a move in the opening dictionary (baron30)
        # If it is not in, return None (no move was found)
        try:
            move = chess.polyglot.MemoryMappedReader("models/openings/baron30.bin").weighted_choice(self.board).move
            return (move, None)
        except:
            return (None, None)

    def get_ai_move(self):
        self.amount_of_moves = 1

        # Try to find an opening move
        moves = self.get_opening_move()
        if (moves[0] is not None): return moves

        moves = self.get_ordered_moves()

        # If no moves are available (usually due to a glitch) return None
        if (len(moves) == 0):
            return (None, None)

        # If we can only do one move, don't evaluate it, just play it
        if (len(moves) == 1):
            for move in moves: return (move, None)

        # Clean the transposition table (for some reason it's filling up with bad data :/)
        # Not sure how to fix since I have no idea why it is.
        self.clean_table()

        # Perform an iterative deepening search
        self.iterative_deepening_search()

        # Return the best move, with it's score, found
        return (self.best_move, self.best_score)

    # Credit: https://www.chessprogramming.org/Iterative_Deepening
    def iterative_deepening_search(self):
        # Set alpha/beta
        alpha = ChessConstants.neg_inf
        beta = ChessConstants.pos_inf

        # Clear all best moves from previous search
        self.best_score = 0
        self.best_iter_score = 0
        self.best_move = None
        self.best_iter_move = None
        self.current_depth_search = 0

        # Set time limits
        self.stop_iteration = False
        self.start_time = time.time()

        # Perform an iterative deepening search up to the stop depth, updating the best move/score each time
        for depth in range(1, self.max_depth + 1):
            self.current_depth_search = depth
            self.negamax_search(alpha, beta, depth, 0)

            # Setting a depth / time limit
            if ((time.time() - self.start_time) > self.time_limit and self.current_depth_search >= self.min_depth):
                if (not self.stop_iteration):
                    self.best_move = self.best_iter_move
                    self.best_score = self.best_iter_score
                break

            self.best_move = self.best_iter_move
            self.best_score = self.best_iter_score

            # If mate was found, stop search (it's already best move)
            if (self.best_score > ChessConstants.mate_score - 100):
                break

    # credit to: https://www.chessprogramming.org/Alpha-Beta
    def negamax_search(self, alpha, beta, depth, plys):
        # Setting a depth / time limit (give a bit more time to search if already searching)
        if ((time.time() - self.start_time) > self.time_limit + self.extra_time and self.current_depth_search >= self.min_depth):
            self.stop_iteration = True
            return 0

        # Check for draws. Only check after 1 ply since it is too computationally heavy to do EVERY time
        if (plys == 1):
            if (self.board.is_fifty_moves() or self.board.is_insufficient_material() or self.board.can_claim_threefold_repetition()):
                return 0

        # Skips evaluating if there is a mate sequence already found faster than the current position is to a mate (if applicable)
        if (plys >= 1):
            alpha = max(alpha, -ChessConstants.mate_score + plys)
            beta = min(beta, ChessConstants.mate_score - plys)
            if (alpha >= beta):
                return alpha

        # Lookup the position in the table, return the best move if found
        entry = self.probe_transposition(depth, alpha, beta)
        if (entry[0] is not None):
            self.hit_true += 1
            if (plys == 0):
                self.best_iter_move = entry[1]["move"]
                self.best_iter_eval = entry[0]
            return entry[0]

        self.hit_false += 1

        # Base case: Once we reach the final depth, we do a quiescence search where we only look
        # at moves which involve taking a piece. Looking into research shows using the transposition table
        # in a quiescence search gives low hit rates and is not worth it
        if (depth == 0):
            # evaluation = self.evaluate_board()
            evaluation = self.quiescense_search(alpha, beta)
            return evaluation

        # Get a list of ordered moves
        moves = self.get_ordered_moves()

        # Dealing with checkmate or draws (stalemate)
        # Return ply - mate score for checkmate so we get the smallest path to checkmate, else 0
        if (len(moves) == 0):
            if (self.board.is_check()):
                # Checkmate
                return plys - ChessConstants.mate_score
            else:
                # Stalemate
                return 0

        # We set a best move / hash_flag for the transposition table
        # This will be stored such that for this position, we know what the best move is likely to be
        # so we can use it in later iterations
        negamax_move = None
        hash_flag = ChessConstants.HASH_ALPHA

        # For each legal move in the board
        for move in moves:
            # Push the board with the move and iterate to a new depth.
            # Undo the move once it has been evaluated
            self.board.push(move)
            score = - self.negamax_search(-beta, -alpha, depth - 1, plys + 1)
            self.board.pop()

            # Use a shortcut to stop evaluation if we know another move is always better
            if (score >= beta):
                self.store_transposition(depth, beta, ChessConstants.HASH_BETA, plys, move)
                return beta

            # Else, update the best score found so far with a known eval
            if (score > alpha):
                hash_flag = ChessConstants.HASH_EXACT
                alpha = score
                negamax_move = move
                if (plys == 0):
                    # If the ply depth is 0 (meaning we are at the lowest level)
                    # We should update the best move/score
                    self.best_iter_move = move
                    self.best_iter_score = score

        # Finally, store the best move found from each depth
        # This is used so we can know the best move to search first when searching again
        # But also, what the value of it is
        self.store_transposition(depth, alpha, hash_flag, plys, negamax_move)
        return alpha

    # credit to: https://www.chessprogramming.org/Quiescence_Search
    def quiescense_search(self, alpha, beta):
        # Setting a depth / time limit (give a bit more time to search if already searching)
        if ((time.time() - self.start_time) > self.time_limit + 4 and self.current_depth_search >= self.min_depth):
            self.stop_iteration = True
            return 0

        # Evaluate the board
        stand_pat = self.evaluate_board()

        # Use similar alpha beta cuttoffs
        if (stand_pat >= beta):
            return beta
        if (alpha < stand_pat):
            alpha = stand_pat

        # Order all moves but only look at captures
        moves = self.get_ordered_capture_moves()

        # Run quiescence search for each move until there is not more capture moves
        for move in moves:
            self.board.push(move)
            score = - self.quiescense_search(-beta, -alpha)
            self.board.pop()

            if (score >= beta):
                return beta
            if (score > alpha):
                alpha = score

        return alpha

    # |--------------------|
    # |Evaluation Functions|
    # |--------------------|

    # Just a simple evaluator calculating the sum of each piece
    # credit to: https://www.chessprogramming.org/Simplified_Evaluation_Function
    def evaluate_board(self):
        worth = 0
        self.amount_of_moves += 1

        # Endgame has yet to be implemented, may be done later
        endgame = False

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece is not None:
                move_worth = self.get_piece_worth(piece, square, endgame)
                worth += move_worth if piece.color else -move_worth

        color_playing = 1 if self.board.turn else -1

        return worth * color_playing

    def get_piece_worth(self, piece, square, endgame):
        # A piece is worth the amount + it's location
        return ChessConstants.piece_worths[piece.piece_type] + self.get_piece_location_worth(piece, square, endgame)

    def get_piece_location_worth(self, piece, square, endgame):
        return ChessConstants.piece_location_worths[(piece.piece_type, piece.color, endgame)][square]

    # |-------------|
    # |MOVE ORDERING|
    # |-------------|

    def get_ordered_moves(self):

        # Get all legal moves
        moves = list(self.board.legal_moves)

        # Get the possible best move from transposition
        tt_move = self.get_transposition_move()

        # If there is no move, or a collision occured such that tt_move is not a legal move
        # sort the whole array
        if (tt_move is None or tt_move not in moves):
            return list(sorted(moves, key=self.get_guessed_move_worth, reverse=True))

        # Remove the best move from the list, sort it and add it to the start of the list
        moves.remove(tt_move)
        ordered_moves = list(sorted(moves, key=self.get_guessed_move_worth, reverse=True))
        return [tt_move] + ordered_moves

    def get_ordered_capture_moves(self):
        moves = filter(lambda move: self.board.is_capture(move), self.board.legal_moves)
        ordered_moves = list(sorted(moves, key=self.get_guessed_move_worth, reverse=True))

        return list(ordered_moves)

    def get_guessed_move_worth(self, move):
        guessed_worth = 0
        endgame = False

        piece_start = self.board.piece_at(move.from_square)
        piece_end = self.board.piece_at(move.to_square)

        # Promotions should be really good (want to ensure promoting to queen is usually better)
        if move.promotion is not None:
            guessed_worth += 10 * self.get_piece_worth(chess.Piece(move.promotion, self.board.turn), move.to_square,
                                                       endgame)

        # Capturing pieces is also great, uses MVV-LVA to weight captures from low to high (e.g. PxQ) higher
        if piece_end is not None:
            guessed_worth += ChessConstants.mvv_lva[piece_start.piece_type][piece_end.piece_type]

        # Find the change in the location of a piece
        guessed_worth += self.get_piece_location_worth(piece_start, move.to_square,
                                                       endgame) - self.get_piece_location_worth(piece_start,
                                                                                                move.from_square,
                                                                                                endgame)

        return guessed_worth

    # |--------------|
    # |TRANSPOSITIONS|
    # |--------------|

    # credit to: https://web.archive.org/web/20071031100051/http://www.brucemo.com/compchess/programming/hashing.htm
    # credit to: https://mediocrechess.blogspot.com/2007/01/guide-transposition-tables.html
    def store_transposition(self, depth, evaluation, hash_flag, ply, move):
        # Create zobrist and hash keys
        zob_key = chess.polyglot.zobrist_hash(self.board)
        hash_key = zob_key  # % self.length_of_table

        # Clean the table if it is full
        if (len(self.transposition_table) > self.length_of_table): self.clean_table()

        # Store the values
        # Need to deal with collisions later
        stored_value = {"key": zob_key, "evaluation": evaluation, "flag": hash_flag, "depth": depth, "move": move,
                        "ply": ply}
        self.transposition_table.update({hash_key: stored_value})

    def probe_transposition(self, depth, alpha, beta):
        zob_key = chess.polyglot.zobrist_hash(self.board)
        hash_key = zob_key  # % self.length_of_table

        if (hash_key not in self.transposition_table): return (None, None)

        information = self.transposition_table[hash_key]
        if (information["key"] == zob_key):
            if (information["depth"] >= depth):
                # We know the exact value of the position
                if (information["flag"] == ChessConstants.HASH_EXACT):
                    return (information["evaluation"], information)

                # We know it's at most this value (could be lower)
                if (information["flag"] == ChessConstants.HASH_ALPHA and information["evaluation"] <= alpha):
                    return (alpha, information)

                # We know it is at least this value (could be higher)
                if (information["flag"] == ChessConstants.HASH_BETA and information["evaluation"] >= beta):
                    return (beta, information)
        return (None, None)

    def clean_table(self):
        self.transposition_table = {}


    def get_transposition_move(self):
        zob_key = chess.polyglot.zobrist_hash(self.board)
        hash_key = zob_key  # % self.length_of_table

        if (hash_key not in self.transposition_table): return None

        information = self.transposition_table[hash_key]
        if (information["key"] != zob_key): return None

        return information["move"]
