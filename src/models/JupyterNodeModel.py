class JupyterNodeModel(object):
    def __init__(self, title, code, parent=None):
        self.title = title
        self.code = code
        super().__init__()

    def __str__(self):
        return self.title