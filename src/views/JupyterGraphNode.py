from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PySide6.QtGui import QBrush, QPen, QColor, QPolygonF, QPainterPath, QFont
from PySide6.QtCore import Qt, QRectF


class JupyterGraphNode(QGraphicsItem):
    def __init__(self, title,  parent=None):
        super().__init__(parent)

        self._node_width = 160
        self._node_height = 80
        self._node_radius = 10

        self._pen = QPen(QColor("#151515"))
        self._selected_pen = QPen(QColor("#aaffee00"))
        self._background_color = QBrush(QColor("#aa151515"))

        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

        self._title = title
        self._title_color = Qt.white
        self._title_font = QFont('Consolas', 13)
        self._title_height = 30
        self._title_padding = 3
        self._title_brush_back = QBrush(QColor("#aa00003f"))
        self.init_title()

    def boundingRect(self):
        return QRectF(-self._node_width / 2, -self._node_height / 2, self._node_width, self._node_height)
        # return self.shape().boundingRect()

    def paint(self, painter, option, widget):
        node_outline = QPainterPath()
        node_outline.addRoundedRect(-self._node_width / 2, -self._node_height / 2, self._node_width, self._node_height, self._node_radius, self._node_radius)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self._background_color)
        painter.drawPath(node_outline)

        # Draw title
        title_outline = QPainterPath()
        title_outline.setFillRule(Qt.WindingFill)
        title_outline.addRoundedRect(-self._node_width / 2, -self._node_height / 2, self._node_width, self._title_height, self._node_radius, self._node_radius)
        title_outline.addRect(-self._node_width / 2 + self._node_width-self._node_radius , -self._node_height / 2 + self._title_height - self._node_radius, self._node_radius, self._node_radius)
        title_outline.addRect(-self._node_width / 2 , -self._node_height / 2 + self._title_height - self._node_radius, self._node_radius, self._node_radius)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._title_brush_back)

        painter.drawPath(title_outline)


        if self.isSelected():
            painter.setPen(self._selected_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(node_outline)
        else:
            painter.setPen(self._pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(node_outline)
        pass

    def init_title(self):
        self._titleitem = QGraphicsTextItem(self)
        self._titleitem.setPlainText(self._title)
        self._titleitem.setFont(self._title_font)
        self._titleitem.setDefaultTextColor(self._title_color)
        self._titleitem.setPos(-self._node_width / 2 + self._title_padding, -self._node_height / 2 + self._title_padding)
        # self._titleitem.setPos(self._title_padding, self._title_padding)

