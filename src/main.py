import sys

from PySide6 import QtGui, QtWidgets, QtCore
from PySide6.QtCore import QSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QDockWidget, QMainWindow, QListWidget, QTabWidget, QTextEdit, QFrame, QWidget, \
    QVBoxLayout, QApplication

from src.models.JupyterNodeModel import JupyterNodeModel
from src.utils.ipynb_file_util import load_notebook, save_notebook
from src.views.JupyterVisualRunnerEditor import *


class JupyterVisualRunner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_node_sketchpad()
        self.center()

    def closeEvent(self, event):
        # Save QDockWidget state
        settings = QSettings("Jupyter Visual Runner", "Jupyter Visual Runner")
        settings.setValue('windowState', self.saveState())

    def add_tab(self):
        self.scene2 = NodeSketchpadScene()
        self.view2 = NodeSketchpadView(self.scene2, self)
        self.view2.setAlignment(Qt.AlignCenter)
        tab_container = QWidget()
        layout = QVBoxLayout(tab_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view2)
        self.center_tabs.addTab(tab_container, "Scene1")

        notebook = load_notebook('D:\\Dev\\GitHub\\ideas\\scripts\\获取邮箱账号注册过的所有网站\\获取邮箱账号注册过的所有网站.ipynb')

        if notebook.metadata.get("scene_data"):
            items_data = notebook.metadata.get("scene_data")
        else:
            items_data = {}

        graph_nodes_table = {}
        nodes = []
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                node_model = JupyterNodeModel(cell.source.split('\n')[0], cell.source)
                graph_nodes_table[node_model.title] = []
                nodes.append(node_model)
        graph_nodes = {}
        for index, node in enumerate(nodes):
            if index == len(nodes) - 1:
                break
            if node.title in graph_nodes.keys():
                rect1 = graph_nodes[nodes[index].title]
            else:
                rect1 = JupyterGraphNode(nodes[index].title)
                graph_nodes[rect1._title] = rect1
                rect1.setPos(index*0, 0)
            if nodes[index+1].title in graph_nodes.keys():
                rect2 = graph_nodes[nodes[index+1].title]
            else:
                rect2 = JupyterGraphNode(nodes[index+1].title)
                graph_nodes[rect2._title] = rect2
                rect2.setPos((index+1)*300, 0)
            self.scene2.addItem(rect1)
            self.scene2.addItem(rect2)
        for node in nodes:
            if node.title in items_data.keys():
                graph_nodes[node.title].setPos(items_data[node.title].x, items_data[node.title].y)
                if items_data[node.title].children != []:
                    for child in items_data[node.title].children:
                        connection = ConnectionItem(graph_nodes[node.title], graph_nodes[child.title])
                        self.scene2.addItem(connection)

    def save_tab(self):
        notebook = load_notebook('D:\\Dev\\GitHub\\ideas\\scripts\\获取邮箱账号注册过的所有网站\\获取邮箱账号注册过的所有网站.ipynb')
        # Extract data_model from the JupyterGraphNode in the scene
        items_data = {item._title:item.to_dict() for item in self.scene2.items() if isinstance(item, JupyterGraphNode)}
        notebook.metadata["scene_data"] = items_data
        save_notebook(notebook, 'D:\\Dev\\GitHub\\ideas\\scripts\\获取邮箱账号注册过的所有网站\\获取邮箱账号注册过的所有网站.ipynb')


    def setup_node_sketchpad(self):
        self.setWindowTitle("Jupyter Visual Runner")
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QtGui.QIcon("public/icon.png"))

        self.center_tabs = QTabWidget()
        tab_container = QWidget()
        layout = QVBoxLayout(tab_container)
        layout.setContentsMargins(0, 0, 0, 0)
        add_tab_button = QtWidgets.QPushButton("Add Tab")
        save_tab_button = QtWidgets.QPushButton("Save Tab")
        layout.addWidget(add_tab_button)
        layout.addWidget(save_tab_button)
        add_tab_button.clicked.connect(self.add_tab)
        save_tab_button.clicked.connect(self.save_tab)
        self.center_tabs.addTab(tab_container, "Homepage")
        self.setCentralWidget(self.center_tabs)


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