# Chessbot

"*Why create another chessbot ?*" The explanation is simple : I did not find a free bot I liked online : all the bots I saw on internet are parsing the html of the different websites to find the positions. But it creates a big limitation : if there is a new website, or a new html organisation, nothing will work. On the other hand my bot just looks at the screen and work with it to find the chessboard and the pieces. It is much more robust ! 

This chess bot can play automatically as white or black on lichess.com, chess.com, chess24.com and theoretically any website using drag and drop to move pieces. It uses stockfish engine to process moves, mss to do fast screenshots, pyautogui to move the mouse, chess to store and test the moves, and opencv to detect the chessboard. It has been written only with python. 

About the bot level, it beats easily chess.com computer on level 8/10 (around 2000 ELO) when taking 1.2 second per move and crushes every human opponent on any time format longer than 1 minute.

This bot has been developped on iOS, but all the librairies it is using are compatible on Linux and Windows too. 


## Getting Started

### Prerequisites

#### Stockfish:

This bot uses stockfish to calculate the next best move. Here is the procedure to make it work :

* Download stockfish for your OS (https://stockfishchess.org/download/), the macOS stockfish I used is already commited.
* Add it to your path with : ```export PATH=$PATH:$(pwd)```
* Test that stockfish is working well by running the command ```stockfish``` in your terminal. It should output something like this: ```Stockfish 120218 64 by T. Romstad, M. Costalba, J. Kiiski, G. Linscott```

#### Python:

This bot requires python 3 to run

### Using the bot:

The bot runs very easily:
* go in the folder that contains the source code
* Run the command ```python3 main.py```

### Limitations:

This project is far from perfect yet, it has a few limitations :
* Because of the computer vision algorithm used to detect the chessboard, the square colors should be with plain colors, without having wierd textures.
* The GUI is still quite basic
* One small deviation during a game (the board moved, the user touched the mouse...) and the bot will not work at all.
* It is not possible to stop the chessbot without closing the window
* This project has been tested only on a Mac

Please feel free to help me improve it

## Author

**Stanislas Heili** - *Initial work* - [myGit](https://github.com/Stanou01260/)
