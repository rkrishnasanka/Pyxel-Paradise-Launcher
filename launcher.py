import pyxel
import subprocess
import os
from enum import Enum

class AppState(Enum):
    BROWSE = 1
    LAUNCHING = 2

class Alt:
    def __init__(self):
        pyxel.init(240, 240)
        self.dirs = self._get_game_directories()
        self.cursorpos = 0
        self._appstate = AppState.BROWSE
        pyxel.run(self.update, self.draw)


    def update(self):

        if self._appstate == AppState.BROWSE:
            if pyxel.btnp(pyxel.KEY_UP):
                self.cursorpos = self.cursorpos - 1

            if pyxel.btnp(pyxel.KEY_A):
                print("a")

            if pyxel.btnp(pyxel.KEY_DOWN):
                self.cursorpos = self.cursorpos + 1

            if pyxel.btnp(pyxel.KEY_D):
                print("d")

            if pyxel.btnp(pyxel.KEY_ENTER):
                current_selection = self.dirs[self.cursorpos]
                print("Current Selection: ", current_selection)
                self._appstate = AppState.LAUNCHING
                p = subprocess.Popen(["python3", ("./games/{}/main.py").format(current_selection)])
                returncode = p.wait()
                print("Return Code: ", returncode)
                self._appstate = AppState.BROWSE
    
        elif self._appstate == AppState.LAUNCHING:
            pass


    def draw(self):
        pyxel.cls(0)
        pyxel.rect(0, 0, 240, 9, 0)
        pyxel.line(0, 9, 239, 9, 0)

        # pyxel.text(93, 2, self.help_message, 13)
        # self.help_message = ""
        if self._appstate == AppState.BROWSE:
            y = 13
            for dir in self.dirs:
                pyxel.text(16, y, dir, 13)
                y = y + 16

            
            y = (self.cursorpos+1) *16
            #rect(x1: int, y1: int, x2: int, y2: int, col: int)
            pyxel.circ(7, y , 2, 14)
            # pyxel.rect(7, y, 14,14, 14)

        elif self._appstate == AppState.LAUNCHING:
            pyxel.text(16, 50, "Launching App...", 20)


    def _get_game_directories(self):
        return [name for name in os.listdir('./games')
            if os.path.isdir(os.path.join('./games', name))]


Alt()