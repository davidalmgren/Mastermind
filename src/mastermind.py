"""
Main game file
"""

import sys

from PyQt5.QtWidgets import QApplication

from .gui import Gui
from .game import Game


def main():
    app = QApplication([])

    window = Gui()
    Game(window)

    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
