from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from piece import Piece

class Board(QFrame):  # base the board on a QFrame widget
    updateTimerSignal = pyqtSignal(int) # signal sent when timer is updated
    clickLocationSignal = pyqtSignal(str) # signal sent when there is a new click location

    # TODO set the board width and height to be square
    boardWidth  = 7     # board is 0 squares wide # TODO this needs updating
    boardHeight = 7     #
    timerSpeed  = 1     # the timer updates ever 1 second
    counter     = 10    # the number the counter will count down from
    flipBlackWhite = 0  # black first, then white turn

    def __init__(self, parent):
        super().__init__(parent)
        self.initBoard()

    def initBoard(self):
        '''initiates board'''
        self.timer = QBasicTimer()  # create a timer for the game
        self.isStarted = False      # game is not currently started
        self.start()                # start the game which will start the timer

        self.boardArray =[[0 for col in range(self.boardWidth)] for row in range(self.boardHeight)] # TODO - create a 2d int/Piece array to store the state of the game
        self.printBoardArray()    # TODO - uncomment this method after create the array above

    def printBoardArray(self):
        '''prints the boardArray in an attractive way'''
        print("boardArray:")
        print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in self.boardArray]))

    def isCaptured(self, row, col):
        try:
            opponent = -self.boardArray[row][col]
            if self.boardArray[row-1][col] == self.boardArray[row+1][col] == \
               self.boardArray[row][col-1] == self.boardArray[row][col+1] == \
               opponent:
                self.boardArray[row][col] = 0
        except Exception as e:
            print(e)
    def isMultiCaptured(self, row, col, prevDir):
        try:
            if not self.boardArray[row-1][col] or not self.boardArray[row+1][col] or \
               not self.boardArray[row][col-1] or not self.boardArray[row][col+1]:
               return False # there's a way out, I can survive

            ally     = +self.boardArray[row][col]
            opponent = -self.boardArray[row][col]
            if self.boardArray[row-1][col] == ally and prevDir != "down":
                if self.isMultiCaptured(row-1,col,"up"): # this litl ally is potentially be captured
                    self.boardArray[row][col] = 0
            if self.boardArray[row+1][col] == ally and prevDir != "up":
                if self.isMultiCaptured(row+1,col,"down"):
                    self.boardArray[row][col] = 0
            if self.boardArray[row][col-1] == ally and prevDir != "left":
                if self.isMultiCaptured(row,col-1,"right"):
                    self.boardArray[row][col] = 0
            if self.boardArray[row][col+1] == ally and prevDir != "right":
                if self.isMultiCaptured(row,col+1,"left"):
                    self.boardArray[row][col] = 0
            # check is surronded
            if prevDir == "up" and self.boardArray[row-1][col] == \
               self.boardArray[row][col-1] == self.boardArray[row][col+1] == \
               opponent:
                self.boardArray[row][col] = 0
                return True # pertentally captured
            if prevDir == "down" and self.boardArray[row+1][col] == \
               self.boardArray[row][col-1] == self.boardArray[row][col+1] == \
               opponent:
                self.boardArray[row][col] = 0
                return True
            if prevDir == "left" and self.boardArray[row-1][col] == \
               self.boardArray[row+1][col] == self.boardArray[row][col+1] == \
               opponent:
                self.boardArray[row][col] = 0
                return True
            if prevDir == "right" and self.boardArray[row-1][col] == \
               self.boardArray[row+1][col] == self.boardArray[row][col-1] == \
               opponent:
                self.boardArray[row][col] = 0
                return True
            return False
        except Exception as e:
            print(e)
    def checkHostage(self, row, col):
        try:
            opponent = -self.boardArray[row][col]
            if self.boardArray[row-1][col] == opponent:
                self.isMultiCaptured(row-1,col,"") #self.isCaptured(row-1, col)
            if self.boardArray[row+1][col] == opponent:
                self.isMultiCaptured(row+1,col,"") #self.isCaptured(row+1, col)
            if self.boardArray[row][col-1] == opponent:
                self.isMultiCaptured(row,col-1,"") #self.isCaptured(row, col-1)
            if self.boardArray[row][col+1] == opponent:
                self.isMultiCaptured(row,col+1,"") #self.isCaptured(row, col+1)
        except Exception as e:
            print(e)

    def mousePosToColRow(self, event):
        '''convert the mouse click event to a row and column'''
        try:
            col = int(round((event.x()) / self.squareWidth()))
            row = int(round((event.y()) / self.squareHeight()))
            if self.flipBlackWhite: self.boardArray[row][col] = 1
            else:                   self.boardArray[row][col] = -1

            self.checkHostage(row, col)

            self.printBoardArray()
            self.drawPieces(QPainter(self))
            self.update()
        except Exception as e:
            print(e)

    def squareWidth(self):
        '''returns the width of one square in the board'''
        return self.contentsRect().width() / self.boardWidth

    def squareHeight(self):
        '''returns the height of one square of the board'''
        return self.contentsRect().height() / self.boardHeight

    def start(self):
        '''starts game'''
        self.isStarted = True                       # set the boolean which determines if the game has started to TRUE
        self.resetGame()                            # reset the game
        self.timer.start(self.timerSpeed, self)     # start the timer with the correct speed
        print("start () - timer is started")

    def timerEvent(self, event):
        '''this event is automatically called when the timer is updated. based on the timerSpeed variable '''
        # TODO adapter this code to handle your timers
        if event.timerId() == self.timer.timerId():  # if the timer that has 'ticked' is the one in this class
            if Board.counter == 0:
                print("Game over")
            self.counter -= 1
            #print('timerEvent()', self.counter)
            self.updateTimerSignal.emit(self.counter)
        else:
            super(Board, self).timerEvent(event)      # if we do not handle an event we should pass it to the super
                                                        # class for handelingother wise pass it to the super class for handling

    def paintEvent(self, event):
        '''paints the board and the pieces of the game'''
        painter = QPainter(self)
        self.drawBoardSquares(painter)
        self.drawPieces(painter)

    def mousePressEvent(self, event):
        '''this event is automatically called when the mouse is pressed'''
        clickLoc = "click location ["+str(event.x())+","+str(event.y())+"]"     # the location where a mouse click was registered
        print("mousePressEvent() - "+clickLoc)
        # TODO you could call some game logic here
        self.flipBlackWhite = not self.flipBlackWhite
        self.mousePosToColRow(event)
        self.clickLocationSignal.emit(clickLoc)

    def resetGame(self):
        '''clears pieces from the board'''
        # TODO write code to reset game

    def tryMove(self, newX, newY):
        '''tries to move a piece'''

    def drawBoardSquares(self, painter):
        '''draw all the square on the board'''
        try:
            # TODO set the default colour of the brush
            for row in range(0, Board.boardHeight):
                for col in range (0, Board.boardWidth):
                    painter.save()
                    colTransformation = self.squareWidth()* col # TODO set this value equal the transformation in the column direction
                    rowTransformation = self.squareHeight()* row # TODO set this value equal the transformation in the row direction
                    painter.translate(colTransformation,rowTransformation)
                    painter.fillRect(0,0, self.squareWidth(), self.squareHeight(), QColor(255,255,255))                          # TODO provide the required arguments
                    painter.setPen(QPen(Qt.black, 5, Qt.SolidLine))
                    painter.drawRect(0,0, self.squareWidth(), self.squareHeight())
                    painter.restore()
                    # TODO change the colour of the brush so that a checkered board is drawn
        except Exception as e:
            print(e)

    def drawPieces(self, painter):
        '''draw the prices on the board'''
        try:
            colour = Qt.transparent # empty square could be modeled with transparent pieces
            for row in range(0, len(self.boardArray)):
                for col in range(0, len(self.boardArray[0])):
                    painter.save()
                    if (self.boardArray[row][col] == 1):
                        colTransformation = self.squareWidth()*col - self.squareWidth()/2
                        rowTransformation = self.squareHeight()*row - self.squareHeight()/2
                        painter.translate(colTransformation, rowTransformation)
                        # TODO draw some the pieces as ellipses
                        # TODO choose your colour and set the painter brush to the correct colour
                        painter.setPen(QPen(Qt.cyan, 5 , Qt.SolidLine))
                        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))

                        radius = (self.squareWidth() - 8) / 2
                        center = QPoint(radius, radius)
                        painter.drawEllipse(center, radius, radius)
                        painter.restore()
                    elif (self.boardArray[row][col] == -1):
                        colTransformation = self.squareWidth()*col - self.squareWidth()/2
                        rowTransformation = self.squareHeight()*row - self.squareHeight()/2
                        painter.translate(colTransformation, rowTransformation)
                        # TODO draw some the pieces as ellipses
                        # TODO choose your colour and set the painter brush to the correct colour
                        painter.setPen(QPen(Qt.red, 5, Qt.SolidLine))
                        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))

                        radius = (self.squareWidth() - 8) / 2
                        center = QPoint(radius, radius)
                        painter.drawEllipse(center, radius, radius)
                        painter.restore()
        except Exception as e:
            print(e)
