from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtGui import QBrush, QColor, QPen, QPainter
from PySide6.QtCore import Qt, QLine, QEvent
from src.config.NodeEditorConfig import *
import PySide6
import math

from src.views.JupyterGraphNode import JupyterGraphNode


class NodeSketchpadScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setBackgroundBrush(QBrush(QColor(NodeEditorConfig.scene_background_color)))

        self._width = NodeEditorConfig.scene_width
        self._height = NodeEditorConfig.scene_height
        # Center the scene
        self.setSceneRect(
            -self._width / 2, -self._height / 2, self._width, self._height
        )

        self._grid_size = NodeEditorConfig.scene_grid_size
        self._grid_chunk = NodeEditorConfig.scene_grid_chunk

        self._normal_line_pen = QPen(
            QColor(NodeEditorConfig.scene_grid_normal_line_color)
        )
        self._normal_line_pen.setWidthF(NodeEditorConfig.scene_grid_normal_line_width)

        self._dark_line_pen = QPen(QColor(NodeEditorConfig.scene_grid_dark_line_color))
        self._dark_line_pen.setWidthF(NodeEditorConfig.scene_grid_dark_line_width)

        self.addItem(JupyterGraphNode("Start"))
        self.addItem(JupyterGraphNode("End"))

    def addItem(self, item):
        super().addItem(item)
        item.setPos(0, 0)

    def drawBackground(self, painter: PySide6.QtGui.QPainter, rect):
        super().drawBackground(painter, rect)

        lines, dark_lines = self.cal_grid_lines(rect)
        painter.setPen(self._dark_line_pen)
        painter.drawLines(dark_lines)
        painter.setPen(self._normal_line_pen)
        painter.drawLines(lines)

    def cal_grid_lines(self, rect):
        left, right, top, bottom = (
            math.floor(rect.left()),
            math.floor(rect.right()),
            math.floor(rect.top()),
            math.floor(rect.bottom()),
        )

        # Top left corner
        first_left = left - (left % self._grid_size)
        first_top = top - (top % self._grid_size)

        # Calculate the start and end points of the lines
        lines = []
        dark_lines = []
        # Draw horizontal lines
        for v in range(first_top, bottom, self._grid_size):
            line = QLine(left, v, right, v)
            if v % (self._grid_size * self._grid_chunk) == 0:
                dark_lines.append(line)
            else:
                lines.append(line)
        # Draw vertical lines
        for h in range(first_left, right, self._grid_size):
            line = QLine(h, top, h, bottom)
            if h % (self._grid_size * self._grid_chunk) == 0:
                dark_lines.append(line)
            else:
                lines.append(line)

        return lines, dark_lines


class NodeSketchpadView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self._scene = scene
        self.setScene(self._scene)

        # Make the animation more smooth
        self.setRenderHint(
            QPainter.Antialiasing
            | QPainter.TextAntialiasing
            | QPainter.SmoothPixmapTransform
        )
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # Hide the scrollbar
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Always track the mouse when adjust the ratio
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        #
        self._drag_mode = False

    def wheelEvent(self, event):
        # Zoom
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale(zoom_factor, zoom_factor)

    def mousePressEvent(self, event):
        # When no node is selected, the entire canvas can be dragged
        if event.button() == Qt.LeftButton:
            self.leftButtonPressed(event)
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.leftButtonReleased(event)
        return super().mouseReleaseEvent(event)

    def leftButtonPressed(self, event):
        if self.itemAt(event.pos()) is not None:
            return
        else:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._drag_mode = True

    def leftButtonReleased(self, event):
        self.setDragMode(QGraphicsView.NoDrag)
        self._drag_mode = False