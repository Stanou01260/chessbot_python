import numpy as np
import cv2 #OpenCV
import pyautogui #Used to take screenshots and move the mouse
import chess #This is used to deal with the advancement in the game
import chess.uci #This is used to transform uci notations: for instance the uci "e2e4" corresponds to the san : "1. e4"
import random #Use the generate random numbers for processing time
import time #Used to time the executions
import mss #Used to get superfast screenshots
import os
import glob
import game_state_classes

def find_chessboard():
    #We do a first classical screenshot to see the screen size:
    screenshot_shape = np.array(pyautogui.screenshot()).shape
    monitor = {'top': 0, 'left': 0, 'width': screenshot_shape[1], 'height': screenshot_shape[0]}
    sct = mss.mss()
    img = np.array(np.array(sct.grab(monitor)))
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    is_found, current_chessboard_image,minX,minY,maxX,maxY,test_image = find_chessboard_from_image(img)
    position = game_state_classes.Board_position(minX,minY,maxX,maxY)
    return is_found, position

def get_chessboard(game_state):
    position = game_state.board_position_on_screen
    monitor = {'top': 0, 'left': 0, 'width': position.maxX + 10, 'height': position.maxY + 10}
    img = np.array(np.array(game_state.sct.grab(monitor)))
    #Converting the image in grayscale:
    image = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    dim = (800, 800 ) # perform the actual resizing of the chessboard
    resizedChessBoard = cv2.resize(image[position.minY:position.maxY, position.minX:position.maxX], dim, interpolation = cv2.INTER_AREA)
    return resizedChessBoard

def find_chessboard_from_image(img):
    #The algorithm here is much faster than the previous one:
    #1 Get the horizontal lines by convolving the image with [[-1,1]], get the indexes with the most start and end lines
    #2 Get the vertical lines by convolving the image with [[-1],[1]], get the indexes with the most start and end lines
    #3 Check if there is only one probable start and end for each dimension, and the board is squared
    #4 Resize the image to a std dimension to standardize the treatments

    #Converting the image in grayscale:
    image = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    found_board = False
        
    kernelH = np.array([[-1,1]])
    kernelV = np.array([[-1],[1]])

    #Récupération des lignes horizontales :
    lignesHorizontales = np.absolute(cv2.filter2D(image.astype('float'),-1,kernelV))
    ret,thresh1 = cv2.threshold(lignesHorizontales,30,255,cv2.THRESH_BINARY)
    
    kernelSmall = np.ones((1,3), np.uint8)
    kernelBig = np.ones((1,50), np.uint8)

    #Remove holes:
    imgH1 = cv2.dilate(thresh1, kernelSmall, iterations=1)
    imgH2 = cv2.erode(imgH1, kernelSmall, iterations=1)
    
    #Remove small lines
    imgH3 = cv2.erode(imgH2, kernelBig, iterations=1)
    imgH4 = cv2.dilate(imgH3, kernelBig, iterations=1)

    linesStarts = cv2.filter2D(imgH4,-1,kernelH)
    linesEnds = cv2.filter2D(imgH4,-1,-kernelH)

    lines = linesStarts.sum(axis=0)/255
    lineStart = 0
    nbLineStart = 0
    for idx, val in enumerate(lines):
        if val > 6:
            nbLineStart += 1
            lineStart = idx

    lines = linesEnds.sum(axis=0)/255
    lineEnd = 0
    nbLineEnd = 0
    for idx, val in enumerate(lines):
        if val > 6:
            nbLineEnd += 1
            lineEnd = idx        

    #Récupération des lignes verticales:
    lignesVerticales = np.absolute(cv2.filter2D(image.astype('float'),-1,kernelH))
    ret,thresh1 = cv2.threshold(lignesVerticales,30,255,cv2.THRESH_BINARY)
    
    kernelSmall = np.ones((3,1), np.uint8)
    kernelBig = np.ones((50,1), np.uint8)
    
    #Remove holes:
    imgV1 = cv2.dilate(thresh1, kernelSmall, iterations=1)
    imgV2 = cv2.erode(imgV1, kernelSmall, iterations=1)
    
    #Remove small lines
    imgV3 = cv2.erode(imgV2, kernelBig, iterations=1)
    imgV4 = cv2.dilate(imgV3, kernelBig, iterations=1)

    columnStarts = cv2.filter2D(imgV4,-1,kernelV)
    columnEnds = cv2.filter2D(imgV4,-1,-kernelV)

    column = columnStarts.sum(axis=1)/255
    columnStart = 0
    nbColumnStart = 0
    for idx, val in enumerate(column):
        if val > 6:
            columnStart = idx
            nbColumnStart += 1
            
    column = columnEnds.sum(axis=1)/255
    columnEnd = 0
    nbColumnEnd = 0
    for idx, val in enumerate(column):
        if val > 6:
            columnEnd = idx
            nbColumnEnd += 1


    found_board = False
    if (nbLineStart == 1) and (nbLineEnd == 1) and (nbColumnStart == 1) and (nbColumnEnd == 1) :
        print("We found a board")
        if abs((columnEnd - columnStart) - (lineEnd - lineStart)) > 3:
            print ("However, the board is not a square")
        else:
            print(columnStart,columnEnd,lineStart,lineEnd)
            if (columnEnd - columnStart) % 8 == 1:
                columnEnd -= 1
            if (columnEnd - columnStart) % 8 == 7:
                columnEnd += 1
            if (lineEnd - lineStart) % 8 == 1:
                lineStart += 1
            if (lineEnd - lineStart) % 8 == 7:
                lineStart -= 1
            print(columnStart,columnEnd,lineStart,lineEnd)

            found_board = True
    else:
        print("We did not found the borders of the board")

    if found_board:
        print("Found chessboard sized:" , (columnEnd-columnStart),(lineEnd-lineStart)," x:",columnStart,columnEnd," y: ",lineStart,lineEnd)
        dim = (800, 800 ) # perform the actual resizing of the chessboard
        print(lineStart,lineEnd,columnStart,columnEnd)
        resizedChessBoard = cv2.resize(image[columnStart:columnEnd, lineStart:lineEnd], dim, interpolation = cv2.INTER_AREA)
        return True, resizedChessBoard , lineStart, columnStart  , lineEnd   , columnEnd  , resizedChessBoard 

    return False, image, 0, 0, 0, 0 , image

def test_chessboard_detection(imageDir,expectedBoard):
    valid_image_extensions = [".jpg", ".jpeg", ".png", ".tif", ".tiff"] 
    image_count = 0
    error_count = 0
    for file in os.listdir(imageDir):
        print("\n\nTesting new file ", file)
        extension = os.path.splitext(file)[1]
        if extension.lower() not in valid_image_extensions:
            continue
        image_count = image_count+1
        image = cv2.imread(os.path.join(imageDir, file))
        found_board, resizedChessBoard , minX,minY,maxX,maxY, info_image =  find_chessboard_from_image(image)
        if found_board != expectedBoard:
            print("Error in", file)
            error_count = error_count + 1
            cv2.imwrite("Errors/Error" + repr(expectedBoard) + file,info_image)
        else:
            cv2.imwrite("Errors/NoError" + repr(expectedBoard) + file,info_image)

    #print("Had ", error_count, " error_count out of ", image_count, " images")
    return image_count,error_count

def cleanFolder(folder_name):
    files = glob.glob(folder_name)
    for f in files:
        os.remove(f)


def global_test_chessboard_detection():
    cleanFolder('Errors/*')
    
    #Images having a board
    print("\nTreating images having a board : ")
    image_count,error_count = test_chessboard_detection("TestImages/withBoard/",True)
    print("Errors with images having a board : ", 100 * error_count/image_count, "%")
    
    #Images having no board
    print("\nTreating images having no board : ")
    image_count,error_count = test_chessboard_detection("TestImages/withoutBoard/",False)
    print("Errors with images not having a board : ", 100 * error_count/image_count, "%")
    
    print("\n Please find outputs in the folder Errors/")

if __name__ == "__main__":
    global_test_chessboard_detection()