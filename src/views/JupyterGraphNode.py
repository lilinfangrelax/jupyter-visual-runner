from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QBrush, QPen, QColor, QPolygonF, QPainterPath
from PySide6.QtCore import Qt, QRectF


class JupyterGraphNode(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._node_width = 160
        self._node_height = 80
        self._node_radius = 10

        self._pen = QPen(QColor("#151515"))
        self._selected_pen = QPen(QColor("#aaffee00"))
        self._background_color = QBrush(QColor("#aa151515"))

        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    def boundingRect(self):
        return QRectF(-self._node_width / 2, -self._node_height / 2, self._node_width, self._node_height)
        # return self.shape().boundingRect()

    def paint(self, painter, option, widget):
        node_outline = QPainterPath()
        node_outline.addRoundedRect(-self._node_width / 2, -self._node_height / 2, self._node_width, self._node_height, self._node_radius, self._node_radius)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self._background_color)
        painter.drawPath(node_outline)

        if self.isSelected():
            painter.setPen(self._selected_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(node_outline)
        else:
            painter.setPen(self._pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(node_outline)
        pass