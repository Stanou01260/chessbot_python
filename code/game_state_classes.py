import chess #This is used to deal with the advancement in the game
import chess.uci #This is used to transform uci notations: for instance the uci "e2e4" corresponds to the san : "1. e4"
import numpy as np
from board_basics import *
import chessboard_detection
import pyautogui
import cv2 #OpenCV
import mss #Used to get superfast screenshots
import time #Used to time the executions


class Board_position:
    def __init__(self,minX,minY,maxX,maxY):
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY

    def print_custom(self):
        return ("from " + str(self.minX) + "," + str(self.minY) + " to " + str(self.maxX) + ","+ str(self.maxY))

class Game_state:

    def __init__(self):
        self.we_play_white = True #This store the player color, it will be changed later
        self.moves_to_detect_before_use_engine = -1 #The program uses the engine to play move every time that this variable is 0
        self.expected_move_to_detect = "" #This variable stores the move we should see next, if we don't see the right one in the next iteration, we wait and try again. This solves the slow transition problem: for instance, starting with e2e4, the screenshot can happen when the pawn is on e3, that is a possible position. We always have to double check that the move is done.
        self.previous_chessboard_image = [] #Storing the chessboard image from previous iteration
        self.executed_moves = [] #Store the move detected on san format
        self.engine = chess.uci.popen_engine("stockfish")#The engine used is stockfish. It requires to have the command stockfish working on the shell
        self.board = chess.Board() #This object comes from the "chess" package, the moves are stored inside it (and it has other cool features such as showing all the "legal moves")
        self.board_position_on_screen = []
        self.sct = mss.mss()
    
    #This function checks if the chessboard image we see fits the moves we stored
    #The only check done right now is squares have the right emptiness.
    def can_image_correspond_to_chessboard(self, move, current_chessboard_image):
        self.board.push(move)
        squares = chess.SquareSet(chess.BB_ALL)
        for square in squares:
            row = chess.square_rank(square)
            column = chess.square_file(square)
            piece = self.board.piece_at(square)
            shouldBeEmpty = (piece == None)
                
            if self.we_play_white == True:
                #print("White on bottom",row,column,piece)
                rowOnImage = 7-row
                columnOnImage = column
            else:
                #print("White on top",row,7 - column,piece)
                rowOnImage = row
                columnOnImage = 7-column

            squareImage = get_square_image(rowOnImage,columnOnImage,current_chessboard_image)

            if is_square_empty(squareImage) != shouldBeEmpty:
                self.board.pop()
                print( "Problem with : ", self.board.uci(move) ," the square ", rowOnImage, columnOnImage, "should ",'be empty' if shouldBeEmpty else 'contain a piece')
                return False
        print("Accepted move", self.board.uci(move))
        self.board.pop()
        return True


    def get_valid_move(self, potential_starts, potential_arrivals, current_chessboard_image):
        print("Starts and arrivals:",potential_starts, potential_arrivals)

        valid_move_string = ""
        for start in potential_starts:
            for arrival in potential_arrivals:
                uci_move = start+arrival
                move = chess.Move.from_uci(uci_move)
                if move in self.board.legal_moves:
                    if self.can_image_correspond_to_chessboard(move,current_chessboard_image):#We only keep the move if the current image looks like this move happenned
                        valid_move_string = uci_move
                else:
                    uci_move_promoted = uci_move + 'q'
                    promoted_move = chess.Move.from_uci(uci_move_promoted)
                    if promoted_move in self.board.legal_moves:
                        if self.can_image_correspond_to_chessboard(move,current_chessboard_image):#We only keep the move if the current image looks like this move happenned
                            valid_move_string = uci_move_promoted
                            print("There has been a promotion to queen")
                    
        #Detect castling king side with white
        if ("e1" in potential_starts) and ("h1" in potential_starts) and ("f1" in potential_arrivals) and ("g1" in potential_arrivals):
            valid_move_string = "e1g1"

        #Detect castling queen side with white
        if ("e1" in potential_starts) and ("a1" in potential_starts) and ("c1" in potential_arrivals) and ("d1" in potential_arrivals):
            valid_move_string = "e1c1"

        #Detect castling king side with black
        if ("e8" in potential_starts) and ("h8" in potential_starts) and ("f8" in potential_arrivals) and ("g8" in potential_arrivals):
            valid_move_string = "e8g8"

        #Detect castling queen side with black
        if ("e8" in potential_starts) and ("a8" in potential_starts) and ("c8" in potential_arrivals) and ("d8" in potential_arrivals):
            valid_move_string = "e8c8"
        
        return valid_move_string

    def register_move_if_needed(self):
        #cv2.imshow('old_image',self.previous_chessboard_image)
        #k = cv2.waitKey(10000)                
        new_board = chessboard_detection.get_chessboard(self)
        potential_starts, potential_arrivals = get_potential_moves(self.previous_chessboard_image,new_board,self.we_play_white)
        valid_move_string1 = self.get_valid_move(potential_starts,potential_arrivals,new_board)
        print("Valid move string 1:" + valid_move_string1)

        if len(valid_move_string1) > 0:
            time.sleep(0.1)    
            'Check that we were not in the middle of a move animation'
            new_board = chessboard_detection.get_chessboard(self)
            potential_starts, potential_arrivals = get_potential_moves(self.previous_chessboard_image,new_board,self.we_play_white)
            valid_move_string2 = self.get_valid_move(potential_starts,potential_arrivals,new_board)
            print("Valid move string 2:" + valid_move_string2)
            if valid_move_string2 != valid_move_string1:
                return False, "The move has changed"
            valid_move_UCI = chess.Move.from_uci(valid_move_string1)
            valid_move_registered = self.register_move(valid_move_UCI,new_board) 
            return True, valid_move_string1
        return False, "No move found"
        
        

    def register_move(self,move,board_image):
        if move in self.board.legal_moves:
            print("Move has been registered")
            self.executed_moves= np.append(self.executed_moves,self.board.san(move))
            self.board.push(move)
            self.moves_to_detect_before_use_engine = self.moves_to_detect_before_use_engine - 1
            self.previous_chessboard_image = board_image
            return True
        else:
            return False

    def get_square_center(self,square_name):
        row,column = convert_square_name_to_row_column(square_name,self.we_play_white)
        position = self.board_position_on_screen
        centerX = int(position.minX + (column + 0.5) *(position.maxX-position.minX)/8)
        centerY = int(position.minY + (row + 0.5) *(position.maxY-position.minY)/8)
        return centerX,centerY

    def play_next_move(self):
        #This function calculates the next best move with the engine, and play it (by moving the mouse)
        print("\nUs to play: Calculating next move")
        self.engine.position(self.board)
        engine_process = self.engine.go(movetime=200)#random.randint(200,400))

        best_move = engine_process.bestmove
        best_move_string = best_move.uci()
        #print("Play next move")

        #print(bestMove)
        origin_square = best_move_string[0:2]
        destination_square = best_move_string[2:4]
        
        # I added custom oppenings because I was very annoyed to always see e2e4, feel free to comment or change this
        #Potentially, we could even start the bot after N moves allowing the user to see the games he want
        #Custom white openning:
        #if len(moveHistory) == 0:
        #    origin_square = "b1"
        #   destination_square = "c3"
        #if len(moveHistory) == 2 :
        #    origin_square = "c3"
        #    destination_square = "b1"
        #Custom black openning:
        #if len(moveHistory) == 1 :
        #    origin_square = "g8"
        #    destination_square = "f6"
        #if len(moveHistory) == 3 :
        #    origin_square = "f6"
        #    destination_square = "g8"

        #From the move we get the positions:
        centerXOrigin, centerYOrigin = self.get_square_center(origin_square)
        centerXDest, centerYDest = self.get_square_center(destination_square)

        #Having the positions we can drag the piece:
        pyautogui.moveTo(centerXOrigin, centerYOrigin, 0.01)
        pyautogui.dragTo(centerXOrigin, centerYOrigin + 1, button='left', duration=0.01) #This small click is used to get the focus back on the browser window
        pyautogui.dragTo(centerXDest, centerYDest, button='left', duration=0.3)

        if best_move.promotion != None:
            print("Promoting to a queen")
            #Deal with queen promotion:
            cv2.waitKey(100)
            pyautogui.dragTo(centerXDest, centerYDest + 1, button='left', duration=0.1) #Always promoting to a queen

        print("Done playing move",origin_square,destination_square)
        self.moves_to_detect_before_use_engine = 2
        return

