from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

HELP_TEXT = """
Objective
---------
A secret combination of 4 colors is selected, and you have to guess that combination in 8 or fewer tries to win.

How to Play
-----------
From top to bottom, at each row, click on a circle and pick a color. After filling all circles in a row, you can check your guess.

- A green circle means the color and the position are correct.
- A yellow circle means that the color exists in the combination but the position is not correct.
- An empty circle means that the color is not in the combination at all.
"""  # noqa: E501

COLORS = [QColor(Qt.red).rgba(), QColor(Qt.green).rgba(),
          QColor(Qt.blue).rgba(), QColor(Qt.magenta).rgba(),
          QColor(Qt.cyan).rgba(), QColor(Qt.darkGreen).rgba(),
          QColor(Qt.yellow).rgba(), QColor(Qt.darkRed).rgba()]
