from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QFrame, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import QByteArray, Qt

from .svg import SVG_RETRY, SVG_SUN, SVG_MOON, SVG_HELP
from .constants import HELP_TEXT, COLORS


class SquareWidget(QWidget):
    def __init__(self, color, width, parent=None):
        super().__init__(parent)
        self.width = width
        self.square_color = QColor(color)
        self.border_color = QColor(Qt.transparent)
        self.selected = False
        self.pen_width = 3

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen()
        pen.setColor(self.border_color)
        pen.setWidth(self.pen_width)
        painter.setPen(pen)

        painter.setBrush(self.square_color)
        painter.drawRect(0, 0, self.width, self.width)

    def select(self, v):
        if v:
            self.selected = True
            self.border_color = QColor(Qt.black)
            self.pen_width = 10
        else:
            self.selected = False
            self.border_color = QColor(Qt.transparent)
            self.pen_width = 3
        self.update()

    def enterEvent(self, event):
        if not self.selected:
            self.border_color = QColor(Qt.black)
            self.update()

    def leaveEvent(self, event):
        if not self.selected:
            self.border_color = QColor(Qt.transparent)
            self.update()


class CircleWidget(QWidget):
    def __init__(self, diameter, parent=None):
        super().__init__(parent)
        self.diameter = diameter
        self.circle_color = QColor(Qt.black)
        self.active_hover = False
        self.selected_color = QColor(Qt.transparent)
        self.fill_color = self.selected_color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen()
        pen.setColor(self.circle_color)
        pen.setWidth(1)
        painter.setPen(pen)

        if self.fill_color:
            painter.setBrush(self.fill_color)
        painter.drawEllipse(1, 1, self.diameter - 2, self.diameter - 2)

    def enterEvent(self, event):
        if self.active_hover:
            self.fill_color = QColor(Qt.lightGray)
            self.update()

    def leaveEvent(self, event):
        if self.active_hover:
            self.fill_color = self.selected_color
            self.update()


class HoverLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("border: 1px solid rgba(0, 0, 0, 0);")

    def enterEvent(self, event):
        self.setStyleSheet("border: 1px solid black;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet("border: 1px solid rgba(0, 0, 0, 0);")
        super().leaveEvent(event)


class Gui(QMainWindow):
    def __init__(self):
        super().__init__()

        self._day = True
        self._light_widget = None

        self.retry_widget = None

        self.circles = None
        self.hint_circles = None
        self.color_squares = None
        self.check_button = None

        self._init_ui()

    def _init_ui(self):
        # Set background color
        self.setStyleSheet("background-color: white;")

        # Set the window size
        width = 320
        height = 500
        self.setFixedSize(width, height)

        # Make the window float if you are using a tiling wm
        self.setWindowFlags(self.windowFlags() | 0x4000000)

        # Set title
        self.setWindowTitle('Mastermind')

        # Set up top bar
        nav_bar = QFrame(self)
        nav_bar_layout = QHBoxLayout()
        nav_bar.setLayout(nav_bar_layout)
        nav_bar.setGeometry(0, 0, width, 50)

        label = QLabel('Mastermind', self)
        label.setFont(QFont('Impact', 16))

        # Create option labels
        self.retry_widget = HoverLabel()
        self._set_svg_on_label(self.retry_widget, SVG_RETRY)

        self._light_widget = HoverLabel()
        self._set_svg_on_label(self._light_widget, SVG_SUN)
        self._light_widget.mousePressEvent = self._set_night_or_day

        help_widget = HoverLabel()
        self._set_svg_on_label(help_widget, SVG_HELP)
        help_widget.mousePressEvent = self._spawn_help

        nav_bar_layout.addWidget(label)
        nav_bar_layout.addStretch()
        nav_bar_layout.addWidget(self.retry_widget)
        nav_bar_layout.addWidget(self._light_widget)
        nav_bar_layout.addWidget(help_widget)

        # Create divider line
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setGeometry(5, 45, width - 10, 5)

        game_frame = QFrame(self)
        game_frame.setGeometry(0, 50, width, height - 30)

        # Set up guess circles
        self.circles = []
        for row in range(8):
            self.circles.append([])
            for col in range(4):
                circle = CircleWidget(45, game_frame)
                circle.setFixedSize(46, 46)
                x = col * 50 + 10
                y = row * 50 + 10
                circle.move(x, y)
                self.circles[row].append(circle)

        # Set up the hinting circles
        self.hint_circles = []
        for row in range(7):
            self.hint_circles.append([])
            for col in range(4):
                circle = CircleWidget(20, game_frame)
                circle.setFixedSize(21, 21)
                x = col * 22 + 220
                y = row * 50 + 80
                circle.move(x, y)
                self.hint_circles[row].append(circle)

        # Set up the color squares to pick color
        self.color_squares = {}
        for col, color in enumerate(COLORS):
            square = SquareWidget(color, 30, game_frame)
            square.setFixedSize(31, 31)
            x = col * 39 + 10
            y = 415
            square.move(x, y)

            # Use closure to set color in this class instance
            def get_set_color_func(clr, clr_squares):
                def func(_):
                    for key, value in clr_squares.items():
                        value.select(key == clr)
                return func

            square.mousePressEvent = get_set_color_func(color, self.color_squares)
            self.color_squares[color] = square

        self.check_button = QPushButton("Check", game_frame)
        self.check_button.setGeometry(225, 15, 80, 50)

    def _set_svg_on_label(self, widget, svg_data):
        svg_bytes = QByteArray(svg_data.encode())
        pixmap = QPixmap()
        pixmap.loadFromData(svg_bytes)
        widget.setPixmap(pixmap)

    def _set_night_or_day(self, _):
        if self._day:
            self._set_svg_on_label(self._light_widget, SVG_MOON)
            self.setStyleSheet("background-color: gray;")
        else:
            self._set_svg_on_label(self._light_widget, SVG_SUN)
            self.setStyleSheet("background-color: white;")

        self._day = not self._day

    def spawn_warning(self, title, text):
        QMessageBox.warning(self, title, text)

    def spawn_information(self, title, text):
        QMessageBox.information(self, title, text)

    def _spawn_help(self, _):
        self.spawn_information("Game Rules", HELP_TEXT)

    def get_active_color(self):
        for key, value in self.color_squares.items():
            if value.selected:
                return key

        return Qt.transparent
