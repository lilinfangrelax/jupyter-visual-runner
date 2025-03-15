import math

from PySide6.QtCore import QRectF, QLineF, QPointF, Qt
from PySide6.QtGui import QPolygonF, QColor
from PySide6.QtWidgets import QGraphicsItem


class ConnectionItem(QGraphicsItem):
    def __init__(self, source, destination):
        super().__init__()
        self.source = source
        self.destination = destination
        self.setZValue(-1)

        # Listen for changes in the position of the source and target
        self.source.addObserver(self)
        self.destination.addObserver(self)

    def addObserver(self, item):
        item.installSceneEventFilter(self)

    def sceneEventFilter(self, watched, event):
        # Update connection lines when source or target moves
        if watched in (self.source, self.destination) and event.type() == event.GraphicsItemMove:
            self.update()
        return super().sceneEventFilter(watched, event)

    def boundingRect(self):
        # 计算包围盒，包含线和箭头
        start = self.source.sceneBoundingRect().center()
        end = self.destination.sceneBoundingRect().center()
        return QRectF(start, end).normalized().adjusted(-10, -10, 10, 10)

    def paint(self, painter, option, widget):
        # 获取场景中的实际坐标
        start_point = self.source.sceneBoundingRect().center()
        end_point = self.destination.sceneBoundingRect().center()

        # 绘制连接线
        line = QLineF(start_point, end_point)
        painter.setPen(QColor("#aaababab"))
        painter.drawLine(line)

        center_point = line.center()

        # 计算箭头角度和位置
        angle = math.atan2(-line.dy(), line.dx())
        arrow_size = 20
        arrow_p1 = center_point + QPointF(
            math.sin(angle - math.pi / 3) * arrow_size,
            math.cos(angle - math.pi / 3) * arrow_size
        )
        arrow_p2 = center_point + QPointF(
            math.sin(angle - math.pi * 2 / 3) * arrow_size,
            math.cos(angle - math.pi * 2 / 3) * arrow_size
        )





        # 绘制箭头
        arrow_head = QPolygonF()
        arrow_head.append(center_point)
        arrow_head.append(arrow_p1)
        arrow_head.append(arrow_p2)
        painter.setBrush(QColor("#aaababab"))
        painter.drawPolygon(arrow_head)