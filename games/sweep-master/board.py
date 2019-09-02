import pyxel
from random import randint
from enum import Enum, unique, auto


class Field:
    """
    Represents a single field on the board.
    """
    def __init__(self, corners):
        self.left_x = corners[0]
        self.left_y = corners[1]
        self.right_x = corners[2]
        self.right_y = corners[3]
        self.uncovered = False
        self.flagged = False

    def is_being_clicked(self, x, y):
        return ((self.left_x <= x <= self.right_x) and
                (self.left_y <= y <= self.right_y))

    def click(self):
        self.uncovered = True

    def toggle_flag(self):
        self.flagged = not self.flagged

    def uncover_neighbours(self):
        return False

    def is_normal(self):
        return False

    def is_flagged(self):
        return self.flagged

    def is_a_bomb(self):
        return False

    def is_uncovered(self):
        return self.uncovered

    def draw_hidden(self):
        pyxel.rect(self.left_x, self.left_y, self.right_x, self.right_y, 5)

    def draw_flagged(self):
        pyxel.blt(self.left_x, self.left_y, 1, 0, 0, 10, 10)

    def draw_uncovered(self):
        pyxel.rect(self.left_x, self.left_y, self.right_x, self.right_y, 0)

    def draw(self):
        if self.uncovered:
            self.draw_uncovered()
        elif self.flagged:
            self.draw_flagged()
        else:
            self.draw_hidden()


class NormalField(Field):
    """
    Field that does not have any neighbour that has a bomb
    and that doesn't have a bomb itself.
    """
    def __init__(self, corners):
        super(NormalField, self).__init__(corners)

    def uncover_neighbours(self):
        return self.uncovered

    def is_normal(self):
        return True


class BombField(Field):
    """
    A field with a bomb.
    """
    def __init__(self, corners):
        super(BombField, self).__init__(corners)

    def draw_uncovered(self):
        pyxel.blt(self.left_x, self.left_y, 0, 0, 0, 10, 10)

    def is_a_bomb(self):
        return True


class NeighbourField(Field):
    """
    A field without a bomb, but one that has a bomb nearby.
    """
    def __init__(self, corners, bombs_nearby):
        super(NeighbourField, self).__init__(corners)
        self.bombs_nearby = bombs_nearby
        # colours of numbers
        colours = {1: 1, 2: 3, 3: 8, 4: 11, 5: 4, 6: 12, 7: 14, 8: 6}
        self.colour = colours[bombs_nearby]
        center_x = (self.left_x + self.right_x) / 2
        center_y = (self.left_y + self.right_y) / 2
        self.text_x = center_x - pyxel.constants.FONT_WIDTH / 2
        self.text_y = center_y - pyxel.constants.FONT_HEIGHT / 2

    def draw_uncovered(self):
        pyxel.rect(self.left_x, self.left_y, self.right_x, self.right_y, 0)
        pyxel.text(self.text_x, self.text_y, str(self.bombs_nearby), self.colour)


class Board:
    """
    Game board.
    """
    def __init__(self, dimensions, bombs):
        # images of a bomb and a flag
        pyxel.image(0).load(0, 0, 'assets/bomb.png')
        pyxel.image(1).load(0, 0, 'assets/flag.png')
        # set state
        self.dimensions = dimensions
        self.number_of_fields = dimensions ** 2
        self.number_of_bombs = bombs
        self.flagged_fields = 0
        self.fields = []
        self.fields_remaining = self.number_of_fields - self.number_of_bombs
        self.bomb_exploded = False
        self.field_width = 10
        self.field_height = 10
        self.gutters_width = 3

        self.generate_board()

    @unique
    class FieldType(Enum):
        NORMAL = auto()
        BOMB = auto()

    def valid_field(self, x, y):
        return 0 <= x < self.dimensions and 0 <= y < self.dimensions

    def generate_fields(self):
        """
        Generates all fields on the board.
        """
        new_fields = []
        for i in range(self.dimensions):
            current_row = []
            for j in range(self.dimensions):
                current_row.append({'x': i, 'y': j, 'field_type': self.FieldType.NORMAL, 'bombs_nearby': 0})
            new_fields.append(current_row)
        return new_fields

    def arm_random_fields(self, fields):
        """
        Picks random fields from the list provided as an argument and arms them
        (ie. changes normal fields to a fields with a bomb).
        """
        armed_fields = 0
        while armed_fields < self.number_of_bombs:
            i = randint(0, self.dimensions - 1)
            j = randint(0, self.dimensions - 1)
            current_field = fields[i][j]
            if current_field['field_type'] == self.FieldType.NORMAL:
                current_field['field_type'] = self.FieldType.BOMB
                armed_fields += 1

    def all_neighbours(self, x, y):
        """
        Generates a list of neighbours for a particular position on the board.
        """
        neighbours = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if [i, j] != [0, 0]:
                    neighbours_x = x + i
                    neighbours_y = y + j
                    if self.valid_field(neighbours_x, neighbours_y):
                        neighbours.append({'x': neighbours_x, 'y': neighbours_y})
        return neighbours

    def inform_neighbours(self, fields):
        """
        Informs neighbours of fields with a bomb, that there is a bomb nearby.
        Used in the creation of the board.
        """
        for x in range(self.dimensions):
            for y in range(self.dimensions):
                current_field = fields[x][y]
                if current_field['field_type'] == self.FieldType.NORMAL:
                    neighbours = self.all_neighbours(x, y)
                    for neighbour in neighbours:
                        neighbours_x = neighbour['x']
                        neighbours_y = neighbour['y']
                        if fields[neighbours_x][neighbours_y]['field_type'] == self.FieldType.BOMB:
                            current_field['bombs_nearby'] += 1

    def uncover_neighbours(self, x, y):
        """
        Uncovers all fields neighbouring a given position on the board.
        """
        neighbours = self.all_neighbours(x, y)
        for neighbours_coordinates in neighbours:
            neighbours_x = neighbours_coordinates['x']
            neighbours_y = neighbours_coordinates['y']
            neighbour = self.fields[neighbours_x][neighbours_y]
            if not neighbour.is_a_bomb() and not neighbour.is_uncovered():
                self.fields_remaining -= 1
                neighbour.click()
                if neighbour.is_normal():
                    self.uncover_neighbours(neighbours_x, neighbours_y)

    def generate_board(self):
        self.fields = []
        self.fields_remaining = self.number_of_fields - self.number_of_bombs
        self.flagged_fields = 0
        self.bomb_exploded = False

        # generates all the fields and stores them in a temporary list
        all_fields = self.generate_fields()
        self.arm_random_fields(all_fields)
        self.inform_neighbours(all_fields)

        vertical_gutters = 0
        horizontal_gutters = 0

        # copies the generated fields from a temporary list to the board
        for y in range(self.dimensions):
            horizontal_gutters += self.gutters_width
            row = []
            for x in range(self.dimensions):
                vertical_gutters += self.gutters_width
                left_x = vertical_gutters + x * self.field_width
                left_y = horizontal_gutters + y * self.field_height
                right_x = vertical_gutters + (x + 1) * self.field_width
                right_y = horizontal_gutters + (y + 1) * self.field_height
                corners = [left_x, left_y, right_x, right_y]
                if all_fields[x][y]['field_type'] == self.FieldType.BOMB:
                    row.append(BombField(corners))
                else:
                    bombs_nearby = all_fields[x][y]['bombs_nearby']
                    if bombs_nearby == 0:
                        row.append(NormalField(corners))
                    else:
                        row.append(NeighbourField(corners, bombs_nearby))
            self.fields.append(row)
            vertical_gutters = 0

    def uncover_bombs(self):
        for row in self.fields:
            for field in row:
                if field.is_a_bomb():
                    field.click()

    def click(self, mouse_x, mouse_y):
        for column in range(self.dimensions):
            for row in range(self.dimensions):
                field = self.fields[column][row]
                if field.is_being_clicked(mouse_x, mouse_y) and not field.is_flagged():
                    field.click()
                    if field.is_a_bomb():
                        self.bomb_exploded = True
                        self.uncover_bombs()
                    else:
                        self.fields_remaining -= 1
                        if field.is_normal():
                            self.uncover_neighbours(column, row)
                    return

    def toggle_flag(self, mouse_x, mouse_y):
        for column in range(self.dimensions):
            for row in range(self.dimensions):
                field = self.fields[column][row]
                if not field.is_uncovered() and field.is_being_clicked(mouse_x, mouse_y):
                    # update flagged fields count
                    if field.is_flagged():
                        self.flagged_fields -= 1
                    else:
                        self.flagged_fields += 1

                    field.toggle_flag()
                    return

    def game_over(self):
        return self.bomb_exploded or self.fields_remaining == 0

    def game_won(self):
        return self.fields_remaining == 0

    def draw(self):
        for row in self.fields:
            for field in row:
                field.draw()

        text_x = self.gutters_width
        text_y = self.dimensions * (self.gutters_width + self.field_height) + self.gutters_width
        pyxel.text(text_x, text_y, "Bombs: " + str(self.number_of_bombs) + " Flags: " + str(self.flagged_fields), 14)
