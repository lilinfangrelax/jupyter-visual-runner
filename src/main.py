import sys

from PySide6 import QtGui, QtWidgets, QtCore
from PySide6.QtCore import QSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QDockWidget, QMainWindow, QListWidget, QTabWidget, QTextEdit, QFrame, QWidget, \
    QVBoxLayout, QApplication
from src.views.JupyterVisualRunnerEditor import *


class JupyterVisualRunner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_node_sketchpad()
        self.showEvent = self.on_show
        self.center()

    def on_show(self, event):
        # 在窗口显示后调用 fitInView
        # self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        # self.view.scale(80,80)
        pass

    def closeEvent(self, event):
        # Save QDockWidget state
        settings = QSettings("Jupyter Visual Runner", "Jupyter Visual Runner")
        settings.setValue('windowState', self.saveState())

    def setup_node_sketchpad(self):
        self.setWindowTitle("Jupyter Visual Runner")
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QtGui.QIcon("public/icon.png"))

        self.center_tabs = QTabWidget()
        tab_container = QWidget()
        layout = QVBoxLayout(tab_container)
        layout.setContentsMargins(0, 0, 0, 0)
        self.center_tabs.addTab(tab_container, "Homepage")
        self.setCentralWidget(self.center_tabs)

        self.scene2 = NodeSketchpadScene()
        self.view2 = NodeSketchpadView(self.scene2, self)
        self.view2.setAlignment(Qt.AlignCenter)
        tab_container2 = QWidget()
        layout2 = QVBoxLayout(tab_container2)
        layout2.setContentsMargins(0, 0, 0, 0)
        layout2.addWidget(self.view2)
        self.center_tabs.addTab(tab_container2, "Scene1")
        
        self.scene3 = NodeSketchpadScene()
        self.view3 = NodeSketchpadView(self.scene3, self)
        self.view3.setAlignment(Qt.AlignCenter)
        tab_container3 = QWidget()
        layout3 = QVBoxLayout(tab_container3)
        layout3.setContentsMargins(0, 0, 0, 0)
        layout3.addWidget(self.view3)
        self.center_tabs.addTab(tab_container3, "Scene2")



        dock1 = QDockWidget("Browser", self)
        dock1_widget = QListWidget()
        dock1.setWidget(dock1_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock1)

        dock2 = QDockWidget("Properties", self)
        dock2_widget = QListWidget()
        dock2.setWidget(dock2_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock2)

        dock3 = QDockWidget("Logger", self)
        dock3_widget = QTextEdit()
        dock3_widget.setReadOnly(True)
        dock3_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # Solve problem: there is a blue line in the bottom of QTextEdit
        # https://stackoverflow.com/questions/16436058/how-to-make-qtextedit-with-no-visible-border
        dock3_widget.setFrameStyle(QFrame.NoFrame)
        dock3.setWidget(dock3_widget)
        dock3.setMinimumHeight(150)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock3)

        # Temporarily hide this widget
        # dock4 = QDockWidget("Result", self)
        web_view = QWebEngineView()
        web_view.setHtml(
            '<a href="https://data.typeracer.com/pit/profile?user=hk_l&ref=badge" target="_top"><img src="https://data.typeracer.com/misc/badge?user=hk_l" border="0" alt="TypeRacer.com scorecard for user hk_l"/></a>')
        # dock4.setWidget(web_view)
        # dock4.setEnabled(False)
        # self.addDockWidget(Qt.RightDockWidgetArea, dock4)

    def center(self):
        # Get the center point of the screen
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        center_point = screen_geometry.center()
        # Align the geometric center of the window to the center of the screen
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(center_point)

        self.move(window_geometry.topLeft())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    jupyter_visual_runner = JupyterVisualRunner()

    # Load QDockWidget state
    # the companyName and appName is necessary to save DockWidget state, I don't know why.
    settings = QSettings("Jupyter Visual Runner", "Jupyter Visual Runner")
    state = settings.value('windowState')
    if state != None:
        jupyter_visual_runner.restoreState(state)

    jupyter_visual_runner.show()
    app.exec()