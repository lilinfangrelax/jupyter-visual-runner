import math
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItem
from PySide6.QtCore import Qt, QLineF, QPointF, QRectF
from PySide6.QtGui import QPainter, QPolygonF

class ConnectionItem(QGraphicsItem):
    def __init__(self, source, destination):
        super().__init__()
        self.source = source
        self.destination = destination
        self.setZValue(10000)  # 确保线在矩形下方

        # 监听源和目标的位置变化
        self.source.addObserver(self)
        self.destination.addObserver(self)

    def addObserver(self, item):
        item.installSceneEventFilter(self)

    def sceneEventFilter(self, watched, event):
        # 当源或目标移动时更新连接线
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
        painter.setPen(Qt.black)
        painter.drawLine(line)

        # 计算箭头角度和位置
        angle = math.atan2(line.dy(), -line.dx())
        arrow_size = 10
        arrow_p1 = end_point + QPointF(
            math.sin(angle - math.pi / 3) * arrow_size,
            math.cos(angle - math.pi / 3) * arrow_size
        )
        arrow_p2 = end_point + QPointF(
            math.sin(angle - math.pi * 2 / 3) * arrow_size,
            math.cos(angle - math.pi * 2 / 3) * arrow_size
        )

        # 绘制箭头
        arrow_head = QPolygonF()
        arrow_head.append(end_point)
        arrow_head.append(arrow_p1)
        arrow_head.append(arrow_p2)
        painter.setBrush(Qt.black)
        painter.drawPolygon(arrow_head)

class ObservableRectItem(QGraphicsRectItem):
    def __init__(self, *args):
        super().__init__(*args)
        self.observers = []

    def addObserver(self, observer):
        self.observers.append(observer)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for observer in self.observers:
                observer.update()
        return super().itemChange(change, value)

# 创建场景和视图
app = QApplication()
scene = QGraphicsScene()
view = QGraphicsView(scene)
view.setRenderHint(QPainter.Antialiasing)

# 创建可观察的矩形项
rect1 = ObservableRectItem(0, 0, 50, 50)
rect1.setPos(50, 50)
rect1.setBrush(Qt.blue)
scene.addItem(rect1)

rect2 = ObservableRectItem(0, 0, 50, 50)
rect2.setPos(200, 150)
rect2.setBrush(Qt.red)
scene.addItem(rect2)

# 创建连接线并添加到场景
connection = ConnectionItem(rect1, rect2)
scene.addItem(connection)

view.show()
app.exec()