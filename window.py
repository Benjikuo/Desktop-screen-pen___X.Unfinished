# type: ignore
from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor, QKeySequence
from PySide2.QtWidgets import QWidget, QApplication, QShortcut

from canva import Canva
from toolbar import Toolbar


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.canva = Canva(self)
        self.toolbar = Toolbar(self, self.canva)
        self.toolbar.raise_()

        self.showFullScreen()
        self.build_shortcuts()

    def resizeEvent(self, event):
        self.canva.setGeometry(self.rect())
        self.toolbar.adjustSize()
        tw = self.toolbar.width()
        self.toolbar.move((self.width() - tw) // 2, 10)

    def build_shortcuts(self):
        def shortcut(key, func):
            QShortcut(QKeySequence(key), self, activated=func)

        shortcut("W", lambda: self.toggle_board())
        shortcut("E", lambda: self.toggle_eraser())
        shortcut("D", lambda: self.set_lasttool())
        shortcut("T", lambda: self.set_pen(color="black"))
        shortcut("G", lambda: self.set_pen(color="white"))
        shortcut("B", lambda: self.set_pen(color="white"))
        shortcut("R", lambda: self.set_rectaingle(color="red"))
        shortcut("F", lambda: self.set_pen(color="white"))
        shortcut("V", lambda: self.set_highlight(color="yellow"))
        shortcut("S", lambda: self.toggle_shape())
        shortcut("C", lambda: self.toggle_color())
        shortcut("SHIFT+R", lambda: self.set_rectaingle())
        shortcut("SHIFT+F", lambda: self.set_pen())
        shortcut("SHIFT+V", lambda: self.set_highlight())
        shortcut("SHIFT+S", lambda: self.toggle_shape(reverse=True))
        shortcut("SHIFT+C", lambda: self.toggle_color(reverse=True))
        shortcut("X", lambda: self.canva.clear())
        shortcut("A", lambda: self.canva.undo())
        shortcut("Z", lambda: self.canva.redo())
        shortcut("Ctrl+Z", lambda: self.canva.undo())
        shortcut("Ctrl+Y", lambda: self.canva.redo())
        shortcut("Ctrl+S", lambda: self.canva.save())
        shortcut("Ctrl+R", lambda: self.closeEvent())
        shortcut("Esc", lambda: self.closeEvent())

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        change = 2

        if delta > 0:
            self.canva.thickness = min(50, self.canva.thickness + change)
        else:
            self.canva.thickness = max(2, self.canva.thickness - change)

        self.toolbar.btn_size.update()

        pos = self.mapFromGlobal(QCursor.pos())
        self.canva.show_size_popup(pos, self.canva.thickness)
        self.canva.update()

    def toggle_board(self):
        self.canva.drawing_mode = True

        if self.canva.board_color != (0, 0, 0, 50):
            self.canva.board_color = (0, 0, 0, 50)
        else:
            self.canva.board_color = (0, 0, 0, 255)

        if self.canva.tool == "eraser":
            self.canva.setCursor(Qt.BlankCursor)
        else:
            self.canva.setCursor(Qt.CrossCursor)

        self.canva.update()

    def toggle_eraser(self):
        if self.canva.tool != "eraser":
            self.canva.set_tool("eraser")
        else:
            self.canva.set_tool("crop_eraser")

    def set_lasttool(self):
        self.canva.set_tool(self.canva.last_tool)

    def set_rectaingle(self):
        self.canva.set_tool("pen")
        self.canva.set_size(4)
        self.canva.set_shape("rect")
        self.canva.set_color("red")

    def set_pen(self, color=None):
        self.canva.set_tool("pen")
        self.canva.set_size(4)
        self.canva.set_shape("free")
        if color != None:
            self.canva.set_color(color)

    def set_highlight(self):
        self.canva.set_tool("highlight")
        self.canva.set_size(6)
        self.canva.set_shape("free")
        self.canva.set_color("yellow")

    def toggle_shape(self, reverse=False):
        if self.canva.tool in ("eraser", "crop_eraser"):
            self.canva.set_tool("pen")
        if reverse:
            shape = "free"
        else:
            shape = "line"
        self.canva.set_shape(shape)

    def toggle_color(self, reverse=False):
        self.canva.set_color_tuple(color)
        self.toolbar.btn_color.update()

        colors = [
            (255, 255, 255),
            (255, 0, 0),
            (255, 136, 0),
            (255, 255, 0),
            (0, 255, 0),
            (0, 128, 255),
            (170, 85, 255),
        ]

        self.color_index = 0

        self.color_index = (self.color_index + 1) % len(colors)
        rgb = colors[self.color_index]
        self.canva.set_color_tuple(rgb)
        self.toolbar.btn_color.update()

    def closeEvent(self, event=None):
        QApplication.instance().quit()
