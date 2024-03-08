import random

from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from .constants import COLORS


class Game:
    def __init__(self, gui):
        self.gui = gui

        # Game state 0 is the start of the game
        self.state = 0
        self.winner_colors = None

        self._setup()

    def _setup(self):
        self.gui.retry_widget.mousePressEvent = self._reset_board
        self.gui.check_button.clicked.connect(self._check_board)
        self._reset_board(None)

    def _reset_board(self, _):
        self.gui.check_button.setEnabled(True)
        for value in self.gui.color_squares.values():
            value.select(False)

        for c in self.gui.circles[0]:
            c.selected_color = QColor(Qt.transparent)
            c.fill_color = c.selected_color
            c.update()

        for i in range(1, len(self.gui.circles)):
            for c in self.gui.circles[i]:
                c.active_hover = False
                c.selected_color = QColor(Qt.transparent)
                c.fill_color = c.selected_color
                c.update()

        for i in range(len(self.gui.hint_circles)):
            for c in self.gui.hint_circles[i]:
                c.selected_color = QColor(Qt.transparent)
                c.fill_color = c.selected_color
                c.update()

        self.state = 0
        self.winner_colors = random.sample(COLORS, 4)
        self._set_circle_callbacks()

    def _set_circle_callbacks(self):
        def get_toggle_color_func(circle):
            def func(_):
                if self.gui.get_active_color():
                    circle.selected_color = QColor(self.gui.get_active_color())
                else:
                    circle.selected_color = QColor(Qt.transparent)
                circle.update()
            return func

        def empty(_):
            pass

        for i, row in enumerate(self.gui.circles):
            for c in row:
                if i == self.state:
                    c.active_hover = True
                    c.mousePressEvent = get_toggle_color_func(c)
                else:
                    c.active_hover = False
                    c.mousePressEvent = empty
                c.update()

    def _check_board(self):
        self.gui.check_button.setEnabled(False)

        for c in self.gui.circles[self.state]:
            if c.selected_color.alpha() == 0:
                self.gui.spawn_warning("Illegal moves!",
                                       "All colors not filled in.")
                self.gui.check_button.setEnabled(True)
                return

        color_states = [Qt.transparent] * 4

        for i, c in enumerate(self.gui.circles[self.state]):
            if c.fill_color.rgba() == self.winner_colors[i]:
                color_states[i] = Qt.green
            elif c.fill_color.rgba() in self.winner_colors:
                color_states[i] = Qt.yellow

        if all(cs == Qt.green for cs in color_states):
            self.gui.spawn_information("Winner!", "Congratulations, you won.")
            self.state = -1
            self._set_circle_callbacks()
            return

        if self.state == 7 and not all(cs == Qt.green for cs in color_states):
            self.gui.spawn_information("Loser!", "You lost :(")
            self.state = -1
            self._set_circle_callbacks()
            return

        for i, cs in enumerate(color_states):
            self.gui.hint_circles[self.state][i].fill_color = QColor(cs)
            self.gui.hint_circles[self.state][i].selected_color = QColor(cs)
            self.gui.hint_circles[self.state][i].update()

        # Move to next state
        self.state += 1
        self._set_circle_callbacks()
        self.gui.check_button.setEnabled(True)
