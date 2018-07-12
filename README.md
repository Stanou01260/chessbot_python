# Chessbot

This chess bot can play automatically as white or black on lichess.com, chess.com, chess24.com and theoretically any website using drag and drop to move pieces. It uses stockfish engine to process moves, mss to do fast screenshots, pyautogui to move the mouse, chess to store and test the moves, and opencv to detect the chessboard. It has been written only with python. 

About the bot level, it beats easily chess.com computer on level 8/10 (around 2000 ELO) when taking 1.2 second per move and crushes every human opponent on any time format longer than 1 minute.

This bot has been developped on iOS, but all the librairies it is using are compatible on Linux and Windows too. 


## Getting Started

### Prerequisites

#### Stockfish:

This bot uses stockfish to calculate the next best move. Here is the procedure to make it work :

* Download stockfish for mac os (https://stockfishchess.org/download/)
* Add it to your path with : ```export PATH=$PATH:$(pwd)````
* Test that stockfish is working well by running the command ```stockfish``` in your terminal. It should output somthing like this: ```Stockfish 120218 64 by T. Romstad, M. Costalba, J. Kiiski, G. Linscott```

#### Python:

This bot requires python 3 to run

### Using the bot:

The bot runs very easily:
* go in the folder that contains the source code
* Run the command ```python3 main.py```

### Limitations:

This project is far from perfect yet, it has a few limitations :
* Because of the computer vision algorithm used to detect the chessboard, the square colors should be with plain colors, without having original textures.
* The GUI is still quite basic
* One small deviation during a game (the board moved, the user touched the mouse...) and the bot will not work at all.
* It is not possible to stop the chessbot without closing the window

## Author

**Stanislas Heili** - *Initial work* - [myGit](https://github.com/Stanou01260/)
