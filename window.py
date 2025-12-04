# type: ignore
from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor, QKeySequence
from PySide2.QtWidgets import QWidget, QApplication, QShortcut
from mss import mss
from mss.tools import to_png
import os

from canva import Canva
from toolbar import Toolbar


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.tool_index = 0
        self.shape_index = 0
        self.color_index = 0

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
        shortcut("Q", lambda: self.toggle_tool())
        shortcut("S", lambda: self.toggle_shape())
        shortcut("C", lambda: self.toggle_color())
        shortcut("R", lambda: self.set_rectaingle(color="red"))
        shortcut("F", lambda: self.set_pen(color="white"))
        shortcut("V", lambda: self.set_highlight(color="yellow"))
        shortcut("SHIFT+Q", lambda: self.toggle_tool(reverse=True))
        shortcut("SHIFT+S", lambda: self.toggle_shape(reverse=True))
        shortcut("SHIFT+C", lambda: self.toggle_color(reverse=True))
        shortcut("SHIFT+R", lambda: self.set_rectaingle())
        shortcut("SHIFT+F", lambda: self.set_pen())
        shortcut("SHIFT+V", lambda: self.set_highlight())
        shortcut("T", lambda: self.set_pen(color="gray"))
        shortcut("G", lambda: self.set_pen(color="white"))
        shortcut("B", lambda: self.set_pen(color="white"))
        shortcut("X", lambda: self.canva.clear())
        shortcut("A", lambda: self.canva.undo())
        shortcut("Z", lambda: self.canva.redo())
        shortcut("Ctrl+Z", lambda: self.canva.undo())
        shortcut("Ctrl+Y", lambda: self.canva.redo())
        shortcut("Ctrl+S", lambda: self.save())
        shortcut("Ctrl+R", lambda: self.closeEvent())
        shortcut("Esc", lambda: self.closeEvent())

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        change = 2

        if delta > 0:
            self.canva.thickness = min(50, self.canva.thickness + change)
        else:
            self.canva.thickness = max(2, self.canva.thickness - change)

        pos = self.mapFromGlobal(QCursor.pos())
        self.canva.show_size_popup(pos, self.canva.thickness)
        self.toolbar.btn_size.update()
        self.canva.update()

    # W
    def toggle_board(self):
        self.canva.drawing_mode = True

        if self.canva.board_color != (0, 0, 0, 50):
            self.canva.board_color = (0, 0, 0, 50)
        else:
            self.canva.board_color = (0, 0, 0, 255)
        self.canva.update()

    # E
    def toggle_eraser(self):
        if self.canva.tool != "eraser":
            self.canva.set_tool("eraser")
        else:
            self.canva.set_tool("crop_eraser")

    # D
    def set_lasttool(self):
        self.canva.set_tool(self.canva.last_tool)

    # Q
    def toggle_tool(self, reverse=False):
        tools = [
            "pen",
            "highlight",
            "eraser",
            "crop_eraser",
        ]

        self.tool_index = tools.index(self.canva.tool)
        if reverse:
            self.tool_index = (self.tool_index - 1) % len(tools)
        else:
            self.tool_index = (self.tool_index + 1) % len(tools)

        t = tools[self.tool_index]
        self.canva.set_tool(t)

    # S
    def toggle_shape(self, reverse=False):
        shapes = [
            "free",
            "line",
            "rect",
        ]

        self.shape_index = shapes.index(self.canva.shape)
        if reverse:
            self.shape_index = (self.shape_index - 1) % len(shapes)
        else:
            self.shape_index = (self.shape_index + 1) % len(shapes)

        s = shapes[self.shape_index]
        self.canva.set_shape(s)
        self.toolbar.btn_shape.update()

    # C
    def toggle_color(self, reverse=False):
        colors = [
            "white",
            "red",
            "orange",
            "yellow",
            "green",
            "blue",
            "purple",
        ]

        self.color_index = colors.index(self.canva.color)
        if reverse:
            self.color_index = (self.color_index - 1) % len(colors)
        else:
            self.color_index = (self.color_index + 1) % len(colors)

        c = colors[self.color_index]
        self.canva.set_color(c)
        self.toolbar.btn_color.update()

    # R
    def set_rectaingle(self):
        self.canva.set_tool("pen")
        self.canva.set_size(4)
        self.canva.set_shape("rect")
        self.canva.set_color("red")

    # F
    def set_pen(self, color=None):
        self.canva.set_tool("pen")
        self.canva.set_size(4)
        self.canva.set_shape("free")
        if color != None:
            self.canva.set_color(color)

    # V
    def set_highlight(self):
        self.canva.set_tool("highlight")
        self.canva.set_size(6)
        self.canva.set_shape("free")
        self.canva.set_color("yellow")

    # CTRL+S
    def save(self, back=None):
        old = self.canva.board_color

        if back == "black":
            self.canva.board_color = (0, 0, 0, 255)
        elif back == "trans":
            self.canva.board_color = (0, 0, 0, 0)
        elif self.canva.board_color == (0, 0, 0, 50):
            self.canva.board_color = (0, 0, 0, 0)

        self.toolbar.hide()
        self.canva.update()
        QApplication.processEvents()

        download = os.path.join(os.path.expanduser("~"), "Downloads")
        default_path = os.path.join(download, "canva_screenshot.png")
        with mss() as sct:
            screenshot = sct.grab(sct.monitors[1])
            to_png(screenshot.rgb, screenshot.size, output=default_path)
        os.startfile(download)

        self.canva.board_color = old
        self.toolbar.show()
        self.canva.update()

    # CTRL+R
    def closeEvent(self, event=None):
        QApplication.instance().quit()
