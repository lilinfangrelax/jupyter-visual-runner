import datetime
import sys
import uuid
from pathlib import Path

from PySide6 import QtGui, QtWidgets, QtCore
from PySide6.QtCore import QSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QDockWidget, QMainWindow, QListWidget, QTabWidget, QTextEdit, QFrame, QWidget, \
    QVBoxLayout, QApplication, QPushButton

from src.controllers.graph_execute_controller import GraphExecuteController
from src.models.JupyterNodeModel import JupyterNodeModel
from src.utils.ipynb_file_util import load_notebook, save_notebook
from src.views.CustomTab import CustomTab
from src.views.JupyterVisualRunnerEditor import *


class JupyterVisualRunner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Jupyter Visual Runner", "Jupyter Visual Runner")
        self.recent_files = self.settings.value("RecentFiles", [])
        if self.recent_files is None:
            self.recent_files = []
        self.setup_node_sketchpad()
        self.center()
        self.thread1 = None


    def closeEvent(self, event):
        # Save QDockWidget state
        self.settings.setValue('windowState', self.saveState())

    def add_tab_without_filepath(self):
        # 1. Open file chooser to get the .ipynb file path
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "Jupyter Notebook (*.ipynb)")
        if file_path == '':
            return
        self.recent_files.append(file_path)
        settings.setValue("RecentFiles", self.recent_files)
        self.add_tab(file_path)

    # MVP: 200 line to restructure the code
    def add_tab(self, file_path):
        """ Add a new tab"""
        # 2. Init tab
        tab_id = str(uuid.uuid1())
        notebook_dir = Path(file_path).parent.resolve()
        scene = NodeSketchpadScene()
        view = NodeSketchpadView(scene, self)
        view.setAlignment(Qt.AlignCenter)
        title = file_path.split('/')[-1]
        tab_container = CustomTab(title, tab_id, notebook_dir, file_path, scene, view)
        layout = QVBoxLayout(tab_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)
        self.center_tabs.addTab(tab_container, title)


        # 3. Load the .ipynb file
        notebook = load_notebook(file_path)
        if notebook.metadata.get("scene_data"):
            items_data = notebook.metadata.get("scene_data")
        else:
            items_data = {}
        graph_nodes_table = {}
        nodes = []
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                node_model = JupyterNodeModel(cell.source.split('\n')[0], cell.source)
                node_model.tab_id = tab_id
                graph_nodes_table[node_model.title] = []
                nodes.append(node_model)

        # 4. Draw the graph
        graph_nodes = {}
        for index, node in enumerate(nodes):
            if index == len(nodes) - 1:
                break
            if node.title in graph_nodes.keys():
                rect1 = graph_nodes[nodes[index].title]
            else:
                rect1 = JupyterGraphNode(nodes[index].title, nodes[index].code)
                graph_nodes[rect1._title] = rect1
                rect1.setPos(index*0, 0)
                rect1.signals.nodeClicked.connect(self.update_widget)

            if nodes[index+1].title in graph_nodes.keys():
                rect2 = graph_nodes[nodes[index+1].title]
            else:
                rect2 = JupyterGraphNode(nodes[index+1].title, nodes[index+1].code)
                graph_nodes[rect2._title] = rect2
                rect2.setPos((index+1)*300, 0)
                rect2.signals.nodeClicked.connect(self.update_widget)

            scene.addItem(rect1)
            scene.addItem(rect2)

        # 5. Draw the connections
        for node in nodes:
            if node.title in items_data.keys():
                graph_nodes[node.title].setPos(items_data[node.title].x, items_data[node.title].y)
                if items_data[node.title].children != []:
                    for child_title in items_data[node.title].children:
                        connection = ConnectionItem(graph_nodes[node.title], graph_nodes[child_title])
                        scene.addItem(connection)

        self.center_tabs.setCurrentWidget(tab_container)

    def save_tab(self):
        current_widget = self.center_tabs.currentWidget()
        if current_widget is None:
            return
        if isinstance(current_widget, CustomTab):
            notebook = load_notebook(current_widget.notebook_path)
            # Extract data_model from the JupyterGraphNode in the scene
            items_data = {item._title:item.to_dict() for item in current_widget.scene.items() if isinstance(item, JupyterGraphNode)}
            notebook.metadata["scene_data"] = items_data
            save_notebook(notebook, current_widget.notebook_path)

    def run_tab(self):
        current_widget = self.center_tabs.currentWidget()
        if current_widget is None:
            return
        if isinstance(current_widget, CustomTab):
            graph = {item.data_model.title:item.data_model.children for item in current_widget.scene.items() if isinstance(item, JupyterGraphNode)}
            nodes = {item.data_model.title:[item.data_model.code, item.data_model.uuid] for item in current_widget.scene.items() if isinstance(item, JupyterGraphNode)}

            # Clear the scene
            for item in current_widget.scene.items():
                if isinstance(item, JupyterGraphNode):
                    item.set_default_color()
            if self.thread1 is not None:
                self.thread1.quit()
                self.thread1.wait()

            self.thread1 = QtCore.QThread()
            self.worker = GraphExecuteController(graph, nodes, current_widget.notebook_dir, current_widget.tab_id)
            self.worker.moveToThread(self.thread1)
            self.worker.executor_process.connect(self.update_process)
            self.worker.executor_binding.connect(self.bind_item_msg_id)
            self.thread1.started.connect(self.worker.execute_all)
            self.thread1.start()

    def bind_item_msg_id(self, binding):
        msg_id = binding.split(":")[0]
        tab_id = binding.split(":")[1].split("#")[0]
        item_id = binding.split(":")[1].split("#")[1]
        self.logger_widget.append(binding)
        for index in range(self.center_tabs.count()):
            tab_widget = self.center_tabs.widget(index)
            if getattr(tab_widget, 'tab_id', None) == tab_id:
                    for item in tab_widget.scene.items():
                        if isinstance(item, JupyterGraphNode):
                            if item.data_model.uuid == item_id:
                                item.data_model.msg_id = msg_id

    def update_process(self, process):
        process_msg_id = process.split(":")[0].split("#")[0]
        tab_id = process.split(":")[0].split("#")[1]
        print(process)
        for index in range(self.center_tabs.count()):
            tab_widget = self.center_tabs.widget(index)
            if getattr(tab_widget, 'tab_id', None) == tab_id:
                    for item in tab_widget.scene.items():
                        if isinstance(item, JupyterGraphNode):
                            if item.data_model.msg_id == process_msg_id:
                                status_str = process.replace(f"{process_msg_id}#{tab_id}:", "")
                                print(status_str)
                                if status_str == "status:busy":
                                    color = QColor('yellow')
                                    item.set_color(color)
                                    item.data_model.last_status = "status:busy"
                                if status_str.startswith("execute_input"):
                                    color = QColor('yellow')
                                    item.set_color(color)
                                    item.data_model.last_status = "execute_input"
                                elif status_str == "status:idle" and item.data_model.last_status == "status:busy":
                                    return
                                elif status_str == "status:idle" and item.data_model.last_status != "error":
                                    color = QColor('green')
                                    item.set_color(color)
                                    item.data_model.last_status = "idle"
                                elif status_str.startswith("error"):
                                    color = QColor('red')
                                    item.set_color(color)
                                    item.data_model.last_status = "error"
                                    item.set_result_text(status_str.replace("error_:","").split("\n")[0])
                                    item.data_model.result = status_str.replace("error_:", "")
                                elif status_str.startswith("stream"):
                                    item.data_model.last_status = "stream"
                                    item.set_result_text(status_str.replace('stream:', "").split("\n")[0])
                                    item.data_model.result = status_str.replace("stream:", "")




                                print(f"{datetime.datetime.now()} {item.data_model.title}: {status_str}")
                    self.logger_widget.append(process)


    def setup_node_sketchpad(self):
        self.setWindowTitle("Jupyter Visual Runner")
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QtGui.QIcon("public/icon.png"))

        self.center_tabs = QTabWidget()
        homepage = QWidget()
        layout = QVBoxLayout(homepage)
        layout.setContentsMargins(0, 0, 0, 0)
        self.center_tabs.addTab(homepage, "Homepage")
        self.setCentralWidget(self.center_tabs)
        # Show all recent files and filepath in the homepage, and clickable
        if self.recent_files is not None:
            for file_path in self.recent_files:
                recent_file_button = QPushButton(file_path)
                layout.addWidget(recent_file_button)
                recent_file_button.clicked.connect(lambda _, path=file_path: self.add_tab(path))




        dock1 = QDockWidget("Browser", self)
        dock1_widget = QListWidget()
        dock1.setWidget(dock1_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock1)

        properties_dock = QDockWidget("Properties", self)
        properties_dock_widget = QListWidget()
        properties_dock.setWidget(properties_dock_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, properties_dock)

        # node raw code Dock
        raw_code_dock = QDockWidget("Raw", self)
        self.raw_code_widget = QTextEdit()
        self.raw_code_widget.setLineWrapMode(QTextEdit.NoWrap)
        self.raw_code_widget.setFont(NodeEditorConfig.node_title_font)
        raw_code_dock.setWidget(self.raw_code_widget)
        self.tabifyDockWidget(properties_dock, raw_code_dock)

        # result Dock
        result_dock = QDockWidget("Result", self)
        self.result_widget = QTextEdit()
        self.result_widget.setReadOnly(True)
        self.result_widget.setFont(NodeEditorConfig.node_title_font)
        self.result_widget.setLineWrapMode(QTextEdit.NoWrap)
        result_dock.setWidget(self.result_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, result_dock)


        dock3 = QDockWidget("Logger", self)
        self.logger_widget = QTextEdit()
        self.logger_widget.setReadOnly(True)
        self.logger_widget.setLineWrapMode(QTextEdit.NoWrap)
        self.logger_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # Solve problem: there is a blue line in the bottom of QTextEdit
        # https://stackoverflow.com/questions/16436058/how-to-make-qtextedit-with-no-visible-border
        self.logger_widget.setFrameStyle(QFrame.NoFrame)
        dock3.setWidget(self.logger_widget)
        dock3.setMinimumHeight(150)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock3)

        button_group = QDockWidget("Button Group", self)
        button_group_widget = QWidget()
        button_group.setWidget(button_group_widget)
        button_group_layout = QVBoxLayout(button_group_widget)
        button_group_layout.setContentsMargins(0, 0, 0, 0)
        add_tab_button = QtWidgets.QPushButton("Add Tab")
        save_tab_button = QtWidgets.QPushButton("Save Tab")
        run_button = QtWidgets.QPushButton("Run")
        button_group_layout.addWidget(add_tab_button)
        button_group_layout.addWidget(save_tab_button)
        button_group_layout.addWidget(run_button)
        add_tab_button.clicked.connect(self.add_tab_without_filepath)
        save_tab_button.clicked.connect(self.save_tab)
        run_button.clicked.connect(self.run_tab)
        self.addDockWidget(Qt.BottomDockWidgetArea, button_group)




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

    def update_widget(self, data_model_dict):
        self.raw_code_widget.setText(data_model_dict["code"])
        self.result_widget.setText(data_model_dict["result"])

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