"""
A version of minesweeper written with the pyxel python library.

Author: andrzej229
"""

import pyxel
from board import Board
from enum import Enum, unique, auto


@unique
class GameState(Enum):
    START = auto()
    GAME = auto()
    END_WON = auto()
    END_LOST = auto()


class App:
    @staticmethod
    def message_box_dimensions(width, height):
        box_left_x = width / 2 - 51
        box_left_y = height / 2 - 54
        box_right_x = width / 2 + 50
        box_right_y = width / 2 + 50
        return {
            'box_left_x': box_left_x,
            'box_left_y': box_left_y,
            'box_right_x': box_right_x,
            'box_right_y': box_right_y,
            'box_centre_x': (box_left_x + box_right_x) / 2,
            'box_centre_y': (box_left_y + box_right_y) / 2
        }

    def __init__(self):
        # board dimensions
        self.width = 134
        self.height = 140
        # generate window
        pyxel.init(self.width, self.height, caption='Sweep')
        # set state
        self.state = GameState.START
        self.sound_played = False
        self.board_columns = 10
        self.board_bombs = 10
        # generate board
        self.board = Board(self.board_columns, self.board_bombs)

        # set sounds
        pyxel.sound(0).set('g0e0c0', 't', '7', 'f', 25)
        pyxel.sound(1).set('c0e0g0c1', 't', '7', 'f', 25)

        # message box dimensions
        self.message_box = App.message_box_dimensions(self.width, self.height)

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if pyxel.btnp(pyxel.KEY_N):
            self.board.generate_board()
            self.sound_played = False
            self.state = GameState.GAME

        if self.state == GameState.GAME:
            if pyxel.btnp(pyxel.KEY_LEFT_BUTTON):
                self.board.click(pyxel.mouse_x, pyxel.mouse_y)

            if pyxel.btnp(pyxel.KEY_RIGHT_BUTTON):
                self.board.toggle_flag(pyxel.mouse_x, pyxel.mouse_y)

        if self.board.game_over():
            if self.board.game_won():
                self.state = GameState.END_WON
                if not self.sound_played:
                    pyxel.play(0, 1)
            else:
                self.state = GameState.END_LOST
                if not self.sound_played:
                    pyxel.play(0, 0)

            self.sound_played = True

    def draw(self):
        pyxel.cls(0)

        self.board.draw()

        if self.state == GameState.START:
            self.print_message("Sweep", "Press \"n\"", "to start the game")

        if self.state == GameState.END_WON:
            self.print_message("You won", "Press \"n\"", "to play again")

        if self.state == GameState.END_LOST:
            self.print_message("You lost", "Press \"n\"", "to play again", False)

    def print_box(self):
        box_left_x = self.message_box['box_left_x']
        box_left_y = self.message_box['box_left_y']
        box_right_x = self.message_box['box_right_x']
        box_right_y = self.message_box['box_right_y']
        pyxel.rect(box_left_x, box_left_y, box_right_x, box_right_y, 3)

    def print_message(self, first_message, second_message, third_message, print_box=True):
        if print_box:
            self.print_box()

        box_centre_x = self.message_box['box_centre_x']
        box_centre_y = self.message_box['box_centre_y']
        name_x = box_centre_x - pyxel.constants.FONT_WIDTH * len(first_message) / 2
        name_y = box_centre_y - pyxel.constants.FONT_HEIGHT * 4
        pyxel.text(name_x, name_y, first_message, 14)

        play_x = box_centre_x - pyxel.constants.FONT_WIDTH * len(second_message) / 2
        play_y = name_y + pyxel.constants.FONT_HEIGHT * 3
        pyxel.text(play_x, play_y, second_message, 14)

        press_x = box_centre_x - pyxel.constants.FONT_WIDTH * len(third_message) / 2
        press_y = play_y + pyxel.constants.FONT_HEIGHT * 1.5
        pyxel.text(press_x, press_y, third_message, 14)


App()
