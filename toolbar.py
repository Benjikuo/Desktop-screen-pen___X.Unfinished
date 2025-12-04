# type: ignore
from PySide2.QtCore import Qt, QSize, QPoint
from PySide2.QtGui import QColor, QPainter, QPen, QIcon
from PySide2.QtWidgets import QPushButton, QFrame, QHBoxLayout, QMenu
import os

from canva import Canva


def get_icon(path: str):
    base = os.path.dirname(os.path.abspath(__file__))
    full = os.path.join(base, "image", "toolbar", path)
    return QIcon(full)


class SizeButton(QPushButton):
    def __init__(self, canvas: Canva, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = canvas
        self.setFixedSize(52, 52)

    def paintEvent(self, event):
        super().paintEvent(event)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(255, 255, 255), 3))
        p.setBrush(Qt.NoBrush)

        cx = self.width() // 2
        cy = self.height() // 2
        r = min(18, self.canvas.thickness / 2)
        p.drawEllipse(QPoint(cx, cy), r, r)


class ShapeButton(QPushButton):
    def __init__(self, canvas: Canva, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = canvas
        self.setFixedSize(52, 52)

    def paintEvent(self, event):
        super().paintEvent(event)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(255, 255, 255), 3))

        cx = self.width() // 2
        cy = self.height() // 2

        shape = self.canvas.shape
        if shape == "free":
            font = p.font()
            font.setFamily("Microsoft JhengHei")
            font.setPointSize(24)

            p.setFont(font)
            p.drawText(self.rect(), Qt.AlignCenter, "S")

        elif shape == "line":
            p.drawLine(cx - 12, cy - 12, cx + 12, cy + 12)

        elif shape == "rect":
            p.drawRect(cx - 12, cy - 12, 24, 24)


class ColorButton(QPushButton):
    def __init__(self, canvas: Canva, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = canvas
        self.setFixedSize(52, 52)

    def paintEvent(self, event):
        super().paintEvent(event)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(255, 255, 255), 3))

        r = self.canvas.pen_color.red()
        g = self.canvas.pen_color.green()
        b = self.canvas.pen_color.blue()
        p.setBrush(QColor(r, g, b))

        x = (self.width()) // 2
        y = (self.height()) // 2
        p.drawRoundedRect(x - 13, y - 13, 26, 26, 8, 8)


class Toolbar(QFrame):
    def __init__(self, window, canva):
        super().__init__(window)
        self.canva = canva

        self.setFixedHeight(72)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #333333;
                border-radius: 12px;
            }
        
            QPushButton {
                background-color: #555555;
                border-radius: 8px;
            }
        
            QPushButton:hover {
                background-color: #777777;
            }

            QPushButton:pressed {
                background-color: #906000;
            }
        
            QMenu {
                background-color: #333333;
                color: #FFFFFF;
                border: 1px solid #666666;
                font-size: 15px;
            }

            QMenu::item {
                padding: 4px 6px;
            }
        
            QMenu::item:selected {
                background-color: #555555;
            }
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        def icon_btn(path, scale=0.8):
            btn = QPushButton()
            btn.setFixedSize(52, 52)
            btn.setIcon(get_icon(path))
            btn.setIconSize(QSize(int(52 * scale), int(52 * scale)))
            layout.addWidget(btn)
            return btn

        # board
        btn_board = icon_btn("board.svg")
        btn_board.clicked.connect(window.toggle_board)

        # tool
        btn_tool = icon_btn(f"tools/{self.canva.tool}.svg")
        tool_menu = QMenu(self)
        tool_menu.addAction("🖊️ pen", lambda: self.canva.set_tool("free"))
        tool_menu.addAction("🖍️ highlight", lambda: self.canva.set_tool("highlight"))
        tool_menu.addAction(" █  eraser", lambda: self.canva.set_tool("eraser"))
        tool_menu.addAction(
            "［ ］ crop eraser", lambda: self.canva.set_tool("crop_eraser")
        )
        btn_tool.setMenu(tool_menu)

        # size
        self.btn_size = SizeButton(canva)
        layout.addWidget(self.btn_size)
        size_menu = QMenu(self)
        for s in [4, 6, 10, 14, 20, 30, 50]:
            size_menu.addAction(
                f"{s}px",
                lambda v=s: (self.canva.set_size(v), self.btn_size.update()),
            )
        self.btn_size.setMenu(size_menu)

        # shape
        self.btn_shape = ShapeButton(canva)
        layout.addWidget(self.btn_shape)
        shape_menu = QMenu(self)
        shape_menu.addAction(" S  free pen", lambda: self.canva.set_shape("free"))
        shape_menu.addAction(" ╲  line", lambda: self.canva.set_shape("line"))
        shape_menu.addAction("☐  ractangle", lambda: self.canva.set_shape("rect"))
        self.btn_shape.setMenu(shape_menu)

        # color
        self.btn_color = ColorButton(canva)
        layout.addWidget(self.btn_color)
        color_menu = QMenu(self)
        colors = {
            "⬜ white": "white",
            "🟥 red": "red",
            "🟧 orange": "orange",
            "🟨 yellow": "yellow",
            "🟩 green": "green",
            "🟦 blue": "blue",
            "🟪 purple": "purple",
        }
        for name, color in colors.items():
            color_menu.addAction(
                name,
                lambda c=color: (self.canva.set_color(c), self.btn_color.update()),
            )
        self.btn_color.setMenu(color_menu)

        # save
        btn_save = icon_btn("save.svg")
        save_menu = QMenu(self)
        save_menu.addAction("⬛ Black background", lambda: window.save("black"))
        save_menu.addAction(
            " ....  Transparent background", lambda: window.save("trans")
        )
        btn_save.setMenu(save_menu)

        # undo
        btn_undo = icon_btn("undo.svg")
        btn_undo.clicked.connect(canva.undo)

        # redo
        btn_redo = icon_btn("redo.svg")
        btn_redo.clicked.connect(canva.redo)

        # clear
        btn_clear = icon_btn("clear.svg")
        btn_clear.clicked.connect(canva.clear)

        # close
        btn_close = icon_btn("close.svg")
        btn_close.clicked.connect(window.closeEvent)
