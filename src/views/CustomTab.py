from PySide6.QtWidgets import QWidget


class CustomTab(QWidget):
    def __init__(self, title, tab_id, notebook_dir, notebook_path, scene, view, parent=None):
        super().__init__(parent)
        self.title = title
        self.tab_id = tab_id
        self.notebook_dir = notebook_dir
        self.notebook_path = notebook_path
        self.scene = scene
        self.view = view
        self.selected_item = None