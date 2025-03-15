from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem, QGraphicsLineItem
from PySide6.QtGui import QBrush, QPen, QColor, QPolygonF, QPainterPath, QFont, QTransform
from PySide6.QtCore import Qt, QRectF, QLineF

from src.views.ConnectionItem import ConnectionItem


class JupyterGraphNode(QGraphicsItem):
    def __init__(self, title,  parent=None):
        super().__init__(parent)

        self._node_width = 160
        self._node_height = 80
        self._node_radius = 10
        self.observers = []

        self._pen = QPen(QColor("#151515"))
        self._selected_pen = QPen(QColor("#aaffee00"))
        self._background_color = QBrush(QColor("#151515"))

        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

        self._title = title
        self._title_color = Qt.white
        self._title_font = QFont('Consolas', 13)
        self._title_height = 30
        self._title_padding = 3
        self._title_brush_back = QBrush(QColor("#aa00003f"))
        self.init_title()

        self.drag_mode = None  # 'move' or 'connect'
        self.temp_connection = None

    def addObserver(self, observer):
        self.observers.append(observer)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for observer in self.observers:
                observer.update()
        return super().itemChange(change, value)

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

    def mousePressEvent(self, event):
        # 通过 Ctrl 键区分模式
        if event.modifiers() == Qt.ControlModifier:
            # 连接模式：开始创建临时线
            self.drag_mode = 'connect'
            self.temp_connection = QGraphicsLineItem(
                QLineF(self.sceneBoundingRect().center(), event.scenePos()))
            self.temp_connection.setPen(QPen(Qt.white, 2, Qt.DashLine))
            self.scene().addItem(self.temp_connection)
        else:
            # 移动模式：交给父类处理
            self.drag_mode = 'move'
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_mode == 'connect':
            # 更新临时连接线
            start = self.sceneBoundingRect().center()
            self.temp_connection.setLine(QLineF(start, event.scenePos()))
        else:
            # 正常移动节点
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drag_mode == 'connect':
            # 完成连接创建
            self.scene().removeItem(self.temp_connection)
            self.temp_connection = None

            # 检测目标项
            target_item = self.scene().itemAt(event.scenePos(), QTransform())
            if (isinstance(target_item, JupyterGraphNode) and
                    target_item != self):
                connection = ConnectionItem(self, target_item)
                self.scene().addItem(connection)

        self.drag_mode = None
        super().mouseReleaseEvent(event)
